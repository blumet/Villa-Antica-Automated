"""Revenue Agent — Rate monitoring, parity, soft nights, price nudges."""
from agents.base import BaseAgent, log_event
from config import ESCALATION, COMMERCIAL_BRIEF


class RevenueAgent(BaseAgent):
    name = "revenue"
    tool_names = [
        "get_rates",
        "get_soft_nights",
        "get_occupancy_stats",
        "update_rate",
        "get_reservations_by_date",
    ]
    system_prompt = f"""You are the Revenue Management Agent at Villa Antica Barcelona, Barcelona.

Your responsibilities:
- Monitor rates daily against 3 competitor hotels (Hotel Bruma, Casa Marina, Palau Boutique)
- Detect soft nights (low occupancy forecast) and recommend rate adjustments
- Check channel parity — our rate on OTAs should not exceed our direct rate
- Execute approved rate changes (use update_rate tool)
- Identify upsell windows (e.g., high-demand nights where we're priced below competitors)

Hard rules:
- NEVER drop rate below €{COMMERCIAL_BRIEF['adr_floor_eur']} without escalation
- Any rate change > {ESCALATION['rate_change_pct']}% requires human sign-off: return "ESCALATE: [reason] Proposed rate: €[X]"
- Corporate contracted rates cannot be changed autonomously

Current strategy:
- {COMMERCIAL_BRIEF['notes']}
- Shoulder nights: {', '.join(COMMERCIAL_BRIEF['shoulder_nights'])} — push rate nudges on these

When you identify a soft night:
1. Check current rate
2. Compare against competitors
3. Recommend a nudge (typically -5% to -12% to stimulate demand)
4. If within 15% of current rate → execute it
5. If larger → escalate with full context

Always explain your reasoning briefly. Include the math."""


class RevenueAgent(RevenueAgent):
    def run(self, event: dict) -> dict:
        result = super().run(event)
        text = result["result"]
        if "ESCALATE:" in text:
            result["escalate"] = True
            log_event(self.name, "escalation",
                      f"⚠️ Rate escalation: {text[:120]}",
                      {"full_text": text}, escalate=True)
        elif result["actions"]:
            rate_changes = [a for a in result["actions"] if a["tool"] == "update_rate"]
            for change in rate_changes:
                log_event(self.name, "decision",
                          f"💰 Rate updated: {change['input']}")
        return result
