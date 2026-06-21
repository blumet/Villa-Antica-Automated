"""
Scenario A — The Difficult Tuesday
Occupancy: 58%, pace 30% below prior year.
Revenue Agent detects soft nights, proposes rate cut below ADR floor.
Orchestrator fires escalation. GM must approve or override.
"""
from datetime import datetime, timedelta
from agents.base import log_event

TODAY = datetime.now()
SOFT_DATE = (TODAY + timedelta(days=4)).strftime("%Y-%m-%d")  # Thursday


def run(orchestrator) -> dict:
    log_event("SCENARIO", "action",
              "🎬 SCENARIO A: The Difficult Tuesday — starting", {})

    # Step 1: Revenue agent checks soft nights
    event = {
        "type": "soft_night_detected",
        "description": (
            f"Booking pace for {SOFT_DATE} is 30% below prior year. "
            f"Current occupancy forecast: 38%. "
            f"Competitor rates: Hotel Bruma €138, Casa Marina €142, Palau Boutique €135. "
            f"Our current standard rate: €168. "
            f"Evaluate whether a rate adjustment is appropriate given our ADR floor of €150. "
            f"If the optimal rate is below €150, escalate to GM with full context. "
            f"Include the specific proposed rate and commercial rationale."
        ),
        "date": SOFT_DATE,
        "current_rate_eur": 168,
        "occupancy_forecast_pct": 38,
        "pace_vs_prior_year_pct": -30,
    }

    result = orchestrator.dispatch(event)

    log_event("SCENARIO", "decision",
              "✅ Scenario A complete. Check escalation queue for GM decision.",
              {"escalations": len(result.get("escalations", []))})

    return result
