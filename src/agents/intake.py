from __future__ import annotations

import re

from src.core.models import AgentState


class IntakeAgent:
    """Classifies user intent and extracts entities from the support request."""

    INTENT_PATTERNS = {
        "password_reset": [
            r"password.*(reset|forgot|expired|lock|change|rest|help|problem|issue)",
            r"(forgot|reset|locked|rest|change|update|help).*(password|pw|passcode)",
            r"can.?t (log in|login|sign in)",
            r"(help|need|want).*(my\s+)?(password|pw|passcode)",
            r"password",   # broad catch — any mention of password
        ],
        "account_locked": [
            r"account.*(lock|block|suspend|disabled)",
            r"(lock|blocked|suspended).*(account|me|out)",
            r"mfa|multi.factor|authenticat",
            r"sso.*(error|fail|broken)",
        ],
        "wifi_troubleshooting": [
            r"wifi|wi-fi|wi fi",
            r"(no|lost|slow).*(internet|connection|network)",
            r"(internet|network).*(down|slow|drop)",
            r"connect.*(company.secure|corporate)",
        ],
        "vpn_issue": [
            r"vpn",
            r"remote.*(access|connect)",
            r"(connect|access).*(remote|home|offsite)",
        ],
        "software_issue": [
            r"(install|uninstall|update|upgrade).*(software|app|program|application)",
            r"(software|app|application|program).*(crash|error|broken|not working|fail)",
            r"microsoft office|word|excel|teams|zoom|outlook",
            r"license.*(error|expire|invalid)",
        ],
        "ticket_request": [
            r"ticket|escalate|create.*(issue|request|ticket)",
            r"open.*(case|ticket|request)",
        ],
    }

    def run(self, state: AgentState) -> AgentState:
        msg = state["user_message"].lower()
        intent = "general_support"
        entities: dict = {}
        confidence = 0

        for candidate_intent, patterns in self.INTENT_PATTERNS.items():
            matches = sum(1 for p in patterns if re.search(p, msg))
            if matches > confidence:
                confidence = matches
                intent = candidate_intent

        # Entity extraction
        device_match = re.search(r"(laptop|desktop|mac|macbook|windows|ipad|iphone)", msg)
        if device_match:
            entities["device"] = device_match.group(1)

        app_match = re.search(r"(office|word|excel|teams|zoom|outlook|chrome|edge|slack)", msg)
        if app_match:
            entities["application"] = app_match.group(1)

        floor_match = re.search(r"floor (\d+|[a-z]+)", msg)
        if floor_match:
            entities["location"] = floor_match.group(0)

        state["intent"] = intent
        state["entities"] = entities
        state["confidence"] = confidence
        state.setdefault("trace", []).append(
            f"IntakeAgent classified intent as '{intent}' (confidence={confidence})"
        )
        return state
