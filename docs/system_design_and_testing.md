# Multi-Agent IT Support System
## Design, Implementation, Testing & Scaling Document

---

## 1. Problem Definition

**Context:** A 1,000-employee organization where IT analysts spend up to 60% of their time on repetitive, low-complexity support tickets — password resets, WiFi troubleshooting, VPN drops, and software errors. These requests create 4-hour average wait times and cost ~$28 per manual ticket.

**Goal:** Build a multi-agent AI system that resolves the top-5 high-volume IT support categories automatically, reducing manual ticket volume by ≥30% while maintaining a ≥80% first-contact resolution rate.

**Success Metrics:**
| Metric | Target | Achieved |
|--------|--------|----------|
| Intent classification accuracy | ≥ 80% | **100%** |
| Average response latency | ≤ 5,000 ms | **0.4 ms** |
| Escalation accuracy | ≥ 80% | **100%** |
| Test case pass rate | ≥ 80% | **9/9 (100%)** |

---

## 2. Agent Architecture

### 2.1 Agent Roles

```
End User
   │
   ▼
┌─────────────────────┐
│    IntakeAgent       │  Classifies intent (6 categories), extracts entities
│    (Rule-based NLP)  │  (device, application, location)
└──────────┬──────────┘
           │ AgentState
           ▼
┌─────────────────────┐
│   KnowledgeAgent     │  Searches VectorKnowledgeBase with FAISS
│   (RAG Retrieval)    │  Returns top-3 context chunks
└──────────┬──────────┘
           │ + retrieved_context
           ▼
┌─────────────────────┐
│   WorkflowAgent      │  Executes MCP tools:
│   (Automation Layer) │  reset_password, unlock_account, create_ticket,
│                     │  check_vpn_logs, check_system_logs
└──────────┬──────────┘
           │ + automated_result, escalation_needed
           ▼
┌─────────────────────┐
│  EscalationAgent     │  Rules: high-risk intents (vpn, account_locked),
│  (Routing Logic)     │  broad-impact language, workflow flags
└──────────┬──────────┘
           │ + escalation_reason
           ▼
┌─────────────────────┐
│   ResponseAgent      │  Composes grounded response using retrieved
│   (Response Synthesis)│  context + tool results + escalation status
└──────────┬──────────┘
           │ final_response
           ▼
        End User
```

### 2.2 Intent Categories

| Intent | Trigger Patterns | Workflow Action | Escalates? |
|--------|-----------------|-----------------|-----------|
| `password_reset` | "forgot password", "can't log in", "expired" | `reset_password()` | No |
| `account_locked` | "account locked", "MFA failed", "SSO error" | `unlock_account()` | Always |
| `wifi_troubleshooting` | "wifi", "no internet", "network down" | `create_ticket()` if broad | If broad impact |
| `vpn_issue` | "vpn", "remote access" | `check_vpn_logs()` | Always |
| `software_issue` | "crash", "Office", "Teams", "install" | `create_ticket()` | No |
| `ticket_request` | "ticket", "escalate", "open case" | `create_ticket()` | Yes |

### 2.3 AgentState Schema

```python
class AgentState(TypedDict, total=False):
    user_id: str                        # Employee identifier
    user_message: str                   # Raw input text
    intent: str                         # Classified category
    confidence: int                     # Number of pattern matches
    entities: Dict[str, Any]            # device, application, location
    retrieved_context: List[str]        # RAG-retrieved knowledge chunks
    proposed_actions: List[Dict]        # MCP tool calls + results
    automated_result: Dict[str, Any]    # Last tool output
    escalation_needed: bool             # Human routing flag
    escalation_reason: Optional[str]    # Reason for escalation
    final_response: str                 # User-facing answer
    trace: List[str]                    # Per-agent audit log
```

---

## 3. RAG Integration

### 3.1 Pipeline

```
User Query → sentence-transformers encode → FAISS IndexFlatIP search
         → cosine similarity top-k=3 → DocumentChunk retrieval
         → inject into ResponseAgent context
```

### 3.2 Embedding Model

- **Model:** `all-MiniLM-L6-v2` (sentence-transformers)
- **Dimensions:** 384
- **Index type:** `faiss.IndexFlatIP` (inner product = cosine on normalized vectors)
- **Fallback:** Lexical overlap scoring when `sentence-transformers` / `faiss-cpu` unavailable

### 3.3 Knowledge Base

| File | Chunks | Topics |
|------|--------|--------|
| `wifi_network_troubleshooting.txt` | 10 | WiFi connection, signal, auth, VPN, wired |
| `password_policy.txt` | 4 | Password reset workflow, lockout, identity verification |
| `software_troubleshooting.txt` | 6 | App crashes, Office repair, Teams/Zoom, licenses |
| `account_access.txt` | 7 | Account lockout, MFA, SSO, onboarding, email quotas |

### 3.4 Why RAG vs. Pure LLM

| Factor | Pure LLM | RAG (our approach) |
|--------|----------|-------------------|
| Hallucination risk | High | Low — grounded in docs |
| Domain accuracy | Generic | Company-specific procedures |
| Updatability | Requires fine-tuning | Update docs, re-index |
| Privacy | Risk of leaking training data | Controlled retrieval |

---

## 4. MCP Tool Layer

### 4.1 Design Philosophy

The `MCPToolRegistry` implements a **Model Context Protocol-style** abstraction: all tools are registered under a single interface (`registry.call(tool_name, **kwargs)`). This mirrors how real MCP servers standardize tool access, making it trivial to replace simulated tools with live integrations.

### 4.2 Tool Catalog

| Tool | Target System | Returns |
|------|------------|---------|
| `reset_password` | Okta / Azure AD | Reset link status, expiry |
| `unlock_account` | Active Directory | Unlock status, human confirm flag |
| `create_ticket` | ServiceNow / Jira | Ticket ID, priority, title |
| `check_vpn_logs` | Cisco AnyConnect | Disconnect pattern, recommendation |
| `check_system_logs` | Windows Event Log | Error codes, warnings |

### 4.3 Production Integration Path

```python
# Today (simulated)
registry.call("create_ticket", title="WiFi incident", priority="high")

# Production (real MCP server — zero agent code change)
# MCP server URL registered in config → same interface
registry.call("create_ticket", title="WiFi incident", priority="high")
```

---

## 5. API

### 5.1 Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health check |
| `POST` | `/support` | Submit support request |

### 5.2 Request / Response

```json
POST /support
{
  "user_id": "jdoe",
  "message": "My WiFi says connected but I have no internet"
}

Response:
{
  "response": "Here are the recommended WiFi troubleshooting steps: ...",
  "intent": "wifi_troubleshooting",
  "retrieved_context": ["If a user is connected..."],
  "automated_result": {},
  "trace": [
    "IntakeAgent classified intent as 'wifi_troubleshooting' (confidence=2)",
    "KnowledgeAgent retrieved 3 knowledge chunks",
    "WorkflowAgent executed 0 automated action(s)",
    "EscalationAgent: escalation_needed=False",
    "ResponseAgent composed final response"
  ]
}
```

---

## 6. Testing

### 6.1 Test Suite Summary

| File | Test Count | Coverage |
|------|-----------|----------|
| `tests/test_orchestrator.py` | 7 | Intent, escalation, actions, trace |
| `tests/test_api.py` | 2 | HTTP health, support endpoint |
| `scripts/evaluate.py` | 9 scenarios | Accuracy, latency, escalation |

### 6.2 Evaluation Results

```
Intent accuracy  : 100.0%  (9/9)
Escalation accuracy: 100.0%  (4/4 escalations predicted correctly)
Avg response latency: 0.40 ms
P95 response latency: 2.05 ms
Target: intent >= 80%: PASS ✓
Target: avg lat < 5000ms: PASS ✓
```

### 6.3 Test Scenarios

| # | Message | Expected Intent | Escalation |
|---|---------|----------------|-----------|
| 1 | I forgot my password | password_reset | No |
| 2 | I can't log in — password expired | password_reset | No |
| 3 | Account locked after failed attempts | account_locked | Yes |
| 4 | MFA authenticator stopped working | account_locked | Yes |
| 5 | WiFi connected but no internet | wifi_troubleshooting | No |
| 6 | WiFi not working for everyone on floor | wifi_troubleshooting | Yes |
| 7 | VPN keeps disconnecting | vpn_issue | Yes |
| 8 | Teams crashes when joining meeting | software_issue | No |
| 9 | Outlook crashes immediately | software_issue | No |

---

## 7. Scaling Plan

### 7.1 Knowledge Base (Production)

| Current | Production |
|---------|-----------|
| FAISS in-memory | Pinecone / Weaviate / Chroma |
| Local `.txt` files | Confluence, SharePoint, Notion sync |
| Manual re-index | Event-driven re-indexing on doc update |

### 7.2 Agent Orchestration

| Current | Production |
|---------|-----------|
| Linear pipeline | LangGraph state machine with conditional routing |
| No memory | Conversation history via Redis |
| No observability | LangSmith traces, Prometheus metrics |

### 7.3 Security & Compliance

- Add SSO / OAuth2 authentication on the API gateway
- RBAC: agents only call tools the user is authorized for
- Audit logging: full `trace` array stored in immutable log store
- PII scrubbing before embedding user messages

### 7.4 Infrastructure

```
Single instance (demo)        Production
────────────────────          ──────────────────────────────
uvicorn local                 → K8s deployment (3+ replicas)
FAISS in-memory               → Pinecone (managed vector DB)
Simulated MCP tools           → Live MCP servers (Jira, Okta)
No auth                       → API gateway + SSO
No monitoring                 → Datadog / Grafana + alerting
```

---

## 8. Industry Vendor Comparison

### Glean (Enterprise AI Search)
- **What it does:** Unified AI search across Slack, Drive, Jira, Confluence. Uses proprietary connectors + vector search.
- **Agent layer:** Glean Agents automate multi-step workflows — equivalent to our Workflow + Escalation agents.
- **Our position:** Our project is an open-source, auditable prototype of the same RAG+agent architecture. Easier to customize, no vendor lock-in, and serves as a learning model for the pattern.

### ServiceNow (ITSM Platform)
- **What it does:** End-to-end IT service management — ticketing, CMDB, change management, AI-assisted routing.
- **AI layer:** "Now Assist" (GenAI) summarizes tickets, recommends solutions — mirrors our ResponseAgent.
- **MCP relevance:** ServiceNow's REST API is exactly what our `create_ticket` MCP tool simulates.
- **Our position:** Our system replicates the intake + knowledge + escalation pattern that powers ServiceNow's virtual agent, but in a lightweight form suitable for custom deployment or smaller organizations.

---

## 9. Trade-Off Analysis

| Decision | Choice | Rationale | Trade-Off |
|----------|--------|-----------|-----------|
| Embedding model | MiniLM-L6-v2 | Fast, no GPU required, good quality | Larger models (e.g., text-embedding-3) would improve recall |
| Vector DB | FAISS local | Zero dependencies for demo | Not persistent, not distributed |
| Intent classification | Regex patterns | Deterministic, explainable, fast | Lower coverage than a fine-tuned classifier |
| MCP layer | Simulated | Demo reliability, no external API keys needed | Not a live MCP server |
| Framework | Plain Python (no LangGraph) | Simpler to understand and present | Less flexible for complex branching workflows |

