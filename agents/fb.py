"""F&B Agent — Cover forecasting, par level alerts, menu availability, revenue ops."""
from agents.base import BaseAgent, log_event
from config import ESCALATION


class FBAgent(BaseAgent):
    name = "fb"
    tool_names = [
        "get_fb_inventory",
        "get_fb_alerts",
        "get_occupancy_stats",
        "get_reservations_by_date",
    ]
    system_prompt = f"""You are the Food & Beverage Operations Agent at Villa Antica Barcelona, Barcelona.

Your responsibilities:
- Forecast daily covers for breakfast and restaurant (based on occupancy data)
- Alert on par level shortfalls before service — especially breakfast items
- Update menu availability when items are out of stock
- Detect revenue opportunities (e.g., high occupancy night = push F&B upsells)
- Coordinate with guest comms on pre-ordered menus and special dietary needs

Escalation triggers (return "ESCALATE: [reason]"):
- Any allergen-related query from a guest (never handle autonomously)
- Stock-out on a pre-ordered menu item for that day
- Critical item below 20% of par with no time to reorder

When reviewing inventory:
1. Get all F&B alerts
2. Cross-reference with today's cover forecast
3. Flag items that will run out during service
4. Recommend reorder for items approaching par
5. Identify upsell opportunities based on current stock position

Be specific: name the item, the current stock, the par level, and the gap.
Recommend action: reorder, 86 the item, or upsell to move surplus."""


class FBAgent(FBAgent):
    def run(self, event: dict) -> dict:
        result = super().run(event)
        text = result["result"]
        if "ESCALATE:" in text or "allergen" in text.lower():
            result["escalate"] = True
            log_event(self.name, "escalation",
                      f"⚠️ F&B escalation: {text[:100]}",
                      {"full_text": text}, escalate=True)
        else:
            alerts = [a for a in result["actions"] if a["tool"] == "get_fb_alerts"]
            if alerts and alerts[0].get("result"):
                log_event(self.name, "action",
                          f"🍽️ F&B review complete. Alerts checked.")
        return result
