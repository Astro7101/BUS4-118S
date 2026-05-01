from __future__ import annotations

from src.agents.escalation import EscalationAgent
from src.agents.intake import IntakeAgent
from src.agents.knowledge import KnowledgeAgent
from src.agents.response import ResponseAgent
from src.agents.workflow import WorkflowAgent
from src.core.knowledge_base import VectorKnowledgeBase
from src.core.loader import load_txt_documents
from src.core.models import AgentState
from src.tools.mcp_registry import MCPToolRegistry


class SupportOrchestrator:
    def __init__(self, data_dir: str = "data") -> None:
        self.kb = VectorKnowledgeBase()
        self.kb.add_documents(load_txt_documents(data_dir))
        self.intake = IntakeAgent()
        self.knowledge = KnowledgeAgent(self.kb)
        self.workflow = WorkflowAgent(MCPToolRegistry())
        self.escalation = EscalationAgent()
        self.response = ResponseAgent()

    def handle(self, user_id: str, user_message: str) -> AgentState:
        state: AgentState = {"user_id": user_id, "user_message": user_message, "trace": []}
        for agent in [self.intake, self.knowledge, self.workflow, self.escalation, self.response]:
            state = agent.run(state)
        return state
