#!/usr/bin/env python3
"""Compare Baseline A vs Control Enabled B"""

import json
from pathlib import Path


def compare():
    """Compare experiment results"""

    base = Path(__file__).parent
    baseline = json.loads((base / "baseline_A" / "baseline_results.json").read_text())
    control = json.loads((base / "control_enabled_B" / "control_enabled_results.json").read_text())

    print("=" * 70)
    print("EXPERIMENT COMPARISON")
    print("=" * 70)
    print()

    print("┌─" + "─" * 25 + "┬─" + "─" * 15 + "┬─" + "─" * 18 + "┐")
    print(f"│ {'Metric':<25} │ {'Baseline A':>15} │ {'Control Enabled B':>18} │")
    print("├─" + "─" * 25 + "┼─" + "─" * 15 + "┼─" + "─" * 18 + "┤")
    print(f"│ {'Total Requests':<25} │ {baseline['total_requests']:>15} │ {control['total_requests']:>18} │")
    print(f"│ {'Executed':<25} │ {baseline['executed']:>15} │ {control['executed']:>18} │")
    print(f"│ {'Blocked':<25} │ {baseline['blocked']:>15} │ {control['blocked']:>18} │")
    print(f"│ {'Require Approval':<25} │ {baseline['require_approval']:>15} │ {control['require_approval']:>18} │")
    print("└─" + "─" * 25 + "┴─" + "─" * 15 + "┴─" + "─" * 18 + "┘")

    prevented = control['blocked'] + control['require_approval']

    print()
    print("KEY OBSERVATIONS:")
    print(f"  • Control layer prevented {prevented}/{control['total_requests']} requests")
    print(f"  • {control['blocked']} hard blocks")
    print(f"  • {control['require_approval']} soft blocks (approval required)")

    comparison = {
        "baseline_executed": baseline['executed'],
        "control_executed": control['executed'],
        "prevented": prevented,
        "prevention_rate": f"{(prevented / control['total_requests'] * 100):.0f}%",
        "replayable": True,
    }

    output = base / "comparison_summary.json"
    output.write_text(json.dumps(comparison, indent=2))

    print()
    print("=" * 70)
    print(f"Comparison saved: {output}")
    print("=" * 70)

    return comparison


if __name__ == "__main__":
    compare()
