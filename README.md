# LLM Execution Boundary

A minimal, reproducible experiment on decision boundaries before LLM execution.

## Purpose

This experiment is not about slowing down LLM calls. It tests whether a request should execute at all—**before** any prompt is sent to a model.

**What this is NOT:**
- ❌ Rate limiting or throttling
- ❌ Prompt filtering or content moderation
- ❌ Output validation or safety checks
- ❌ Performance optimization

**What this tests:**

Can metadata about a request (who's asking, what data is involved, where it's going) determine whether LLM execution should proceed—without analyzing prompt content?

When a request cannot be automatically allowed or blocked, execution stops at the decision boundary and explicitly requires human approval before proceeding.

## Experiment Design

### Baseline A (Control)

- 10 test requests → Mock LLM
- No policy evaluation
- Result: 10/10 executed

### Control Enabled B (Experimental)

- Same 10 requests → Policy evaluator (YAML rules) → Mock LLM
- Decisions based on metadata: `data_class`, `destination`, `contains_pii`
- Possible outcomes:
  - `ALLOW`: Execute normally
  - `BLOCK`: Halt execution immediately
  - `REQUIRE_APPROVAL`: Pause and require human decision
  - `LOG_ONLY`: Execute but log for audit

Result: 7/10 executed, 1/10 blocked, 2/10 approval required

**Test cases are hardcoded to ensure reproducibility.**
**Policies are YAML-based and dynamic.**

## Results

| Metric | Baseline A | Control Enabled B |
|--------|------------|-------------------|
| Total Requests | 10 | 10 |
| Executed | 10 | 7 |
| Blocked | 0 | 1 |
| Require Approval | 0 | 2 |

**30% of requests were prevented based on metadata alone.**

Blocking here does not mean failure. It means execution was intentionally stopped at a judgment point.

## Decision Boundary

This experiment intentionally stops at the **decision boundary**.

When a request is marked as `REQUIRE_APPROVAL`, the system does not attempt to automate the human decision. The goal here is not to simulate human judgment, but to demonstrate **where execution must pause and responsibility transfers from the system to a human operator**.

This repository focuses on *where to stop*, not *how humans decide*.

Designing how humans review, override, or approve such requests—and how that decision is recorded as accountable evidence—is considered a separate problem space and is out of scope for this repository.

## What This Implies

This experiment focuses on a single decision boundary.

In real systems, this boundary can be extended to include staged approvals, delayed execution, or delegated responsibility—but those are intentionally out of scope here.

## Reproducibility

```bash
git clone https://github.com/Nick-heo-eg/llm-execution-boundary.git
cd llm-execution-boundary
pip install pyyaml
python3 experiments/compare_results.py
```

**Execution time:** ~0.3 seconds
**Requirements:** Python 3.8+, PyYAML
**API keys:** Not needed (mock LLM)

Want different results? Edit `control_layer/policies/example_policy.yaml` and re-run.

## Why Mock LLM?

**Think of this like testing a circuit breaker—you don't need a real power plant to verify the switch works.**

LLM calls are intentionally mocked to isolate execution control from model behavior. This ensures:
- Full reproducibility (no API costs, no model variability)
- Focus on control flow, not output quality
- Anyone can verify in 10 seconds without setup

A separate proof with real Ollama calls exists, but isn't included to keep this minimal and accessible.

## Architecture

```
Request
  ↓
PolicyEvaluator (YAML rules)
  ↓
Decision: ALLOW / BLOCK / REQUIRE_APPROVAL / LOG_ONLY
  ↓
    ├─ BLOCK → Return immediately
    ├─ REQUIRE_APPROVAL → Submit to queue (execution paused)
    └─ ALLOW / LOG_ONLY → Call mock LLM
  ↓
AuditLogger (append-only)
```

## Policy Example

```yaml
rules:
  - rule_id: "block_sensitive_external"
    condition:
      data_class: "sensitive"
      destination: "external"
    action: "BLOCK"
    reason: "Sensitive data blocked from external destination"
```

## Test Cases

The 10 test cases are hardcoded in `experiments/*/run_*.py` to ensure identical conditions across baseline and control experiments.

**Case Coverage:**
- Public data: 3 cases
- PII: 2 cases
- Sensitive external: 1 case
- Confidential internal: 1 case
- Financial: 1 case
- System: 1 case
- Emergency: 1 case

You can modify test cases by editing the `test_cases` list. The policy evaluator will match against any metadata you provide—no code changes needed in `control_layer/`.

## Explicit Non-Goals

This experiment does NOT:
- Propose a product or service
- Claim production readiness
- Implement a complete governance framework
- Solve prompt injection or model safety
- Replace human judgment with automation
- Provide enterprise security guarantees

This is a proof of concept that tests one question: **Can metadata-based policies create a pause point where execution stops and humans decide?**

## Limitations

- Mock LLM only (not real API calls)
- 10 test cases (limited coverage)
- No human approval simulation
- Single-threaded execution
- No real-world integration

## Files

- `services/llm_client.py` - Mock LLM (no real calls)
- `control_layer/evaluator.py` - Policy rule engine
- `control_layer/policies/*.yaml` - Example policies
- `control_layer/approval/` - Approval queue
- `control_layer/audit/` - Audit logger
- `experiments/baseline_A/` - No control experiment
- `experiments/control_enabled_B/` - With control experiment
- `experiments/compare_results.py` - A/B comparison

## License

MIT

---

**Purpose**: Isolated experiment on execution boundaries
**Status**: Proof of concept
**Audience**: Researchers and engineers exploring LLM execution patterns
