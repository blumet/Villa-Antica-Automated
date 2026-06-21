"""Generate realistic mock CSV data for Villa Antica Barcelona — 80-room independent hotel."""
import csv
import random
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta

TODAY = datetime(2026, 6, 14)
random.seed(42)

# ── ROOMS ──────────────────────────────────────────────────────────────────────
ROOM_TYPES = {
    "standard": {"floors": [1, 2], "rate_base": 120, "count": 32},
    "superior": {"floors": [3, 4], "rate_base": 155, "count": 24},
    "deluxe":   {"floors": [5, 6], "rate_base": 195, "count": 16},
    "suite":    {"floors": [7],    "rate_base": 280, "count":  8},
}
VIEWS = ["garden", "street", "courtyard", "sea"]
FEATURES = ["balcony", "bathtub", "king bed", "twin beds", "sofa", "kitchenette"]

rooms = []
room_num = 101
for rtype, cfg in ROOM_TYPES.items():
    for floor in cfg["floors"]:
        per_floor = cfg["count"] // len(cfg["floors"])
        for i in range(per_floor):
            rooms.append({
                "room_number": room_num,
                "room_type": rtype,
                "floor": floor,
                "status": random.choices(
                    ["occupied", "clean", "dirty", "maintenance"],
                    weights=[50, 25, 20, 5]
                )[0],
                "max_occupancy": 2 if rtype != "suite" else 4,
                "view": random.choice(VIEWS),
                "features": "; ".join(random.sample(FEATURES, k=random.randint(1, 3))),
                "rate_base_eur": cfg["rate_base"],
            })
            room_num += 1

with open("data/rooms.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rooms[0].keys())
    writer.writeheader()
    writer.writerows(rooms)

print(f"rooms.csv: {len(rooms)} rooms")

# ── GUESTS ────────────────────────────────────────────────────────────────────
FIRST_NAMES = ["Anna","Marco","Sophie","James","Elena","Thomas","Lucia","David",
               "Maria","Robert","Clara","Michael","Sara","John","Laura","Ahmed",
               "Nina","Patrick","Isabelle","Carlos","Yuki","Fatima","Pierre","Emma"]
LAST_NAMES  = ["Müller","Rossi","Dubois","Smith","García","Becker","Ferrari",
               "Johnson","López","Weber","Tanaka","Ahmed","Bernard","Williams",
               "Schneider","Martin","Gomez","Taylor","Nguyen","Hoffmann"]
LOYALTY     = ["none","none","none","silver","silver","gold","vip"]
PREFS       = ["extra pillows","late checkout","high floor","quiet room",
               "twin beds","sea view","early check-in","king bed","hypoallergenic bedding"]

guests = []
for i in range(1, 201):
    tier = random.choice(LOYALTY)
    visits = {"none": random.randint(1,2), "silver": random.randint(3,6),
              "gold": random.randint(7,15), "vip": random.randint(16,40)}[tier]
    guests.append({
        "guest_id": f"G{i:04d}",
        "first_name": random.choice(FIRST_NAMES),
        "last_name":  random.choice(LAST_NAMES),
        "email":      f"guest{i}@example.com",
        "phone":      f"+49 {random.randint(100,999)} {random.randint(1000000,9999999)}",
        "loyalty_tier": tier,
        "visit_count": visits,
        "last_stay":  (TODAY - timedelta(days=random.randint(30,730))).strftime("%Y-%m-%d"),
        "preferences": "; ".join(random.sample(PREFS, k=random.randint(0,2))),
        "notes":      random.choice(["", "", "", "allergic to feathers", "anniversary stay",
                                     "business traveler", "celebrating birthday", "prefers minimal contact"]),
    })

with open("data/guests.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=guests[0].keys())
    writer.writeheader()
    writer.writerows(guests)

print(f"guests.csv: {len(guests)} guests")

# ── RESERVATIONS ──────────────────────────────────────────────────────────────
CHANNELS   = ["direct", "booking.com", "expedia", "airbnb", "corporate"]
CHAN_RATES  = {"direct":0,"booking.com":0.15,"expedia":0.17,"airbnb":0.16,"corporate":0.10}
STATUS_OPT = ["confirmed","checked_in","checked_out","cancelled"]

occupied_rooms = [r["room_number"] for r in rooms if r["status"] == "occupied"]
all_rooms = [r["room_number"] for r in rooms]

reservations = []
res_id = 1
for room_num in all_rooms:
    room = next(r for r in rooms if r["room_number"] == room_num)
    if room["status"] == "occupied":
        guest = random.choice(guests)
        channel = random.choice(CHANNELS)
        nights  = random.randint(1, 5)
        ci = TODAY - timedelta(days=random.randint(0, 2))
        rate = room["rate_base_eur"] * random.uniform(0.85, 1.25)
        reservations.append({
            "reservation_id": f"RES{res_id:05d}",
            "guest_id": guest["guest_id"],
            "room_number": room_num,
            "check_in":  ci.strftime("%Y-%m-%d"),
            "check_out": (ci + timedelta(days=nights)).strftime("%Y-%m-%d"),
            "channel":   channel,
            "rate_eur":  round(rate, 2),
            "commission_pct": CHAN_RATES[channel],
            "status": "checked_in",
            "booked_at": (ci - timedelta(days=random.randint(3,60))).strftime("%Y-%m-%d"),
            "special_requests": guest["preferences"],
            "adults": random.randint(1,2),
            "children": random.randint(0,1),
        })
        res_id += 1
    num_future = random.randint(0, 3)
    for _ in range(num_future):
        guest  = random.choice(guests)
        channel = random.choice(CHANNELS)
        nights  = random.randint(1, 7)
        ci = TODAY + timedelta(days=random.randint(1, 30))
        rate = room["rate_base_eur"] * random.uniform(0.80, 1.40)
        reservations.append({
            "reservation_id": f"RES{res_id:05d}",
            "guest_id": guest["guest_id"],
            "room_number": room_num,
            "check_in":  ci.strftime("%Y-%m-%d"),
            "check_out": (ci + timedelta(days=nights)).strftime("%Y-%m-%d"),
            "channel":   channel,
            "rate_eur":  round(rate, 2),
            "commission_pct": CHAN_RATES[channel],
            "status": "confirmed",
            "booked_at": (TODAY - timedelta(days=random.randint(1,45))).strftime("%Y-%m-%d"),
            "special_requests": guest["preferences"],
            "adults": random.randint(1,2),
            "children": random.randint(0,1),
        })
        res_id += 1

with open("data/reservations.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=reservations[0].keys())
    writer.writeheader()
    writer.writerows(reservations)

print(f"reservations.csv: {len(reservations)} reservations")

# ── SCENARIO CONSISTENCY OVERRIDE ──────────────────────────────────────────────
# Scenario B's script hardcodes "guest G0045, checked into room 108." Random
# generation above has no idea that contract exists, so the two can drift apart
# (which is exactly what happened during testing). Force it true here, every
# time data is generated, regardless of what randomness assigned to room 108.
def _enforce_scenario_b_contract():
    rows = list(csv.DictReader(open("data/reservations.csv")))
    target = next((r for r in rows if r["room_number"] == "108" and r["status"] == "checked_in"), None)
    if target:
        target["guest_id"] = "G0045"
    else:
        rows.append({
            "reservation_id": f"RES{len(rows) + 1:05d}",
            "guest_id": "G0045",
            "room_number": "108",
            "check_in": (TODAY - timedelta(days=1)).strftime("%Y-%m-%d"),
            "check_out": (TODAY + timedelta(days=2)).strftime("%Y-%m-%d"),
            "channel": "direct",
            "rate_eur": "120.0",
            "commission_pct": "0",
            "status": "checked_in",
            "booked_at": (TODAY - timedelta(days=20)).strftime("%Y-%m-%d"),
            "special_requests": "non-smoking",
            "adults": "1",
            "children": "0",
        })
    with open("data/reservations.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

_enforce_scenario_b_contract()
print("Scenario B contract enforced: G0045 is checked into room 108.")

# ── RATES ─────────────────────────────────────────────────────────────────────
rates = []
for d in range(-7, 30):
    date = TODAY + timedelta(days=d)
    for rtype, cfg in ROOM_TYPES.items():
        base = cfg["rate_base"]
        weekend = 1.12 if date.weekday() >= 4 else 1.0
        our_rate = round(base * weekend * random.uniform(0.90, 1.10), 2)
        rates.append({
            "date": date.strftime("%Y-%m-%d"),
            "room_type": rtype,
            "our_rate": our_rate,
            "competitor_a_rate": round(our_rate * random.uniform(0.88, 1.15), 2),
            "competitor_b_rate": round(our_rate * random.uniform(0.92, 1.20), 2),
            "competitor_c_rate": round(our_rate * random.uniform(0.85, 1.12), 2),
            "occupancy_forecast_pct": round(random.uniform(45, 95), 1),
            "booked_rooms": random.randint(30, 72),
        })

with open("data/rates.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rates[0].keys())
    writer.writeheader()
    writer.writerows(rates)

soft_dates = [(TODAY + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(3,6)]
rates_patched = []
with open("data/rates.csv") as f:
    for row in csv.DictReader(f):
        if row["date"] in soft_dates:
            row["booked_rooms"] = str(random.randint(20, 32))
            row["occupancy_forecast_pct"] = str(round(random.uniform(28, 42), 1))
        rates_patched.append(row)

with open("data/rates.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rates_patched[0].keys())
    writer.writeheader()
    writer.writerows(rates_patched)

print(f"rates.csv: {len(rates)} rate rows")

# ── MAINTENANCE TICKETS ───────────────────────────────────────────────────────
ISSUE_TYPES = ["plumbing","electrical","HVAC","elevator","furniture","cleanliness",
               "TV/AV","minibar","safe","door lock","smoke detector","pest","water leak"]
PRIORITIES  = ["low","medium","high","urgent"]

tickets = []
for i in range(1, 35):
    room = random.choice(rooms)
    created = TODAY - timedelta(days=random.randint(0,14), hours=random.randint(0,23))
    issue   = random.choice(ISSUE_TYPES)
    priority = ("urgent" if issue in ["water leak","electrical","smoke detector","elevator"]
                else random.choices(PRIORITIES, weights=[30,45,20,5])[0])
    resolved = random.random() < 0.6
    tickets.append({
        "ticket_id": f"TKT{i:04d}",
        "room_number": room["room_number"],
        "reported_at": created.strftime("%Y-%m-%d %H:%M"),
        "issue_type": issue,
        "description": f"{issue.capitalize()} issue reported in room {room['room_number']}",
        "priority": priority,
        "status": "resolved" if resolved else random.choice(["open","in_progress"]),
        "assigned_to": random.choice(["Engineering","Housekeeping","External vendor","",""]),
        "resolved_at": (created + timedelta(hours=random.randint(1,48))).strftime("%Y-%m-%d %H:%M") if resolved else "",
        "notes": "",
    })

tickets.append({
    "ticket_id": "TKT0035",
    "room_number": 108,
    "reported_at": "",
    "issue_type": "smoke/smell",
    "description": "Guest reported strong smoke smell — room 108",
    "priority": "high",
    "status": "pending",
    "assigned_to": "",
    "resolved_at": "",
    "notes": "Scenario B trigger",
})

with open("data/maintenance_tickets.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=tickets[0].keys())
    writer.writeheader()
    writer.writerows(tickets)

print(f"maintenance_tickets.csv: {len(tickets)} tickets")

# ── F&B INVENTORY ─────────────────────────────────────────────────────────────
fb_items = [
    ("Breakfast covers forecast", "operations", 65, 58, "covers"),
    ("Coffee beans (kg)", "beverage", 5, 3.2, "kg"),
    ("Orange juice (L)", "beverage", 40, 12, "liters"),
    ("Eggs (units)", "food", 300, 180, "units"),
    ("Bread rolls", "food", 120, 45, "units"),
    ("Smoked salmon (kg)", "food", 4, 1.1, "kg"),
    ("Champagne (bottles)", "beverage", 24, 6, "bottles"),
    ("Still water (bottles)", "beverage", 200, 88, "bottles"),
    ("Sparkling water (bottles)", "beverage", 150, 42, "bottles"),
    ("Minibar beer (units)", "minibar", 160, 52, "units"),
    ("Minibar snacks (units)", "minibar", 200, 73, "units"),
    ("Restaurant covers forecast", "operations", 45, 45, "covers"),
    ("Wine (bottles)", "beverage", 60, 28, "bottles"),
    ("Allergen-free bread", "food", 20, 3, "units"),
    ("Vegetarian main portions", "food", 15, 14, "units"),
]

fb_rows = []
for i, (name, cat, par, stock, unit) in enumerate(fb_items, 1):
    fb_rows.append({
        "item_id": f"FB{i:03d}",
        "item_name": name,
        "category": cat,
        "par_level": par,
        "current_stock": stock,
        "unit": unit,
        "last_updated": TODAY.strftime("%Y-%m-%d 06:00"),
        "alert": "YES" if stock < par * 0.4 else ("WARN" if stock < par * 0.6 else "OK"),
    })

with open("data/fb_inventory.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fb_rows[0].keys())
    writer.writeheader()
    writer.writerows(fb_rows)

print(f"fb_inventory.csv: {len(fb_rows)} items")

# ── BASELINE SNAPSHOT ──────────────────────────────────────────────────────────
# Scenario runs mutate these CSVs permanently (room reassignments, new tickets,
# rate changes). Save a clean copy here so POST /api/reset can restore it without
# re-running this whole generator.
baseline_dir = Path("data/_baseline")
baseline_dir.mkdir(exist_ok=True)
for csv_file in Path("data").glob("*.csv"):
    shutil.copy(csv_file, baseline_dir / csv_file.name)
print(f"\nBaseline snapshot saved to data/_baseline/ — POST /api/reset restores it anytime.")
print("All CSV files generated successfully.")
