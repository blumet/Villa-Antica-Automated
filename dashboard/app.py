"""
Villa Antica Barcelona — FastAPI Backend
Exposes the agent system as a REST + SSE API.
Lovable (or any React app) connects to this.
"""
import asyncio
import json
import shutil
import sys
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base import activity_log, log_event
from agents.orchestrator import Orchestrator, escalation_queue
from tools.pms import (
    get_occupancy_stats, get_open_tickets, get_fb_alerts,
    get_soft_nights, get_rates, get_rooms_by_status,
)
from config import HOTEL, COMMERCIAL_BRIEF

@asynccontextmanager
async def lifespan(app: FastAPI):
    log_event("SYSTEM", "action", f"🏨 {HOTEL['name']} agent system starting...")
    app.state.orchestrator = Orchestrator()
    log_event("SYSTEM", "action", "✅ All agents online. Ready.")
    yield

app = FastAPI(title="Villa Antica Barcelona Agent API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/stream/activity")
async def stream_activity():
    async def event_generator():
        last_id = 0
        while True:
            if len(activity_log) > last_id:
                for entry in activity_log[last_id:]:
                    yield f"data: {json.dumps(entry)}\n\n"
                last_id = len(activity_log)
            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

@app.get("/api/hotel/state")
def get_hotel_state():
    return {
        "hotel": HOTEL,
        "commercial_brief": COMMERCIAL_BRIEF,
        "occupancy": get_occupancy_stats(),
        "open_tickets": len(get_open_tickets()),
        "fb_alerts": len(get_fb_alerts()),
        "soft_nights": len(get_soft_nights(days_ahead=7)),
    }

@app.get("/api/hotel/occupancy")
def get_occupancy():
    return get_occupancy_stats()

@app.get("/api/hotel/rates")
def get_today_rates():
    return get_rates()

@app.get("/api/hotel/soft-nights")
def get_soft():
    return get_soft_nights(days_ahead=14)

@app.get("/api/hotel/tickets")
def get_tickets():
    return get_open_tickets()

@app.get("/api/hotel/fb-alerts")
def get_fb():
    return get_fb_alerts()

@app.get("/api/rooms/{status}")
def rooms_by_status(status: str):
    return get_rooms_by_status(status)

@app.get("/api/activity")
def get_activity(limit: int = 50):
    return activity_log[-limit:]

@app.delete("/api/activity")
def clear_activity():
    activity_log.clear()
    return {"cleared": True}

DATA_DIR = Path(__file__).parent.parent / "data"
BASELINE_DIR = DATA_DIR / "_baseline"

def _reset_to_baseline(announce: bool = True) -> list[str]:
    if not BASELINE_DIR.exists():
        return []
    restored = []
    for f in BASELINE_DIR.glob("*.csv"):
        shutil.copy(f, DATA_DIR / f.name)
        restored.append(f.name)
    activity_log.clear()
    escalation_queue.clear()
    if announce:
        log_event("SYSTEM", "action", "🔄 Demo data reset to baseline.", {"files": restored})
    return restored

@app.post("/api/reset")
def reset_demo_data():
    restored = _reset_to_baseline()
    if not restored:
        return {
            "success": False,
            "error": "No baseline found. Run 'python3 data/generate_data.py' once to create it.",
        }
    return {"success": True, "restored_files": restored}

@app.get("/api/escalations")
def get_escalations():
    return escalation_queue

class EscalationDecision(BaseModel):
    escalation_id: int
    decision: str
    note: str = ""

@app.post("/api/escalations/decide")
def decide_escalation(body: EscalationDecision):
    for esc in escalation_queue:
        if esc["id"] == body.escalation_id:
            esc["status"] = body.decision
            esc["gm_note"] = body.note
            log_event("GM", "decision",
                      f"✅ GM {body.decision} escalation #{body.escalation_id}: {body.note}")
            return {"success": True, "escalation": esc}
    return {"success": False, "error": "Escalation not found"}

def _run_in_thread(fn, *args):
    t = threading.Thread(target=fn, args=args, daemon=True)
    t.start()

@app.post("/api/scenarios/a")
def run_scenario_a(background_tasks: BackgroundTasks):
    _reset_to_baseline(announce=False)
    from scenarios.scenario_a import run
    background_tasks.add_task(run, app.state.orchestrator)
    return {"status": "running", "scenario": "A - The Difficult Tuesday"}

@app.post("/api/scenarios/b")
def run_scenario_b(background_tasks: BackgroundTasks):
    _reset_to_baseline(announce=False)
    from scenarios.scenario_b import run
    background_tasks.add_task(run, app.state.orchestrator)
    return {"status": "running", "scenario": "B - The Angry Guest at 11pm"}

@app.post("/api/scenarios/c")
def run_scenario_c(background_tasks: BackgroundTasks):
    _reset_to_baseline(announce=False)
    from scenarios.scenario_c import run
    background_tasks.add_task(run, app.state.orchestrator)
    return {"status": "running", "scenario": "C - Morning Briefing"}

class CustomEvent(BaseModel):
    type: str
    description: str
    data: dict = {}

@app.post("/api/dispatch")
def dispatch_event(event: CustomEvent, background_tasks: BackgroundTasks):
    ev = {"type": event.type, "description": event.description, **event.data}
    background_tasks.add_task(app.state.orchestrator.dispatch, ev)
    return {"status": "dispatched", "event": ev}

@app.get("/api/health")
def health():
    return {"status": "ok", "hotel": HOTEL["name"], "agents": 5}
