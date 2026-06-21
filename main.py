"""
Villa Antica Barcelona — Entry Point
Run: python main.py
Then open http://localhost:8000/docs for the API explorer.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Validate API key
if not os.getenv("ANTHROPIC_API_KEY"):
    print("ERROR: ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key.")
    sys.exit(1)

import uvicorn

if __name__ == "__main__":
    print("=" * 56)
    print("  🏨  VILLA ANTICA BARCELONA — AI AGENT SYSTEM")
    print("  80-room boutique hotel · Barcelona, Spain")
    print("-" * 56)
    print("  API docs:    http://localhost:8000/docs")
    print("  Activity:    GET /api/activity")
    print("  Live stream: GET /stream/activity (SSE)")
    print("  Scenarios:   POST /api/scenarios/a|b|c")
    print("=" * 56)
    uvicorn.run(
        "dashboard.app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="warning",
    )
