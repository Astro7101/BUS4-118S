from __future__ import annotations

from typing import Dict, List

from src.core.models import AgentState
from src.tools.mcp_registry import MCPToolRegistry


class WorkflowAgent:
    """Executes automated IT workflows via MCP-style tools."""

    def __init__(self, mcp_tools: MCPToolRegistry) -> None:
        self.mcp_tools = mcp_tools

    def run(self, state: AgentState) -> AgentState:
        intent = state.get("intent", "general_support")
        actions: List[Dict[str, object]] = []
        result: Dict[str, object] = {}
        escalation_needed = False
        msg = state["user_message"].lower()
        broad_impact = any(kw in msg for kw in ("everyone", "entire area", "whole floor", "all users"))

        if intent == "password_reset":
            result = self.mcp_tools.call("reset_password", user_id=state["user_id"])
            actions.append({"tool": "reset_password", "result": result})

        elif intent == "account_locked":
            result = self.mcp_tools.call("unlock_account", user_id=state["user_id"])
            actions.append({"tool": "unlock_account", "result": result})
            escalation_needed = True

        elif intent == "wifi_troubleshooting":
            if broad_impact or "still not working" in msg:
                result = self.mcp_tools.call(
                    "create_ticket",
                    title="WiFi connectivity incident",
                    description=state["user_message"],
                    priority="high",
                )
                actions.append({"tool": "create_ticket", "result": result})
                escalation_needed = True

        elif intent == "vpn_issue":
            result = self.mcp_tools.call("check_vpn_logs", user_id=state["user_id"])
            actions.append({"tool": "check_vpn_logs", "result": result})
            escalation_needed = True

        elif intent == "software_issue":
            entities = state.get("entities", {})
            app = entities.get("application", "the application")
            result = self.mcp_tools.call(
                "create_ticket",
                title=f"Software issue: {app}",
                description=state["user_message"],
                priority="medium",
            )
            actions.append({"tool": "create_ticket", "result": result})

        elif intent == "ticket_request":
            result = self.mcp_tools.call(
                "create_ticket",
                title="User-requested IT support ticket",
                description=state["user_message"],
                priority="medium",
            )
            actions.append({"tool": "create_ticket", "result": result})
            escalation_needed = True

        state["proposed_actions"] = actions
        state["automated_result"] = result
        state["escalation_needed"] = escalation_needed
        state.setdefault("trace", []).append(
            f"WorkflowAgent executed {len(actions)} automated action(s)"
        )
        return state
