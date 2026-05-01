# Architecture and Design Notes

## Problem Definition
The system addresses repetitive IT support requests that consume analyst time and create long wait times for end users.

## Why Multi-Agent
A multi-agent design separates responsibilities:
- **Intake Agent**: classifies the issue and extracts simple entities
- **Knowledge Agent**: retrieves context from internal documentation using RAG
- **Workflow Agent**: executes approved automations using an MCP-style tool layer
- **Escalation Agent**: flags broader outages or unresolved issues
- **Response Agent**: composes a grounded, user-friendly answer

## Why RAG
Without retrieval, a chatbot may hallucinate troubleshooting steps. With retrieval, responses are grounded in internal support documentation.

## Why MCP-Style Tooling
Tool calls use one interface, which makes it easier to swap in real tools such as Jira, GitHub, ServiceNow, or Okta later.

## Trade-Offs
- A simple starter uses local files instead of a cloud vector DB.
- The MCP layer is simulated, not a live MCP server.
- Automation is intentionally limited to safe workflows for demo reliability.
