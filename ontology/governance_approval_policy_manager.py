"""Governance Approval Policy Manager.

Provides a simple policy layer that allows autonomous actions to be
executed automatically, blocked, or routed through human approval.
Designed so approval requirements can be removed later by changing
configuration only.
"""

from copy import deepcopy


class GovernanceApprovalPolicyManager:
    PRIMITIVE_NAME = "GOVERNANCE_APPROVAL_POLICY_MANAGER"

    DEFAULT_POLICIES = {
        "storage_account_creation": "approval_required",
        "external_data_migration": "approval_required",
        "quota_removal": "approval_required",
    }

    VALID_MODES = {
        "approval_required",
        "auto_execute",
        "disabled",
    }

    def __init__(self, policies=None):
        self.policies = deepcopy(self.DEFAULT_POLICIES)
        if isinstance(policies, dict):
            for action, mode in policies.items():
                self.set_policy(action, mode)

    def set_policy(self, action, mode):
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid governance mode: {mode}")
        self.policies[str(action)] = mode
        return {
            "primitive": self.PRIMITIVE_NAME,
            "action": str(action),
            "mode": mode,
            "updated": True,
        }

    def get_policy(self, action):
        return self.policies.get(str(action), "approval_required")

    def evaluate_action(self, action, payload=None):
        action = str(action)
        mode = self.get_policy(action)

        if mode == "auto_execute":
            status = "approved"
            requires_human_approval = False
            can_execute = True
        elif mode == "disabled":
            status = "blocked"
            requires_human_approval = False
            can_execute = False
        else:
            status = "awaiting_human_approval"
            requires_human_approval = True
            can_execute = False

        return {
            "primitive": self.PRIMITIVE_NAME,
            "action": action,
            "mode": mode,
            "status": status,
            "requires_human_approval": requires_human_approval,
            "can_execute": can_execute,
            "can_be_fully_automated": True,
            "payload": payload,
        }

    def step(self, inputs):
        if not isinstance(inputs, dict):
            return {
                "primitive": self.PRIMITIVE_NAME,
                "error": "dict expected",
            }

        command = inputs.get("command", "evaluate")

        if command == "set_policy":
            return self.set_policy(
                inputs.get("action"),
                inputs.get("mode", "approval_required"),
            )

        if command == "get_policy":
            action = inputs.get("action")
            return {
                "primitive": self.PRIMITIVE_NAME,
                "action": action,
                "mode": self.get_policy(action),
            }

        return self.evaluate_action(
            inputs.get("action", "unknown_action"),
            inputs.get("payload"),
        )
