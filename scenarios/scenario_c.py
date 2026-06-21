"""
Scenario C — The Morning Briefing
Every day at 07:00, all 5 agents run in parallel.
Orchestrator synthesises into a 6-section GM summary.
"""
from agents.base import log_event


def run(orchestrator) -> dict:
    log_event("SCENARIO", "action",
              "🎬 SCENARIO C: Morning Briefing — 07:00", {})

    result = orchestrator.morning_briefing()

    log_event("SCENARIO", "decision",
              "☀️ Morning briefing delivered to GM dashboard.", {})

    return result
