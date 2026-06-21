"""
Orchestrator — Villa Antica Barcelona GM Intent Layer
Routes incoming events to the right specialist agents.
Monitors for escalations. Compiles the morning briefing.
"""
import json
import threading
from datetime import datetime
from typing import Any

from agents.base import log_event, BaseAgent
from config import COMMERCIAL_BRIEF, HOTEL


# Escalation queue — UI polls this
escalation_queue: list[dict] = []


class Orchestrator:
    """
    The GM's brain. Reads the commercial brief, routes events,
    fires agents (in parallel when appropriate), handles escalations.
    """

    def __init__(self):
        # Import agents lazily to avoid circular imports
        from agents.guest_comms import GuestCommsAgent
        from agents.revenue import RevenueAgent
        from agents.housekeeping import HousekeepingAgent
        from agents.maintenance import MaintenanceAgent
        from agents.fb import FBAgent

        self.agents = {
            "guest_comms":  GuestCommsAgent(),
            "revenue":      RevenueAgent(),
            "housekeeping": HousekeepingAgent(),
            "maintenance":  MaintenanceAgent(),
            "fb":           FBAgent(),
        }
        self.brief = COMMERCIAL_BRIEF

    # ── Routing ───────────────────────────────────────────────────────────────

    def _route(self, event: dict) -> list[str]:
        """
        Determine which agents should handle this event.
        Returns list of agent names. Multiple = parallel execution.
        """
        etype = event.get("type", "")
        routes = {
            "guest_message":      ["guest_comms"],
            "complaint":          ["guest_comms", "maintenance"],  # parallel
            "move_request":       ["guest_comms", "housekeeping"],
            "rate_check":         ["revenue"],
            "soft_night_detected":["revenue"],
            "room_checkout":      ["housekeeping"],
            "maintenance_request":["maintenance"],
            "fb_check":           ["fb"],
            "morning_briefing":   ["guest_comms", "revenue", "housekeeping", "maintenance", "fb"],
            "vip_arrival":        ["housekeeping", "guest_comms"],
        }
        return routes.get(etype, ["guest_comms"])  # default

    # ── Escalation handling ───────────────────────────────────────────────────

    def _handle_escalation(self, agent_name: str, result: dict, event: dict) -> dict:
        entry = {
            "id": len(escalation_queue) + 1,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "agent": agent_name,
            "event_type": event.get("type"),
            "message": result.get("result", "")[:200],
            "actions": result.get("actions", []),
            "status": "pending",   # pending | approved | overridden
        }
        escalation_queue.append(entry)
        log_event("ORCHESTRATOR", "escalation",
                  f"⚠️ Escalation from {agent_name}: {entry['message'][:80]}...",
                  entry, escalate=True)
        return entry

    # ── Main dispatch ─────────────────────────────────────────────────────────

    def dispatch(self, event: dict) -> dict:
        """
        Receive an event, route it, run agents, handle escalations.
        Returns aggregated result.
        """
        log_event("ORCHESTRATOR", "action",
                  f"📋 Event received: {event.get('type')} — routing...", event)

        agent_names = self._route(event)
        results = {}

        if len(agent_names) == 1:
            # Sequential
            name = agent_names[0]
            agent = self.agents[name]
            result = agent.run(event)
            results[name] = result
        else:
            # Parallel — fire all agents simultaneously
            log_event("ORCHESTRATOR", "action",
                      f"🔀 Parallel dispatch to: {', '.join(agent_names)}")
            threads = {}
            thread_results = {}

            def run_agent(name, ag, ev):
                thread_results[name] = ag.run(ev)

            for name in agent_names:
                t = threading.Thread(target=run_agent,
                                     args=(name, self.agents[name], event))
                threads[name] = t
                t.start()

            for name, t in threads.items():
                t.join(timeout=60)

            results = thread_results

        # Check escalations
        escalations = []
        for name, result in results.items():
            if result.get("escalate"):
                esc = self._handle_escalation(name, result, event)
                escalations.append(esc)

        log_event("ORCHESTRATOR", "decision",
                  f"✅ Event handled by: {', '.join(results.keys())}. "
                  f"Escalations: {len(escalations)}")

        return {
            "event": event,
            "agents_used": list(results.keys()),
            "results": results,
            "escalations": escalations,
        }

    # ── Morning Briefing ──────────────────────────────────────────────────────

    def morning_briefing(self) -> dict:
        """
        Compile a 6-line GM summary by running all agents in parallel
        on a briefing request.
        """
        log_event("ORCHESTRATOR", "action", "☀️ Generating morning briefing...")

        event = {
            "type": "morning_briefing",
            "description": (
                "Generate a concise operational update for the GM. "
                "Cover: current occupancy, any rate issues or soft nights, "
                "housekeeping status, open maintenance tickets, F&B alerts. "
                "Be specific. Use numbers. Maximum 2 sentences per topic."
            ),
        }

        briefing_parts = {}
        threads = {}
        thread_results = {}

        def run_agent(name, ag, ev):
            thread_results[name] = ag.run(ev)

        for name, agent in self.agents.items():
            t = threading.Thread(target=run_agent, args=(name, agent, event))
            threads[name] = t
            t.start()

        for name, t in threads.items():
            t.join(timeout=60)

        # Compile into one briefing
        sections = []
        for name, result in thread_results.items():
            if result.get("result"):
                sections.append(f"**{name.upper().replace('_',' ')}**: {result['result']}")

        briefing_text = "\n\n".join(sections)
        log_event("ORCHESTRATOR", "decision", f"📰 Morning briefing ready:\n{briefing_text}")

        return {
            "type": "morning_briefing",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "briefing": briefing_text,
            "sections": thread_results,
        }
