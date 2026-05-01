from __future__ import annotations

from src.core.knowledge_base import VectorKnowledgeBase
from src.core.models import AgentState


class KnowledgeAgent:
    def __init__(self, kb: VectorKnowledgeBase) -> None:
        self.kb = kb

    def run(self, state: AgentState) -> AgentState:
        docs = self.kb.search(state["user_message"], top_k=3)
        state["retrieved_context"] = [d.text for d in docs]
        state.setdefault("trace", []).append(
            f"KnowledgeAgent retrieved {len(docs)} knowledge chunks"
        )
        return state
