from src.core.orchestrator import SupportOrchestrator

orchestrator = SupportOrchestrator()


def test_password_reset_flow() -> None:
    state = orchestrator.handle("jdoe", "I forgot my password and need a reset")
    assert state["intent"] == "password_reset"
    assert "reset link sent" in state["final_response"]
    assert state["escalation_needed"] is False


def test_account_locked_flow() -> None:
    state = orchestrator.handle("bwilson", "My account is locked after too many failed attempts")
    assert state["intent"] == "account_locked"
    assert state["escalation_needed"] is True
    assert "unlocked" in state["final_response"].lower()


def test_wifi_troubleshooting_flow() -> None:
    state = orchestrator.handle("jdoe", "My WiFi says connected but I have no internet")
    assert state["intent"] == "wifi_troubleshooting"
    assert "troubleshooting steps" in state["final_response"]
    assert state["escalation_needed"] is False


def test_wifi_outage_escalates() -> None:
    state = orchestrator.handle("jdoe", "WiFi is still not working for everyone on my floor")
    assert state["intent"] == "wifi_troubleshooting"
    assert state["escalation_needed"] is True
    assert state["automated_result"].get("ticket_id", "").startswith("INC-")


def test_vpn_issue_escalates() -> None:
    state = orchestrator.handle("jdoe", "My VPN keeps disconnecting this morning")
    assert state["intent"] == "vpn_issue"
    assert state["escalation_needed"] is True
    assert "network team" in state["final_response"]


def test_software_issue_flow() -> None:
    state = orchestrator.handle("rlee", "Microsoft Teams keeps crashing when I join a meeting")
    assert state["intent"] == "software_issue"
    assert state["automated_result"].get("ticket_id", "").startswith("INC-")


def test_trace_populated() -> None:
    state = orchestrator.handle("jdoe", "I need to reset my password")
    trace = state.get("trace", [])
    assert len(trace) == 5  # one entry per agent
    assert any("IntakeAgent" in t for t in trace)
    assert any("KnowledgeAgent" in t for t in trace)
    assert any("WorkflowAgent" in t for t in trace)
    assert any("EscalationAgent" in t for t in trace)
    assert any("ResponseAgent" in t for t in trace)
