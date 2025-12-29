"""Policy Evaluator - Rule-based execution control"""

import yaml
from pathlib import Path
from typing import Dict, Any, List


class PolicyEvaluator:
    """Evaluates execution requests against YAML policies"""

    def __init__(self, policy_dir: Path):
        self.policy_dir = policy_dir
        self.rules: List[Dict[str, Any]] = []
        self._load_policies()

    def _load_policies(self):
        """Load all YAML policy files"""
        for policy_file in self.policy_dir.glob("*.yaml"):
            with policy_file.open("r") as f:
                policy = yaml.safe_load(f)
                self.rules.extend(policy.get("rules", []))

    def evaluate(self, request_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate request against rules.

        Returns first matching rule decision.
        """
        for rule in self.rules:
            if self._matches(rule["condition"], request_metadata):
                return {
                    "decision": rule["action"],
                    "rule_id": rule["rule_id"],
                    "reason": rule["reason"],
                }

        # Default: allow if no rule matches
        return {
            "decision": "ALLOW",
            "rule_id": "default",
            "reason": "No matching policy",
        }

    def _matches(self, condition: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Check if metadata matches rule condition"""
        for key, expected_value in condition.items():
            if metadata.get(key) != expected_value:
                return False
        return True
