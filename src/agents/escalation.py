from __future__ import annotations

from src.core.models import AgentState

# Intents that always require human follow-up
_HIGH_RISK_INTENTS = {"vpn_issue", "account_locked"}
_ALWAYS_ESCALATE_KEYWORDS = {"everyone", "entire area", "whole floor", "all users", "outage"}


class EscalationAgent:
    """Decides whether the case should be escalated to a human technician."""

    def run(self, state: AgentState) -> AgentState:
        intent = state.get("intent", "general_support")
        msg = state.get("user_message", "").lower()
        already_flagged = state.get("escalation_needed", False)

        # Rule 1: certain intents always escalate
        if intent in _HIGH_RISK_INTENTS:
            state["escalation_needed"] = True
            state["escalation_reason"] = f"Intent '{intent}' requires human review."

        # Rule 2: broad-impact language escalates
        elif any(kw in msg for kw in _ALWAYS_ESCALATE_KEYWORDS):
            state["escalation_needed"] = True
            state["escalation_reason"] = "Potential broad impact — routing to IT on-call team."

        # Rule 3: workflow already flagged it
        elif already_flagged:
            state["escalation_needed"] = True
            state["escalation_reason"] = state.get("escalation_reason", "Flagged by workflow agent.")

        else:
            state["escalation_needed"] = False
            state["escalation_reason"] = None

        state.setdefault("trace", []).append(
            f"EscalationAgent: escalation_needed={state['escalation_needed']}"
            + (f" | reason: {state['escalation_reason']}" if state["escalation_needed"] else "")
        )
        return state
