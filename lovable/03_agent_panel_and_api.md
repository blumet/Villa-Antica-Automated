# Lovable Prompt 3 of 3 — Agent Panel, Live API, and Behaviours
# Paste this LAST. It wires up the live data and the AI agent side panel.

Now add the Agent Ops panel and connect everything to the backend API.

## API wiring

const API_BASE = "http://localhost:8000";

Stat cards poll GET /api/hotel/state every 30s. Response shape:
{
  occupancy: {
    active_reservations: number,   → Arrivals card
    occupancy_pct: number,         → In-House card (display as "X%")
    occupied: number,              → Departures card (display as occupied - 10)
    clean_available: number        → Housekeeping card
  }
}

Health check: poll GET /api/health every 10s. Green dot if 200, red if not.

Escalations: poll GET /api/escalations every 5s.
Response: array of { id, agent, message, status }
If any have status "pending", the mode banner turns RED:
  bg `--red-bg`, text #8a2a1f, border-left 4px solid `--red-alert`
  Text: "🔴  Agent escalation requires GM approval — [N] item(s) pending"

## Agent Ops right panel (380px wide, slides in from right)

Toggle: fixed right-side vertical pill "◀ Agent Ops" bg `--bg-header` white text 11px.
Panel: bg white, rounded-left 12px, shadow 0 0 24px rgba(0,0,0,0.15).
Header: bg `--bg-header` · "🤖 Agent Activity" 13px semibold white · pulsing green dot · close X.

Three tabs: Live Feed | Scenarios | Escalations

### Tab 1 — Live Feed
Connect with: const es = new EventSource(API_BASE + "/stream/activity")
es.onmessage = e => { const entry = JSON.parse(e.data); prepend to feed }

Each entry is a compact row:
  - Coloured pill badge (10px text) by agent:
      ORCHESTRATOR → #1b2e35 | guest_comms → #c15a3c | revenue → #6b4fa0
      housekeeping → #1f7a6c | maintenance → #c98a3e | fb → #a85d3b | GM → #d9952c
  - Timestamp #9a958a 11px
  - Message 12px #3a352c, truncate at 2 lines
  - Escalation entries: amber left-border + ⚠️ prefix

Auto-scroll to bottom. "Clear" button calls DELETE /api/activity.
Empty state: "Waiting for agent activity..." + subtle spinner.

### Tab 2 — Scenarios
Three cards (title 13px semibold `--bg-header` color, description 11px `--text-muted`, ▶ Run button outlined in `--accent-primary`):

1. "Scenario A: The Difficult Tuesday"
   Desc: "Revenue agent detects soft night. ADR floor at risk. Escalation fires to GM."
   Run → POST /api/scenarios/a

2. "Scenario B: The Angry Guest at 11pm"
   Desc: "Complaint triggers parallel agents. Room moved. Ticket logged. Zero human involvement."
   Run → POST /api/scenarios/b

3. "Scenario C: Morning Briefing"
   Desc: "All 5 agents brief the GM simultaneously at 07:00."
   Run → POST /api/scenarios/c

On click: show spinner on button until POST responds, then pulse the Live Feed tab.

### Tab 3 — Escalations
Pending items (status === "pending"): amber card
  - Agent name + message preview
  - ✅ Approve button → POST /api/escalations/decide { escalation_id, decision: "approved" }
  - ↩ Override button → POST /api/escalations/decide { escalation_id, decision: "overridden" }

Resolved items: collapsed grey row with checkmark or X icon.
Empty state: "✅ No pending escalations"

## Backend offline handling
If /api/health fails, replace amber mode banner with:
  bg `--red-bg`, text #8a2a1f, border-left 4px solid `--red-alert`
  "⚠️  Backend offline — run: python main.py in the villa_antica_barcelona folder"

## Final notes
- No auth, no routing, single page.
- Table rows are static (hardcoded). Stat cards are live.
- The agent panel is the only dynamic layer the demo needs.
- Mobile: hide the agent panel toggle; show a bottom tab bar with the 3 tabs instead.
