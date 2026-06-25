# Guest Chat System Integration Guide

## Overview
This guest communication system adds realistic, dynamic guest interaction simulation to Villa Antica Barcelona. Guests present issues/requests, the bot offers options, guests choose, and agents execute actions.

**10 Realistic Scenarios:**
1. Late Checkout Request
2. AC Malfunction
3. Excessive Noise
4. Lost/Forgotten Item
5. Allergy/Dietary Issue
6. Broken Room Item
7. WiFi Outage
8. Missing Amenities
9. Billing Dispute
10. Early Departure Request

---

## File Structure & Integration

### 1. **Create New Files**

Place these in your `Hotel_Villa_Antica` repo:

```
Hotel_Villa_Antigua/
├── scenarios/
│   └── guest_scenarios.py          # NEW: 10 guest scenarios
├── tools/
│   ├── guest_simulator.py           # NEW: Chat logic & agent coordination
│   └── guest_api.py                 # NEW: FastAPI endpoints
├── dashboard/
│   └── templates/
│       └── guest_chat.html          # NEW: Guest chat UI
└── [existing files...]
```

### 2. **Update `dashboard/app.py`**

Add these imports at the top:
```python
from sys import path
path.insert(0, '/path/to/repo/tools')  # Update path as needed
from guest_api import router as guest_router
```

Then include the router in your FastAPI app:
```python
app.include_router(guest_router)
```

If you don't have a guest_router, add this line to your app initialization:
```python
app.include_router(guest_router)
```

### 3. **Update `dashboard/templates/` (Optional)**

If you want the guest chat embedded in your main dashboard, add a tab/section in your dashboard HTML:

```html
<div id="guestTab" class="tab-content">
    <iframe src="/static/guest_chat.html" style="width: 100%; height: 100%; border: none;"></iframe>
</div>
```

Or serve `guest_chat.html` directly at `/guest-chat` route.

### 4. **Update `requirements.txt`**

The guest system uses only standard FastAPI/Python. No new dependencies needed.

---

## How It Works

### User Journey:
1. **User clicks "Start New Scenario"**
   - Frontend calls `/api/guest/new-scenario`
   - Backend loads random scenario
   - Guest's initial issue is displayed

2. **Bot offers options**
   - Bot message is shown
   - Guest has 2-3 choices to pick from

3. **Guest chooses an option**
   - Frontend sends choice to `/api/guest/choose-option`
   - Backend executes agent actions
   - Resolution message is shown
   - Guest satisfaction is calculated

4. **Resolution & Reward**
   - Agents involved are displayed
   - Satisfaction score (0-100) is shown
   - If satisfaction > 60%, reward is given

### Backend Logic:
- **`GuestSimulator` class**: Manages conversation state, satisfaction tracking, agent actions
- **Scenarios**: Each has initial message, bot responses, guest options, required agents, resolution paths
- **Satisfaction**: Calculated based on escalation level, compensation amount, resolution quality
- **Rewards**: Personalized based on scenario (champagne for happy guests with preferences, etc.)

---

## API Endpoints

### `GET /api/guest/new-scenario`
Starts a new scenario with random guest issue.

**Response:**
```json
{
  "scenario": {
    "id": "late_checkout",
    "title": "Late Checkout Request",
    "guest_name": "María García",
    "room": "304",
    ...
  },
  "conversation": [
    {"role": "guest", "name": "María García", "message": "Hi...", "time": "..."}
  ],
  "options": [
    {"text": "Just until 2pm is perfect, charge me", "action": "charge_extension", ...}
  ]
}
```

### `POST /api/guest/choose-option`
Guest selects an option.

**Request:**
```json
{
  "optionIndex": 0
}
```

**Response:**
```json
{
  "scenario": {...},
  "conversation": [...],
  "resolution_message": "Perfect! I've registered your late checkout...",
  "agents_involved": ["concierge", "housekeeping"],
  "guest_satisfaction": 85,
  "reward": "Complimentary welcome drink at bar tonight"
}
```

### `GET /api/guest/status`
Get current simulation state.

### `GET /api/guest/live-feed`
Get interaction data for live feed display.

---

## Customization

### Add More Scenarios:
Edit `scenarios/guest_scenarios.py` and add to `GUEST_SCENARIOS` list:

```python
{
    "id": "your_scenario_id",
    "title": "Your Scenario Title",
    "guest_name": "Guest Name",
    "room": "101",
    "initial_message": "Guest's opening message",
    "context": "Background info",
    "guest_personality": "Description",
    "bot_responses": [
        "First bot response",
        "Second bot response (after guest's choice)"
    ],
    "guest_options": [
        {"text": "Option 1", "action": "action_1", "amount": 0, "escalation": "low"},
        {"text": "Option 2", "action": "action_2", "amount": 50, "escalation": "medium"}
    ],
    "required_agents": ["concierge", "housekeeping"],
    "agent_actions": ["update_checkout_time", "notify_housekeeping"],
    "satisfaction_drivers": ["speed", "flexibility"],
    "reward_if_happy": "Complimentary welcome drink"
}
```

### Connect to Real Agents:
In `guest_simulator.py`, modify `_trigger_agent_action()` to:
- Call real agent APIs
- Create actual tickets in your PMS
- Send real notifications
- Log to your activity stream

Currently it just logs to console; upgrade to real integration:

```python
def _trigger_agent_action(self, action: str, choice: Dict) -> List[str]:
    agents = self.current_scenario.get("required_agents", [])
    
    # TODO: Call real agent APIs here
    # Example:
    # if "maintenance" in agents:
    #     send_maintenance_request(...)
    # if "concierge" in agents:
    #     create_concierge_ticket(...)
    
    return agents
```

### Integrate Live Feed:
Update your live feed in `dashboard/` to pull from `/api/guest/live-feed`:

```python
# In your dashboard API:
@app.get("/api/activity")
async def get_activity():
    guest_feed = requests.get("http://localhost:8000/api/guest/live-feed").json()
    # Merge with agent activity...
```

---

## Testing Locally

1. **Copy files to your repo**
2. **Run your existing FastAPI app**
3. **Navigate to `/guest-chat.html`** (or embed iframe in dashboard)
4. **Click "Start New Scenario"**
5. **Choose guest options and watch agents coordinate**

---

## Next Steps

1. **Upload to GitHub** (use web UI: Add files → guest_scenarios.py, guest_simulator.py, guest_api.py, guest_chat.html)
2. **Update dashboard/app.py** to include `guest_router`
3. **Update requirements.txt** (no new deps needed)
4. **Test from Render** once deployed
5. **Connect to real PMS/agent systems** for production use
6. **Add real person alert** on escalations (call, email, SMS)

---

## Live Feed Integration Example

In your current activity feed, add guest interactions:

```python
from tools.guest_api import get_simulator

# In your live feed endpoint:
simulator = get_simulator()
if simulator.current_scenario:
    guest_entry = {
        "type": "guest_interaction",
        "guest": simulator.current_scenario["guest_name"],
        "room": simulator.current_scenario["room"],
        "issue": simulator.current_scenario["title"],
        "agents_involved": simulator.agents_involved,
        "satisfaction": simulator.guest_satisfaction,
        "messages": len(simulator.conversation_history),
        "timestamp": datetime.now().isoformat()
    }
```

---

## Real Person Alerts

For escalations (guest dissatisfaction, high-priority issues), add to `guest_simulator.py`:

```python
def _send_alert_if_needed(self):
    """Alert real person if satisfaction drops or escalation is high"""
    if self.guest_satisfaction < 40:
        # Send SMS/email to on-call manager
        send_alert(f"Low satisfaction: {self.current_scenario['guest_name']} - Room {self.current_scenario['room']}")
    
    # Or check escalation level:
    for choice in self.current_scenario.get("guest_options", []):
        if choice.get("escalation") == "high":
            send_escalation_alert(...)
```

---

## Satisfaction Scoring

- **Base**: 50 (neutral)
- **Escalation impact**: -10 (high), 0 (medium), +10 (low)
- **Compensation bonus**: +5 per €20 offered
- **Final clamp**: 0-100

Example:
- Guest chooses low-escalation + €50 refund = 50 + 10 + 10 = **70%** satisfaction → Reward given
- Guest chooses high-escalation + no compensation = 50 - 10 = **40%** → No reward, incident logged

---

## Deployment to Render

No changes needed—the guest system runs within your existing FastAPI app. Once deployed, test:

```
https://your-render-url.onrender.com/guest-chat.html
```

The system will call `/api/guest/*` endpoints on your Render service.
