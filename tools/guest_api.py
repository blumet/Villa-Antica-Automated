"""
FastAPI endpoints for guest communication
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
sys.path.insert(0, '/Users/blumet/Library/Application Support/Claude/local-agent-mode-sessions/eb04f6db-8b3d-4c6f-a98c-bf36a535d774/85251725-bb66-488b-935b-34f8bbd6cc3e/local_eafc8cd0-8744-41a6-a38c-1308c89f6795/outputs')

from scenarios.guest_scenarios import get_random_scenario
from guest_simulator import get_simulator, reset_simulator

router = APIRouter(prefix="/api/guest", tags=["guest"])


class ChoiceRequest(BaseModel):
    optionIndex: int


@router.get("/new-scenario")
async def new_scenario():
    """Start a new guest scenario"""
    reset_simulator()
    simulator = get_simulator()

    scenario = get_random_scenario()
    bot_response = simulator.load_scenario(scenario)

    return {
        "scenario": scenario,
        "conversation": simulator.get_conversation_summary(),
        "options": bot_response.get("options", []),
        "bot_message": bot_response.get("bot_message", "")
    }


@router.post("/choose-option")
async def choose_option(request: ChoiceRequest):
    """Guest chooses an option"""
    simulator = get_simulator()

    result = simulator.process_guest_choice(request.optionIndex)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "scenario": simulator.current_scenario,
        "conversation": simulator.get_conversation_summary(),
        "options": [],  # No more options after choice
        "resolution_message": result.get("resolution_message", ""),
        "agents_involved": result.get("agents_involved", []),
        "guest_satisfaction": result.get("guest_satisfaction", 0),
        "reward": result.get("reward", ""),
        "action": result.get("action", "")
    }


@router.get("/status")
async def get_status():
    """Get current simulation status"""
    simulator = get_simulator()

    if not simulator.current_scenario:
        return {"status": "idle"}

    return {
        "status": "active" if not simulator.resolved else "resolved",
        "guest": simulator.current_scenario.get("guest_name", "Unknown"),
        "room": simulator.current_scenario.get("room", "Unknown"),
        "issue": simulator.current_scenario.get("title", "Unknown"),
        "satisfaction": simulator.guest_satisfaction,
        "agents_involved": simulator.agents_involved,
        "message_count": len(simulator.conversation_history)
    }


@router.get("/live-feed")
async def get_live_feed():
    """Get current interaction for live feed"""
    simulator = get_simulator()

    if not simulator.current_scenario:
        return None

    return simulator.get_live_feed_entry()
