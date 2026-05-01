from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict, total=False):
    user_id: str
    user_message: str
    intent: str
    confidence: int
    entities: Dict[str, Any]
    retrieved_context: List[str]
    proposed_actions: List[Dict[str, Any]]
    automated_result: Dict[str, Any]
    escalation_needed: bool
    escalation_reason: Optional[str]
    final_response: str
    trace: List[str]


@dataclass
class DocumentChunk:
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
