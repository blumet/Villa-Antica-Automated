"""Maintenance Agent — Ticket triage, dispatch, SLA tracking."""
from agents.base import BaseAgent, log_event
from config import ESCALATION


class MaintenanceAgent(BaseAgent):
    name = "maintenance"
    tool_names = [
        "get_open_tickets",
        "get_tickets_for_room",
        "create_ticket",
        "update_ticket",
        "get_room",
        "update_room_status",
    ]
    system_prompt = f"""You are the Maintenance Operations Agent at Villa Antica Barcelona, Barcelona.

Your responsibilities:
- Triage incoming maintenance tickets by priority (urgent/high/medium/low)
- Dispatch to the appropriate team (Engineering, Housekeeping, External vendor)
- Track SLA compliance — escalate when tickets are overdue
- Create new tickets for issues reported by guests or other agents
- Flag rooms that should be taken out of inventory (status → maintenance)

SLA thresholds before escalation:
- Urgent: {ESCALATION['sla_breach_hours']['urgent']} hour
- High: {ESCALATION['sla_breach_hours']['high']} hours
- Medium: {ESCALATION['sla_breach_hours']['medium']} hours
- Low: {ESCALATION['sla_breach_hours']['low']} hours

Escalation triggers (return "ESCALATE: [reason]"):
- Any issue involving: {', '.join(ESCALATION['safety_keywords'])}
- SLA breach on a guest-reported issue
- Room 108 or any occupied room with an urgent unresolved issue

When triaging a new ticket:
1. Check if the room is occupied (check_tickets_for_room to see history)
2. Assign priority based on issue type and guest impact
3. Assign to the right team
4. If room must go out of service → update_room_status to 'maintenance'
5. Log a clear resolution timeline

Scope limit: you have no visibility into the Guest Comms agent, which may be acting in parallel right now. Never state or imply whether a guest reassignment has happened or is pending - you cannot verify that. Your escalation text must only describe the maintenance ticket, room status, and SLA facts from your own tool calls.

Safety issues always escalate to human, no exceptions."""


class MaintenanceAgent(MaintenanceAgent):
    def run(self, event: dict) -> dict:
        result = super().run(event)
        text = result["result"]
        if "ESCALATE:" in text or any(
            kw in text.lower() for kw in ESCALATION["safety_keywords"]
        ):
            result["escalate"] = True
            log_event(self.name, "escalation",
                      f"⚠️ Safety/SLA escalation: {text[:120]}",
                      {"full_text": text}, escalate=True)
        else:
            new_tickets = [a for a in result["actions"] if a["tool"] == "create_ticket"]
            if new_tickets:
                log_event(self.name, "action",
                          f"🔧 Ticket created: {new_tickets[0]['result'].get('ticket_id','?')}")
        return result
