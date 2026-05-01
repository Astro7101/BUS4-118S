from __future__ import annotations

import os
import sys
import statistics
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.orchestrator import SupportOrchestrator

TEST_CASES = [
    # --- Password Reset ---
    {
        "user_id": "jdoe",
        "message": "I forgot my password and need a reset",
        "expected_intent": "password_reset",
        "expect_escalation": False,
    },
    {
        "user_id": "msmith",
        "message": "I can't log in — my password expired",
        "expected_intent": "password_reset",
        "expect_escalation": False,
    },
    # --- Account Locked ---
    {
        "user_id": "bwilson",
        "message": "My account is locked after too many failed attempts",
        "expected_intent": "account_locked",
        "expect_escalation": True,
    },
    {
        "user_id": "ljones",
        "message": "My MFA authenticator stopped working",
        "expected_intent": "account_locked",
        "expect_escalation": True,
    },
    # --- WiFi ---
    {
        "user_id": "jdoe",
        "message": "My WiFi says connected but I have no internet",
        "expected_intent": "wifi_troubleshooting",
        "expect_escalation": False,
    },
    {
        "user_id": "jdoe",
        "message": "WiFi is still not working for everyone on my floor",
        "expected_intent": "wifi_troubleshooting",
        "expect_escalation": True,
    },
    # --- VPN ---
    {
        "user_id": "jdoe",
        "message": "My VPN keeps disconnecting this morning",
        "expected_intent": "vpn_issue",
        "expect_escalation": True,
    },
    # --- Software ---
    {
        "user_id": "rlee",
        "message": "Microsoft Teams keeps crashing when I join a meeting",
        "expected_intent": "software_issue",
        "expect_escalation": False,
    },
    {
        "user_id": "rlee",
        "message": "Outlook won't open — it crashes immediately",
        "expected_intent": "software_issue",
        "expect_escalation": False,
    },
]


def main() -> None:
    orchestrator = SupportOrchestrator()
    latencies = []
    correct_intent = 0
    correct_escalation = 0

    print("=" * 80)
    print("MULTI-AGENT IT SUPPORT SYSTEM — EVALUATION REPORT")
    print("=" * 80)

    for i, case in enumerate(TEST_CASES, 1):
        start = time.perf_counter()
        state = orchestrator.handle(case["user_id"], case["message"])
        elapsed = (time.perf_counter() - start) * 1000
        latencies.append(elapsed)

        intent_ok = state.get("intent") == case["expected_intent"]
        esc_ok = state.get("escalation_needed", False) == case["expect_escalation"]

        if intent_ok:
            correct_intent += 1
        if esc_ok:
            correct_escalation += 1

        intent_icon = "✓" if intent_ok else "✗"
        esc_icon = "✓" if esc_ok else "✗"

        print(f"\n[{i}/{len(TEST_CASES)}] User: {case['user_id']}")
        print(f"  Message   : {case['message']}")
        print(f"  Intent    : {state.get('intent')} {intent_icon}  (expected: {case['expected_intent']})")
        print(f"  Escalation: {state.get('escalation_needed')} {esc_icon}  (expected: {case['expect_escalation']})")
        print(f"  Response  : {state.get('final_response', '')[:120]}...")
        print(f"  Latency   : {elapsed:.2f} ms")
        print(f"  Trace     : {' → '.join(state.get('trace', []))}")

    n = len(TEST_CASES)
    intent_acc = correct_intent / n
    esc_acc = correct_escalation / n
    avg_lat = statistics.mean(latencies)
    p95_lat = sorted(latencies)[int(0.95 * n)]

    print("\n" + "=" * 80)
    print("SUMMARY METRICS")
    print("=" * 80)
    print(f"  Test cases run         : {n}")
    print(f"  Intent accuracy        : {intent_acc:.1%}  ({correct_intent}/{n})")
    print(f"  Escalation accuracy    : {esc_acc:.1%}  ({correct_escalation}/{n})")
    print(f"  Avg response latency   : {avg_lat:.2f} ms")
    print(f"  P95 response latency   : {p95_lat:.2f} ms")
    print(f"  Target: intent >= 80%  : {'PASS ✓' if intent_acc >= 0.80 else 'FAIL ✗'}")
    print(f"  Target: avg lat < 5000ms: {'PASS ✓' if avg_lat < 5000 else 'FAIL ✗'}")
    print("=" * 80)


if __name__ == "__main__":
    main()
