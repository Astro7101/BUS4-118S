from __future__ import annotations

import random
import string
from typing import Any, Callable, Dict


class MCPToolRegistry:
    """MCP-style tool registry.

    Simulates a Model Context Protocol integration layer by standardizing how
    tools are discovered and called. In production, these map to external systems
    such as Jira, ServiceNow, Okta, GitHub, or internal automation services.
    Each tool call returns a structured dict — a contract mirroring real MCP tool responses.
    """

    TOOL_DESCRIPTIONS = {
        "create_ticket": "Creates a helpdesk ticket in the IT Service Management system (e.g., ServiceNow/Jira).",
        "reset_password": "Sends a secure password-reset email via the identity provider (e.g., Okta/Azure AD).",
        "check_vpn_logs": "Queries VPN gateway logs to diagnose connection failures for a specific user.",
        "unlock_account": "Unlocks an Active Directory account that has been locked due to failed login attempts.",
        "check_system_logs": "Retrieves recent application or system event logs for diagnostic purposes.",
    }

    def __init__(self) -> None:
        self.tools: Dict[str, Callable[..., Dict[str, Any]]] = {
            "create_ticket": self.create_ticket,
            "reset_password": self.reset_password,
            "check_vpn_logs": self.check_vpn_logs,
            "unlock_account": self.unlock_account,
            "check_system_logs": self.check_system_logs,
        }

    # ------------------------------------------------------------------
    # MCP interface
    # ------------------------------------------------------------------

    def list_tools(self) -> Dict[str, str]:
        """Returns available tools and their descriptions (mirrors MCP tool listing)."""
        return dict(self.TOOL_DESCRIPTIONS)

    def call(self, tool_name: str, **kwargs: Any) -> Dict[str, Any]:
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name!r}. Available: {list(self.tools)}")
        return self.tools[tool_name](**kwargs)

    # ------------------------------------------------------------------
    # Tool implementations (simulated)
    # ------------------------------------------------------------------

    @staticmethod
    def _ticket_id() -> str:
        return "INC-" + "".join(random.choices(string.digits, k=4))

    def create_ticket(self, title: str, description: str, priority: str = "medium") -> Dict[str, Any]:
        return {
            "status": "created",
            "ticket_id": self._ticket_id(),
            "title": title,
            "priority": priority,
            "description": description,
            "system": "ServiceNow (simulated)",
        }

    def reset_password(self, user_id: str) -> Dict[str, Any]:
        return {
            "status": "success",
            "user_id": user_id,
            "message": f"Password reset link sent to {user_id}@company.com",
            "expires_in": "15 minutes",
            "system": "Okta (simulated)",
        }

    def check_vpn_logs(self, user_id: str) -> Dict[str, Any]:
        return {
            "status": "reviewed",
            "user_id": user_id,
            "finding": "Repeated disconnects detected from home ISP between 08:15 and 08:27.",
            "recommendation": "Switch to alternate VPN gateway (us-west-2) or connect via Ethernet.",
            "system": "Cisco AnyConnect logs (simulated)",
        }

    def unlock_account(self, user_id: str) -> Dict[str, Any]:
        return {
            "status": "unlocked",
            "user_id": user_id,
            "message": f"Account {user_id} has been unlocked in Active Directory.",
            "requires_human_confirm": True,
            "system": "Active Directory (simulated)",
        }

    def check_system_logs(self, user_id: str, application: str = "system") -> Dict[str, Any]:
        return {
            "status": "retrieved",
            "user_id": user_id,
            "application": application,
            "log_entries": [
                f"ERROR 14:02 {application} - Exception: Module load failed (code 0x80004005)",
                f"WARN  14:01 {application} - Low disk space warning (< 500 MB free)",
            ],
            "system": "Windows Event Log (simulated)",
        }
