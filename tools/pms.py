"""
PMS Data Access Layer — Villa Antica Barcelona
All CSV reads/writes go through here. This is the deterministic layer.
Agents call these functions as tools; they never touch CSVs directly.
"""
from __future__ import annotations
import csv
import json
from datetime import datetime, date
from pathlib import Path
from typing import Any

from config import DATA_DIR

TODAY = date.today()


# ── Internal helpers ───────────────────────────────────────────────────────────

def _read(filename: str) -> list[dict]:
    path = DATA_DIR / filename
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write(filename: str, rows: list[dict]) -> None:
    if not rows:
        return
    path = DATA_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def _update_row(filename: str, key_field: str, key_value: str, updates: dict) -> bool:
    rows = _read(filename)
    found = False
    for row in rows:
        if row[key_field] == str(key_value):
            row.update(updates)
            found = True
    if found:
        _write(filename, rows)
    return found


# ── ROOM TOOLS ────────────────────────────────────────────────────────────────

def get_room(room_number: int) -> dict | None:
    rows = _read("rooms.csv")
    for r in rows:
        if r["room_number"] == str(room_number):
            return r
    return None


def get_rooms_by_status(status: str) -> list[dict]:
    """Return all rooms with a given status: clean | dirty | occupied | maintenance"""
    return [r for r in _read("rooms.csv") if r["status"] == status]


def update_room_status(room_number: int, new_status: str) -> dict:
    ok = _update_row("rooms.csv", "room_number", str(room_number), {"status": new_status})
    return {"success": ok, "room_number": room_number, "new_status": new_status}


def get_available_rooms(room_type: str | None = None) -> list[dict]:
    rooms = get_rooms_by_status("clean")
    if room_type:
        rooms = [r for r in rooms if r["room_type"] == room_type]
    return rooms


# ── GUEST TOOLS ───────────────────────────────────────────────────────────────

def get_guest(guest_id: str) -> dict | None:
    rows = _read("guests.csv")
    for r in rows:
        if r["guest_id"] == guest_id:
            return r
    return None


def get_guest_by_name(first_name: str, last_name: str) -> dict | None:
    rows = _read("guests.csv")
    for r in rows:
        if r["first_name"].lower() == first_name.lower() and \
           r["last_name"].lower() == last_name.lower():
            return r
    return None


# ── RESERVATION TOOLS ─────────────────────────────────────────────────────────

def get_reservations_by_date(target_date: str | None = None) -> list[dict]:
    """Get reservations checking in/out on target_date (default: today)."""
    d = target_date or TODAY.strftime("%Y-%m-%d")
    rows = _read("reservations.csv")
    return [r for r in rows if r["check_in"] == d or r["check_out"] == d]


def get_active_reservations() -> list[dict]:
    """All checked-in reservations."""
    return [r for r in _read("reservations.csv") if r["status"] == "checked_in"]


def get_reservation_for_room(room_number: int) -> dict | None:
    rows = _read("reservations.csv")
    for r in rows:
        if r["room_number"] == str(room_number) and r["status"] == "checked_in":
            return r
    return None


def get_occupancy_stats() -> dict:
    rooms = _read("rooms.csv")
    reservations = get_active_reservations()
    total = len(rooms)
    occupied = len([r for r in rooms if r["status"] == "occupied"])
    clean = len([r for r in rooms if r["status"] == "clean"])
    dirty = len([r for r in rooms if r["status"] == "dirty"])
    maint = len([r for r in rooms if r["status"] == "maintenance"])
    return {
        "total_rooms": total,
        "occupied": occupied,
        "clean_available": clean,
        "dirty": dirty,
        "maintenance": maint,
        "occupancy_pct": round(occupied / total * 100, 1),
        "active_reservations": len(reservations),
    }


def reassign_room(reservation_id: str, new_room_number: int) -> dict:
    """Move a guest to a different room."""
    ok = _update_row("reservations.csv", "reservation_id", reservation_id,
                     {"room_number": str(new_room_number)})
    if ok:
        update_room_status(new_room_number, "occupied")
    return {"success": ok, "reservation_id": reservation_id, "new_room": new_room_number}


# ── RATE TOOLS ────────────────────────────────────────────────────────────────

def get_rates(target_date: str | None = None, room_type: str | None = None) -> list[dict]:
    d = target_date or TODAY.strftime("%Y-%m-%d")
    rows = _read("rates.csv")
    result = [r for r in rows if r["date"] == d]
    if room_type:
        result = [r for r in result if r["room_type"] == room_type]
    return result


def get_rate_range(start_date: str, end_date: str) -> list[dict]:
    rows = _read("rates.csv")
    return [r for r in rows if start_date <= r["date"] <= end_date]


def update_rate(target_date: str, room_type: str, new_rate: float) -> dict:
    rows = _read("rates.csv")
    updated = False
    for row in rows:
        if row["date"] == target_date and row["room_type"] == room_type:
            row["our_rate"] = str(round(new_rate, 2))
            updated = True
    if updated:
        _write("rates.csv", rows)
    return {"success": updated, "date": target_date, "room_type": room_type, "new_rate": new_rate}


def get_soft_nights(days_ahead: int = 14, threshold_pct: float = 55.0) -> list[dict]:
    """Return upcoming nights where forecast occupancy is below threshold."""
    rows = _read("rates.csv")
    today_str = TODAY.strftime("%Y-%m-%d")
    soft = []
    for r in rows:
        if r["date"] > today_str:
            try:
                if float(r["occupancy_forecast_pct"]) < threshold_pct:
                    soft.append(r)
            except (ValueError, KeyError):
                pass
    return soft[:days_ahead]


# ── MAINTENANCE TOOLS ─────────────────────────────────────────────────────────

def get_open_tickets() -> list[dict]:
    return [t for t in _read("maintenance_tickets.csv") if t["status"] in ("open", "pending", "in_progress")]


def get_tickets_for_room(room_number: int) -> list[dict]:
    return [t for t in _read("maintenance_tickets.csv") if t["room_number"] == str(room_number)]


def create_ticket(room_number: int, issue_type: str, description: str, priority: str) -> dict:
    tickets = _read("maintenance_tickets.csv")
    new_id = f"TKT{len(tickets)+1:04d}"
    ticket = {
        "ticket_id": new_id,
        "room_number": str(room_number),
        "reported_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "issue_type": issue_type,
        "description": description,
        "priority": priority,
        "status": "open",
        "assigned_to": "",
        "resolved_at": "",
        "notes": "",
    }
    tickets.append(ticket)
    _write("maintenance_tickets.csv", tickets)
    return ticket


def update_ticket(ticket_id: str, updates: dict) -> dict:
    ok = _update_row("maintenance_tickets.csv", "ticket_id", ticket_id, updates)
    return {"success": ok, "ticket_id": ticket_id, "updates": updates}


# ── F&B TOOLS ─────────────────────────────────────────────────────────────────

def get_fb_inventory() -> list[dict]:
    return _read("fb_inventory.csv")


def get_fb_alerts() -> list[dict]:
    return [i for i in _read("fb_inventory.csv") if i["alert"] in ("WARN", "YES")]


def get_fb_item(item_name: str) -> dict | None:
    for item in _read("fb_inventory.csv"):
        if item_name.lower() in item["item_name"].lower():
            return item
    return None


# ── TOOL REGISTRY ─────────────────────────────────────────────────────────────
# Anthropic tool definitions — agents pick from this list.

ALL_TOOLS = {
    "get_room": {
        "fn": get_room,
        "schema": {
            "name": "get_room",
            "description": "Get details for a specific room by room number.",
            "input_schema": {
                "type": "object",
                "properties": {"room_number": {"type": "integer", "description": "Room number"}},
                "required": ["room_number"],
            },
        },
    },
    "get_rooms_by_status": {
        "fn": get_rooms_by_status,
        "schema": {
            "name": "get_rooms_by_status",
            "description": "Get all rooms with a given status (clean, dirty, occupied, maintenance).",
            "input_schema": {
                "type": "object",
                "properties": {"status": {"type": "string", "enum": ["clean","dirty","occupied","maintenance"]}},
                "required": ["status"],
            },
        },
    },
    "get_available_rooms": {
        "fn": get_available_rooms,
        "schema": {
            "name": "get_available_rooms",
            "description": "Get clean rooms available for assignment, optionally filtered by type.",
            "input_schema": {
                "type": "object",
                "properties": {"room_type": {"type": "string", "description": "optional: standard|superior|deluxe|suite"}},
            },
        },
    },
    "update_room_status": {
        "fn": update_room_status,
        "schema": {
            "name": "update_room_status",
            "description": "Update the status of a room.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "room_number": {"type": "integer"},
                    "new_status": {"type": "string", "enum": ["clean","dirty","occupied","maintenance"]},
                },
                "required": ["room_number", "new_status"],
            },
        },
    },
    "get_reservation_for_room": {
        "fn": get_reservation_for_room,
        "schema": {
            "name": "get_reservation_for_room",
            "description": "Get the active reservation for a given room number.",
            "input_schema": {
                "type": "object",
                "properties": {"room_number": {"type": "integer"}},
                "required": ["room_number"],
            },
        },
    },
    "get_occupancy_stats": {
        "fn": get_occupancy_stats,
        "schema": {
            "name": "get_occupancy_stats",
            "description": "Get current hotel occupancy statistics.",
            "input_schema": {"type": "object", "properties": {}},
        },
    },
    "reassign_room": {
        "fn": reassign_room,
        "schema": {
            "name": "reassign_room",
            "description": "Move a guest reservation to a different room.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "reservation_id": {"type": "string"},
                    "new_room_number": {"type": "integer"},
                },
                "required": ["reservation_id", "new_room_number"],
            },
        },
    },
    "get_soft_nights": {
        "fn": get_soft_nights,
        "schema": {
            "name": "get_soft_nights",
            "description": "Find upcoming nights where occupancy forecast is below a threshold.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "days_ahead": {"type": "integer", "description": "How many days to look ahead"},
                    "threshold_pct": {"type": "number", "description": "Occupancy % below which night is 'soft'"},
                },
            },
        },
    },
    "get_rates": {
        "fn": get_rates,
        "schema": {
            "name": "get_rates",
            "description": "Get our rates and competitor rates for a date and optionally a room type.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "target_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "room_type": {"type": "string"},
                },
            },
        },
    },
    "update_rate": {
        "fn": update_rate,
        "schema": {
            "name": "update_rate",
            "description": "Update our rate for a specific date and room type.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "target_date": {"type": "string"},
                    "room_type": {"type": "string"},
                    "new_rate": {"type": "number"},
                },
                "required": ["target_date", "room_type", "new_rate"],
            },
        },
    },
    "get_open_tickets": {
        "fn": get_open_tickets,
        "schema": {
            "name": "get_open_tickets",
            "description": "Get all open/in-progress maintenance tickets.",
            "input_schema": {"type": "object", "properties": {}},
        },
    },
    "get_tickets_for_room": {
        "fn": get_tickets_for_room,
        "schema": {
            "name": "get_tickets_for_room",
            "description": "Get all maintenance tickets for a specific room.",
            "input_schema": {
                "type": "object",
                "properties": {"room_number": {"type": "integer"}},
                "required": ["room_number"],
            },
        },
    },
    "create_ticket": {
        "fn": create_ticket,
        "schema": {
            "name": "create_ticket",
            "description": "Create a new maintenance ticket.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "room_number": {"type": "integer"},
                    "issue_type": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low","medium","high","urgent"]},
                },
                "required": ["room_number", "issue_type", "description", "priority"],
            },
        },
    },
    "update_ticket": {
        "fn": update_ticket,
        "schema": {
            "name": "update_ticket",
            "description": "Update a maintenance ticket (status, assigned_to, notes, etc).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "updates": {"type": "object", "description": "Dict of fields to update"},
                },
                "required": ["ticket_id", "updates"],
            },
        },
    },
    "get_fb_inventory": {
        "fn": get_fb_inventory,
        "schema": {
            "name": "get_fb_inventory",
            "description": "Get full F&B inventory with stock levels and alerts.",
            "input_schema": {"type": "object", "properties": {}},
        },
    },
    "get_fb_alerts": {
        "fn": get_fb_alerts,
        "schema": {
            "name": "get_fb_alerts",
            "description": "Get F&B items that are below par level (WARN or YES alert).",
            "input_schema": {"type": "object", "properties": {}},
        },
    },
    "get_reservations_by_date": {
        "fn": get_reservations_by_date,
        "schema": {
            "name": "get_reservations_by_date",
            "description": "Get reservations checking in or out on a specific date.",
            "input_schema": {
                "type": "object",
                "properties": {"target_date": {"type": "string", "description": "YYYY-MM-DD, default today"}},
            },
        },
    },
    "get_guest": {
        "fn": get_guest,
        "schema": {
            "name": "get_guest",
            "description": "Get guest profile by guest_id.",
            "input_schema": {
                "type": "object",
                "properties": {"guest_id": {"type": "string"}},
                "required": ["guest_id"],
            },
        },
    },
}
