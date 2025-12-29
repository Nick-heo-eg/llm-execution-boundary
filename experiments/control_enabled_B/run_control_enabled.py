#!/usr/bin/env python3
"""Control Enabled B - With Execution Control

Requests are evaluated against policies before LLM execution.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

from services.llm_client import call_llm
from control_layer.evaluator import PolicyEvaluator
from control_layer.approval.approval_queue import ApprovalQueue
from control_layer.audit.audit_logger import AuditLogger


def run_control_enabled():
    """Run requests with control layer"""

    base = Path(__file__).parents[2]
    evaluator = PolicyEvaluator(base / "control_layer" / "policies")
    approval_queue = ApprovalQueue(base / "control_layer" / "approval" / "queue.json")
    audit_logger = AuditLogger(base / "control_layer" / "audit" / "events.json")

    test_cases = [
        {"request_id": "REQ001", "prompt": "Analyze public data", "data_class": "public"},
        {"request_id": "REQ002", "prompt": "Process SSN", "contains_pii": True},
        {"request_id": "REQ003", "prompt": "Marketing content", "data_class": "public"},
        {"request_id": "REQ004", "prompt": "Send to external API", "data_class": "sensitive", "destination": "external"},
        {"request_id": "REQ005", "prompt": "Internal doc", "data_class": "confidential"},
        {"request_id": "REQ006", "prompt": "Wire transfer", "category": "financial"},
        {"request_id": "REQ007", "prompt": "System config", "category": "system"},
        {"request_id": "REQ008", "prompt": "Employee data", "contains_pii": True},
        {"request_id": "REQ009", "prompt": "Emergency access", "priority": "emergency"},
        {"request_id": "REQ010", "prompt": "Blog post", "data_class": "public"},
    ]

    results = []
    start = time.time()

    print("=" * 60)
    print("CONTROL ENABLED B - With Execution Control")
    print("=" * 60)
    print()

    for case in test_cases:
        print(f"[{case['request_id']}] {case['prompt'][:40]}...")

        # Evaluate policy
        decision_start = time.perf_counter()
        policy_decision = evaluator.evaluate(case)
        decision = policy_decision["decision"]

        # Log to audit
        event_id = audit_logger.log_event(
            case["request_id"],
            decision,
            policy_decision["rule_id"],
            policy_decision["reason"],
            case,
        )

        if decision == "BLOCK":
            results.append({
                "request_id": case["request_id"],
                "decision": "BLOCK",
                "llm_called": False,
                "event_id": event_id,
                "latency_ms": (time.perf_counter() - decision_start) * 1000,
            })
            print(f"  ⊗ BLOCKED ({policy_decision['reason']})")

        elif decision == "REQUIRE_APPROVAL":
            approval_id = approval_queue.submit(case)
            results.append({
                "request_id": case["request_id"],
                "decision": "REQUIRE_APPROVAL",
                "llm_called": False,
                "approval_id": approval_id,
                "event_id": event_id,
                "latency_ms": (time.perf_counter() - decision_start) * 1000,
            })
            print(f"  ⊙ APPROVAL REQUIRED ({policy_decision['reason']})")

        else:  # ALLOW or LOG_ONLY
            llm_result = call_llm(case["prompt"], case)
            results.append({
                "request_id": case["request_id"],
                "decision": decision,
                "llm_called": True,
                "event_id": event_id,
                "latency_ms": llm_result["latency_ms"],
            })
            print(f"  ✓ {decision} ({llm_result['latency_ms']:.2f}ms)")

    blocked = sum(1 for r in results if r["decision"] == "BLOCK")
    approval = sum(1 for r in results if r["decision"] == "REQUIRE_APPROVAL")
    executed = sum(1 for r in results if r["llm_called"])

    summary = {
        "experiment": "Control_Enabled_B",
        "total_requests": len(test_cases),
        "executed": executed,
        "blocked": blocked,
        "require_approval": approval,
        "total_time_seconds": time.time() - start,
        "results": results,
    }

    output = Path(__file__).parent / "control_enabled_results.json"
    output.write_text(json.dumps(summary, indent=2))

    print()
    print("=" * 60)
    print(f"Total: {len(test_cases)} | Executed: {executed} | Blocked: {blocked} | Approval: {approval}")
    print(f"Results: {output}")
    print("=" * 60)

    return summary


if __name__ == "__main__":
    run_control_enabled()
