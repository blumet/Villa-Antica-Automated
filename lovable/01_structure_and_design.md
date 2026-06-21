# Lovable Prompt 1 of 3 — Structure & Design System
# Paste this FIRST. It creates the shell and visual language.
#
# Original design — inspired by general enterprise PMS dashboard conventions
# (top nav, stat cards, reservation grid, side activity panel). Not a copy of
# any specific vendor's product. Visual identity: Mediterranean boutique hotel.

Build an operations dashboard called "Villa Antica Barcelona — Front Desk".
Visual identity: ink-teal header, terracotta accents, warm sand background —
a Mediterranean boutique-hotel palette, not a generic corporate blue dashboard.

## Color tokens (use these names as CSS vars)
- `--bg-header`: #1b2e35 (deep ink-teal)
- `--bg-page`: #f6f2ec (warm sand)
- `--bg-card`: #ffffff
- `--bg-table-header`: #faf8f3
- `--border-card`: #e8e1d3
- `--border-table`: #ece6d9
- `--text-primary`: #23282e
- `--text-muted`: #7c7468
- `--text-header`: #ffffff
- `--accent-primary`: #c15a3c (terracotta — links, primary buttons)
- `--accent-gold`: #c98a3e (VIP / loyalty accents)
- `--status-teal-bg`: #e6f2ef
- `--status-teal-text`: #1f7a6c
- `--amber`: #d9952c
- `--amber-bg`: #fdf2e1
- `--red-alert`: #b3392b
- `--red-bg`: #fbeae6
- `--selected-card-border`: #c15a3c
- `--selected-card-bg`: #fbf1ea

Font: Inter from Google Fonts. Import it.

Card style: rounded corners (10px), subtle shadow `0 1px 3px rgba(0,0,0,0.08)`, gap between cards (not flush dividers). This should feel like a modern SaaS dashboard, not a flat legacy grid.

## Layout (top to bottom, full viewport)

### 1. Header bar — 56px, bg `--bg-header`
- Left: hamburger icon · hotel crest 24x24 · "Villa Antica Barcelona" 13px semibold white · back arrow · breadcrumb "Property › VAB-BCN-01 › Front Desk" in #9aa8a4 12px
- Right: search input (dark bg #243a42, 220px, placeholder "Search reservation...") · cart icon (red badge "3") · bell icon (amber badge "5") · help circle · user avatar "TM" · "VAB-BCN-01" 11px #9aa8a4 · live clock 11px white

### 2. Mode banner — 36px full width
Amber by default: `⚠️  AI Agent Mode — agents are monitoring and acting on live data.`
Style: bg `--amber-bg`, text #8a5f10, border-left 4px solid `--amber`, padding 0 20px.
Turns red when escalations are pending (logic comes in Prompt 3).

### 3. Stat cards row — 4 cards with gaps between them (not flush), 110px tall, rounded 10px, white bg, subtle shadow
Each has: large number (32px bold #1b2e35) + label row (11px grey) + small trend line at bottom (e.g. "+4 vs yesterday" in 11px teal or red).

Card 1 (highlighted — terracotta left border 3px, bg `--selected-card-bg`):
- Number: fetched from GET /api/hotel/state → occupancy.active_reservations
- Labels: "Arrivals" | "Expected Guest Arrivals"
- Terracotta checkmark icon top-right

Card 2: Number = occupancy.occupancy_pct + "%" · Labels: "In-House" | "Occupancy"
Card 3: Number = occupancy.occupied · Labels: "Departures" | "Expected Guest Departures"
Card 4: Number = occupancy.clean_available · Labels: "Housekeeping" | "Rooms Inspected"

### 4. Filter bar — 52px, white bg, border-bottom
Left to right: "Search ⓘ" label · search input 380px (placeholder "Search reservation by...") · "Room No. ⓘ" + input 120px · "Membership Number" + input 140px · "Sort by *" dropdown "Arrival Ascending ▼" 180px · "☰ Filters" button (outlined) · "+ Add Task" button (bg `--accent-primary`, white text)

### 5. Main area = reservations table (Section 2) + agent panel (Section 3)
Table takes full width by default. Agent panel is a 380px collapsible right drawer.

### 6. Bottom status bar — 28px fixed, bg `--bg-header`
Left: "Villa Antica Barcelona  |  AI Agent Mode  |  5 agents active" — 11px white
Right: green/red dot for backend health (GET /api/health) + "localhost:8000"

API base: const API_BASE = "http://localhost:8000" — declare at top of app.
