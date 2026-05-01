from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.core.orchestrator import SupportOrchestrator


app = FastAPI(title="Multi-Agent IT Support System", version="1.0.0")

# Allow the HTML UI to call the API from any origin (demo only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = SupportOrchestrator()
UI_PATH = Path(__file__).parent / "chat_ui.html"


class SupportRequest(BaseModel):
    user_id: str
    message: str


@app.get("/", include_in_schema=False)
def serve_ui() -> FileResponse:
    """Serve the HTML chat UI."""
    return FileResponse(UI_PATH)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "version": "1.0.0"}


@app.get("/tools")
def list_tools() -> Dict[str, Any]:
    """List available MCP tools (mirrors MCP tool discovery)."""
    return {"tools": orchestrator.workflow.mcp_tools.list_tools()}


@app.post("/support")
def support(req: SupportRequest) -> Dict[str, Any]:
    state = orchestrator.handle(req.user_id, req.message)
    return {
        "response": state["final_response"],
        "intent": state.get("intent"),
        "confidence": state.get("confidence", 0),
        "entities": state.get("entities", {}),
        "retrieved_context": state.get("retrieved_context", []),
        "automated_result": state.get("automated_result", {}),
        "escalation_needed": state.get("escalation_needed", False),
        "escalation_reason": state.get("escalation_reason"),
        "trace": state.get("trace", []),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=8000, reload=False)
