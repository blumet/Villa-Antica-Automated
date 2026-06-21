"""
Scenario B — The Angry Guest at 11pm
Guest WhatsApps: room smells like smoke, wants to move.
Guest Comms + Maintenance fire in PARALLEL.
- Guest Comms: finds clean room, drafts warm response
- Maintenance: logs smoke complaint ticket for room 108
Zero human involvement. 90-second resolution.
"""
from agents.base import log_event


def run(orchestrator) -> dict:
    log_event("SCENARIO", "action",
              "🎬 SCENARIO B: The Angry Guest at 11pm — starting", {})

    event = {
        "type": "complaint",
        "description": (
            "Guest in room 108 has sent a WhatsApp at 23:47: "
            "'Hi, my room smells strongly of smoke. I booked a non-smoking room. "
            "I have an early meeting tomorrow and I cannot sleep in here. "
            "I need to be moved to another room immediately.' "
            "\n\n"
            "Guest profile: G0045 — returning direct booker, 4 previous stays, Silver loyalty. "
            "Current time: 23:47. "
            "\n\n"
            "Guest Comms Agent: "
            "1. Check what clean rooms are available right now. "
            "2. Find a room of equal or superior category to room 108 (standard room). "
            "3. Execute the room reassignment. "
            "4. Draft a warm, brief WhatsApp response to the guest confirming the move, "
            "apologising sincerely, and offering a complimentary breakfast tomorrow. "
            "Do NOT offer a refund — that requires escalation. "
            "\n\n"
            "Maintenance Agent: "
            "1. Create a maintenance ticket for room 108 — issue: smoke/smell, priority: high. "
            "2. Flag room 108 for inspection before it's returned to inventory. "
            "3. Update room 108 status to maintenance. "
        ),
        "room_number": 108,
        "guest_id": "G0045",
        "reservation_lookup_room": 108,
        "time": "23:47",
        "channel": "whatsapp",
    }

    result = orchestrator.dispatch(event)

    escalation_count = len(result.get("escalations", []))
    if escalation_count == 0:
        summary = "✅ Scenario B complete. Guest moved. Ticket logged. Zero human involvement."
    else:
        summary = (f"✅ Scenario B complete. Guest moved. Ticket logged. "
                   f"{escalation_count} escalation(s) flagged for human review.")

    log_event("SCENARIO", "decision", summary,
              {"agents": result.get("agents_used", []),
               "escalations": escalation_count})

    return result
