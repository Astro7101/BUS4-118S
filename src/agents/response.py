from __future__ import annotations

from src.core.models import AgentState


class ResponseAgent:
    """Composes the final user-facing response, grounded in retrieved context."""

    def run(self, state: AgentState) -> AgentState:
        intent = state.get("intent", "general_support")
        ctx = state.get("retrieved_context", [])
        result = state.get("automated_result", {})
        escalation = state.get("escalation_needed", False)
        escalation_reason = state.get("escalation_reason", "")

        if intent == "password_reset":
            final = (
                f"I've initiated a password reset for your account. "
                f"{result.get('message', '')} "
                "If you still cannot sign in after resetting, I can open a ticket for IT."
            )

        elif intent == "account_locked":
            final = (
                f"Your account unlock has been submitted. {result.get('message', '')} "
                "A technician will verify and confirm within 15 minutes. "
                "This case has been flagged for human review per security policy."
            )

        elif intent == "wifi_troubleshooting":
            kb_steps = " ".join(ctx[:2]) if ctx else (
                "Restart the device, reconnect to Company-Secure, and test without VPN."
            )
            final = f"Here are the recommended WiFi troubleshooting steps: {kb_steps}"
            if escalation and result.get("ticket_id"):
                final += (
                    f" I also created incident ticket {result['ticket_id']} "
                    "because this may be affecting a broader area."
                )

        elif intent == "vpn_issue":
            final = (
                f"I reviewed the VPN logs for your account. "
                f"{result.get('finding', 'VPN instability detected.')} "
                "This has been escalated to the network team for follow-up."
            )

        elif intent == "software_issue":
            kb_tip = ctx[0] if ctx else "Please collect the exact error message and application version."
            final = (
                f"Here's guidance for your software issue: {kb_tip} "
            )
            if result.get("ticket_id"):
                final += f"I've also logged this as ticket {result['ticket_id']} for IT follow-up."

        elif intent == "ticket_request":
            final = (
                f"Your support request has been logged as {result.get('ticket_id', 'a new ticket')}. "
                "An IT technician will reach out within 4 business hours."
            )

        else:
            final = (
                "I can help with: password resets, account lockouts, WiFi troubleshooting, "
                "VPN issues, software problems, and ticket creation. "
                "Please describe your issue and I'll get started right away."
            )

        if escalation and escalation_reason:
            final += f" \u26a0\ufe0f This case has been escalated: {escalation_reason}"

        state["final_response"] = final
        state.setdefault("trace", []).append("ResponseAgent composed final response")
        return state
