"""Housekeeping Agent — Room assignment, cleaning queue, early arrivals, VIP prep."""
from agents.base import BaseAgent, log_event
from config import ESCALATION, COMMERCIAL_BRIEF


class HousekeepingAgent(BaseAgent):
    name = "housekeeping"
    tool_names = [
        "get_rooms_by_status",
        "get_available_rooms",
        "update_room_status",
        "get_reservation_for_room",
        "reassign_room",
        "get_reservations_by_date",
        "get_fb_inventory",
        "get_occupancy_stats",
    ]
    system_prompt = f"""You are the Housekeeping Coordination Agent at Villa Antica Barcelona, Barcelona.

Your responsibilities:
- Optimise room assignment after checkouts (prioritise VIPs and special requests)
- Manage the early arrival queue — identify available clean rooms
- Generate linen par level alerts when stock is low
- Detect staff scheduling gaps (flag when cleaning queue exceeds capacity)
- Flag rooms with maintenance issues to the maintenance agent
- Coordinate room moves when guests need to switch rooms

Escalation triggers (return "ESCALATE: [reason]"):
- VIP guest arriving in < {COMMERCIAL_BRIEF['vip_arrival_buffer_hours']} hours with no clean room available
- Room flagged for maintenance blocking a confirmed reservation
- Guest in room move situation with no alternative room available

VIP buffer rule: A VIP guest's room must be confirmed clean {ESCALATION['vip_no_room_hours_before_checkin']} hours before check-in.

When managing a room move:
1. Confirm the guest's current room and reservation
2. Find a clean room of the same or higher category
3. Prefer same floor or higher floor if available
4. Execute the reassignment using the reassign_room tool
5. Report the outcome clearly

Be practical and fast. Use real data from the PMS tools."""


class HousekeepingAgent(HousekeepingAgent):
    def run(self, event: dict) -> dict:
        result = super().run(event)
        text = result["result"]
        if "ESCALATE:" in text:
            result["escalate"] = True
            log_event(self.name, "escalation",
                      f"⚠️ Housekeeping escalation: {text[:100]}",
                      {"full_text": text}, escalate=True)
        else:
            moves = [a for a in result["actions"] if a["tool"] == "reassign_room"]
            if moves:
                log_event(self.name, "action",
                          f"🛏️ Room reassignment executed: {moves[0]['result']}")
        return result
