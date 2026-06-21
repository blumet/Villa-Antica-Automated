"""
Villa Antica Barcelona — Commercial Brief & Configuration
This file is the GM's intent layer. Agents read this to understand
what the hotel is optimising for. Change it to change agent behaviour.
"""
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# ── LLM ───────────────────────────────────────────────────────────────────────
# Model used by all agents. Swap back to claude-sonnet-4-6 if Haiku underperforms
# on reasoning-heavy agents (revenue escalation logic, multi-step tool loops).
LLM_MODEL = "claude-haiku-4-5-20251001"

# ── Hotel identity ─────────────────────────────────────────────────────────────
HOTEL = {
    "name": "Villa Antica Barcelona",
    "rooms": 80,
    "location": "Barcelona, Spain",
    "category": "80-room independent boutique hotel",
    "currency": "EUR",
}

# ── GM Commercial Brief ────────────────────────────────────────────────────────
# This is what the orchestrator reads every day to set agent intent.
COMMERCIAL_BRIEF = {
    "adr_floor_eur": 150,           # No rate can go below this without human approval
    "target_occupancy_pct": 82,      # Occupancy goal
    "channel_priority": ["direct", "corporate", "booking.com", "expedia", "airbnb"],
    "rate_change_approval_threshold_pct": 15,  # Changes > 15% require human sign-off
    "vip_arrival_buffer_hours": 3,   # Clean room must be ready X hours before VIP arrival
    "shoulder_nights": ["sunday", "monday", "tuesday"],  # Nights that need rate push
    "current_promotions": ["early_bird_10pct", "direct_breakfast_included"],
    "notes": "Protect ADR above €150. Fill shoulder nights with rate nudges. Prioritise direct channel.",
}

# ── Escalation Thresholds ─────────────────────────────────────────────────────
ESCALATION = {
    "refund_threshold_eur": 50,      # Refund requests above this → human approval
    "rate_change_pct": 15,           # Rate moves > N% → human approval
    "safety_keywords": ["flood", "fire", "water leak", "electrical", "gas", "injury",
                        "blood", "smoke detector", "structural", "unsafe"],
    "vip_no_room_hours_before_checkin": 2,  # Trigger if VIP arrives and no clean room
    "sla_breach_hours": {            # Ticket types → max hours before escalation
        "urgent": 1,
        "high": 4,
        "medium": 24,
        "low": 72,
    },
}

# ── Competitor Hotels (for rate monitoring) ───────────────────────────────────
COMPETITORS = ["Hotel Bruma", "Casa Marina", "Palau Boutique"]
