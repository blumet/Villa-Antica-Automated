"""
Villa Antigua Barcelona — Guest Simulator
Handles guest communication, bot responses, and agent coordination
"""
import json
from datetime import datetime
from typing import Dict, List, Optional


class GuestSimulator:
    """Manages guest communication flow and agent coordination"""

    def __init__(self):
        self.conversation_history = []
        self.current_scenario = None
        self.guest_satisfaction = 0
        self.agents_involved = []
        self.resolved = False

    def load_scenario(self, scenario):
        """Load a new guest scenario"""
        self.current_scenario = scenario
        self.conversation_history = []
        self.agents_involved = []
        self.guest_satisfaction = 50  # Start neutral
        self.resolved = False

        # Add initial guest message
        self.add_message(
            role="guest",
            name=scenario["guest_name"],
            message=scenario["initial_message"],
            type="issue"
        )

        return self.get_next_bot_response()

    def add_message(self, role: str, name: str, message: str, type: str = "message"):
        """Add message to conversation history"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "name": name,
            "message": message,
            "type": type
        })

    def get_next_bot_response(self) -> Dict:
        """Get bot's response based on current scenario"""
        if not self.current_scenario:
            return {"error": "No scenario loaded"}

        # Return appropriate bot response based on conversation stage
        response_index = (len(self.conversation_history) - 1) // 2  # Alternating bot responses

        if response_index < len(self.current_scenario.get("bot_responses", [])):
            bot_message = self.current_scenario["bot_responses"][response_index]
        else:
            bot_message = "How can I further assist you?"

        self.add_message(
            role="bot",
            name="Vila Bot",
            message=bot_message,
            type="response"
        )

        return {
            "bot_message": bot_message,
            "options": self.get_current_options(),
            "scenario": self.current_scenario["title"]
        }

    def get_current_options(self) -> List[Dict]:
        """Get available guest options for current stage"""
        if not self.current_scenario:
            return []

        # First stage: show guest options from scenario
        response_index = (len(self.conversation_history) - 2) // 2
        if response_index == 0:
            return self.current_scenario.get("guest_options", [])

        return []

    def process_guest_choice(self, choice_index: int) -> Dict:
        """Process guest's choice and trigger agent actions"""
        if not self.current_scenario:
            return {"error": "No scenario loaded"}

        options = self.current_scenario.get("guest_options", [])
        if choice_index >= len(options):
            return {"error": "Invalid choice"}

        choice = options[choice_index]
        guest_name = self.current_scenario["guest_name"]

        # Add guest's choice message
        self.add_message(
            role="guest",
            name=guest_name,
            message=choice["text"],
            type="choice"
        )

        # Update satisfaction based on choice
        escalation_level = choice.get("escalation", "low")
        escalation_scores = {"low": 10, "medium": 0, "high": -10}
        self.guest_satisfaction += escalation_scores.get(escalation_level, 0)

        # Trigger agent actions
        action = choice.get("action")
        agents_to_involve = self._trigger_agent_action(action, choice)

        # Get resolution message from bot
        resolution_message = self._get_resolution_message(action, choice)
        self.add_message(
            role="bot",
            name="Vila Bot",
            message=resolution_message,
            type="resolution"
        )

        self.resolved = True

        # Calculate final satisfaction
        self._calculate_final_satisfaction()

        return {
            "action": action,
            "resolution_message": resolution_message,
            "agents_involved": agents_to_involve,
            "guest_satisfaction": self.guest_satisfaction,
            "reward": self._get_reward(),
            "conversation": self.get_conversation_summary()
        }

    def _trigger_agent_action(self, action: str, choice: Dict) -> List[str]:
        """Trigger agent actions based on guest's choice"""
        agents = self.current_scenario.get("required_agents", [])
        self.agents_involved = agents

        action_log = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "agents": agents,
            "details": choice.get("action_details", "")
        }

        # Log action for live feed
        print(f"[AGENT ACTION] {action} - Agents: {', '.join(agents)}")

        return agents

    def _get_resolution_message(self, action: str, choice: Dict) -> str:
        """Generate resolution message based on action"""
        messages = {
            "charge_extension": "Perfect! I've registered your late checkout for 2pm. There will be a €30 charge added to your bill. Enjoy your lunch!",
            "room_change": "Absolutely. We're preparing a fresh room for you right now. A bellhop will be with you in 5 minutes to assist with your move.",
            "credit_only": "Done. I've issued a €50 credit to your account. Maintenance will be up in 10 minutes to repair the AC.",
            "room_change_plus_credit": "Perfect. Room change is being prepared, and I've added a €50 credit. We apologize for the inconvenience.",
            "provide_items": "Noise-canceling headphones and sleep mask are on their way to your room—5 minutes. Sleep well!",
            "request_credit": "Completely understood. I'm upgrading you to a room upgrade tomorrow night at no charge, plus €50 credit for tonight's disruption.",
            "courier_service": "Understood. We're dispatching your passport to the airport by courier immediately. You'll have it in about 1.5 hours. We'll text you tracking info.",
            "replace_meal": "Head chef is preparing a fresh meal immediately, with extra attention to your allergy. You'll have it in 15 minutes.",
            "refund_plus_credit": "We're completely removing the meal charge and adding €100 credit. Our kitchen manager will call you personally.",
            "escalate_to_gm": "Our General Manager will call you within 5 minutes to discuss this properly.",
            "issue_refund": "Refunding €50 immediately. The damage was our oversight. My apologies.",
            "offer_upgrade": "You're upgraded to a deluxe room for tomorrow night. Full breakfast included—no charge.",
            "refund_plus_upgrade": "€50 refund processed, and you're upgraded for tomorrow. No mistakes on our part next time.",
            "fix_in_room": "IT is en route—they'll be there in 3 minutes. You'll be connected before your call.",
            "business_center": "Business center is ready. Private room, hardline connection. I'm sending someone to escort you. You'll be set up in 2 minutes.",
            "get_eta": "IT says 5 minutes max. If it takes longer, you'll have a dedicated hotspot. You won't miss your call.",
            "provide_amenities": "Housekeeping is bringing everything now—towels, toiletries, all of it. 5 minutes.",
            "provide_amenities_plus_credit": "All supplies are coming immediately, and I'm adding a €30 credit for the rough start.",
            "room_upgrade": "I'm moving you to a junior suite at no additional charge. You'll be much more comfortable there.",
            "remove_charge": "€40 unauthorized charge removed immediately. Your corrected bill is ready at checkout.",
            "remove_all_charges": "Both charges removed. I've also added a €15 apology credit. You won't be charged for the facility fee.",
            "partial_resolution": "The €40 unauthorized charge is removed, and I've added a €15 credit for the inconvenience on the facility fee. Fair?",
            "full_refund": "€450 refund approved immediately. We completely understand. Safe travels, and our thoughts are with your family.",
            "future_voucher": "€450 credit issued. Use it whenever things settle down. We'll have a room ready for you.",
            "split_refund": "€225 refund + €225 credit voucher. Take care of your family. We're here when you return.",
        }

        return messages.get(action, "We're taking care of this for you. Thank you for your patience.")

    def _calculate_final_satisfaction(self):
        """Calculate guest satisfaction based on resolution quality"""
        if not self.current_scenario:
            return

        # Satisfaction drivers: speed, empathy, compensation
        drivers = self.current_scenario.get("satisfaction_drivers", [])

        # Bonus for compensation amount
        for choice in self.current_scenario.get("guest_options", []):
            if choice.get("text") in [msg["message"] for msg in self.conversation_history]:
                amount = choice.get("amount", 0)
                if amount > 0:
                    self.guest_satisfaction += min(20, amount // 5)  # Bonus for compensation

        # Clamp satisfaction 0-100
        self.guest_satisfaction = max(0, min(100, self.guest_satisfaction))

    def _get_reward(self) -> str:
        """Determine reward based on satisfaction and scenario"""
        if self.guest_satisfaction >= 80:
            return self.current_scenario.get("reward_if_happy", "Complimentary upgrade")
        elif self.guest_satisfaction >= 60:
            return "€25 credit for future use"
        else:
            return "Incident logged for follow-up"

    def get_conversation_summary(self) -> List[Dict]:
        """Get formatted conversation history"""
        return [
            {
                "time": msg["timestamp"],
                "from": f"{msg['name']} ({msg['role']})",
                "message": msg["message"],
                "type": msg["type"]
            }
            for msg in self.conversation_history
        ]

    def get_live_feed_entry(self) -> Dict:
        """Format current state for live feed display"""
        if not self.current_scenario:
            return {}

        return {
            "timestamp": datetime.now().isoformat(),
            "guest": self.current_scenario["guest_name"],
            "room": self.current_scenario["room"],
            "issue": self.current_scenario["title"],
            "status": "resolved" if self.resolved else "active",
            "agents_involved": self.agents_involved,
            "satisfaction": self.guest_satisfaction,
            "reward": self._get_reward() if self.resolved else None,
            "message_count": len(self.conversation_history)
        }


# Global instance
_simulator = None


def get_simulator() -> GuestSimulator:
    """Get or create global simulator instance"""
    global _simulator
    if _simulator is None:
        _simulator = GuestSimulator()
    return _simulator


def reset_simulator():
    """Reset simulator for new scenario"""
    global _simulator
    _simulator = GuestSimulator()
    return _simulator
