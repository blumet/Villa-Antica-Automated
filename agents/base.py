"""
BaseAgent — Villa Antica Barcelona
Every specialist agent inherits from this class.
Pattern: receive event → call Claude with tools → execute tool calls → return result + escalation flag.
"""
from __future__ import annotations
import json
import time
from datetime import datetime
from typing import Any, Callable

import anthropic

from config import LLM_MODEL, ESCALATION

# Shared Anthropic client — lazy initialized
_client: anthropic.Anthropic | None = None

def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client

# Global activity log — FastAPI streams this to the dashboard
activity_log: list[dict] = []


def log_event(agent: str, event_type: str, message: str, data: dict | None = None,
              escalate: bool = False) -> dict:
    entry = {
        "id": len(activity_log) + 1,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "agent": agent,
        "event_type": event_type,   # action | decision | escalation | tool_call | message
        "message": message,
        "data": data or {},
        "escalate": escalate,
    }
    activity_log.append(entry)
    print(f"[{entry['timestamp']}] [{agent}] {message}")
    return entry


class BaseAgent:
    """
    Wraps an Anthropic chat loop with tool use.
    Subclasses define: name, system_prompt, tool_names (keys from ALL_TOOLS).
    """
    name: str = "agent"
    system_prompt: str = "You are a hotel operations agent."
    tool_names: list[str] = []

    def __init__(self):
        from tools.pms import ALL_TOOLS
        self.tools = {k: ALL_TOOLS[k] for k in self.tool_names if k in ALL_TOOLS}
        self.tool_schemas = [t["schema"] for t in self.tools.values()]
        self.tool_fns: dict[str, Callable] = {k: t["fn"] for k, t in self.tools.items()}

    def _check_escalation(self, text: str) -> bool:
        """Detect if response text contains safety keywords → escalate."""
        text_lower = text.lower()
        return any(kw in text_lower for kw in ESCALATION["safety_keywords"])

    def run(self, event: dict) -> dict:
        """
        Main agent loop.
        event: {"type": str, "description": str, **kwargs}
        Returns: {"agent": str, "result": str, "escalate": bool, "actions": list}
        """
        log_event(self.name, "action", f"Received event: {event.get('type', 'unknown')}", event)

        messages = [
            {
                "role": "user",
                "content": (
                    f"Event: {event.get('type', 'task')}\n\n"
                    f"{event.get('description', '')}\n\n"
                    f"Context: {json.dumps({k: v for k, v in event.items() if k not in ('type','description')}, indent=2)}"
                ),
            }
        ]

        actions_taken = []
        escalate = False
        final_text = ""
        max_iterations = 8

        for _ in range(max_iterations):
            kwargs = {"model": LLM_MODEL, "max_tokens": 1024, "system": self.system_prompt, "messages": messages}
            if self.tool_schemas:
                kwargs["tools"] = self.tool_schemas

            response = _get_client().messages.create(**kwargs)

            # Collect text from this response
            for block in response.content:
                if hasattr(block, "text"):
                    final_text = block.text
                    if self._check_escalation(final_text):
                        escalate = True

            # If no tool calls → done
            if response.stop_reason != "tool_use":
                break

            # Process tool calls
            tool_calls = [b for b in response.content if b.type == "tool_use"]
            tool_results = []

            for tc in tool_calls:
                fn = self.tool_fns.get(tc.name)
                if fn is None:
                    result = {"error": f"Tool {tc.name} not available to this agent"}
                else:
                    try:
                        result = fn(**tc.input)
                    except Exception as e:
                        result = {"error": str(e)}

                log_event(self.name, "tool_call", f"Tool: {tc.name}", {"input": tc.input, "result": result})
                actions_taken.append({"tool": tc.name, "input": tc.input, "result": result})

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": json.dumps(result),
                })

            # Feed tool results back
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        return {
            "agent": self.name,
            "result": final_text,
            "escalate": escalate,
            "actions": actions_taken,
        }
