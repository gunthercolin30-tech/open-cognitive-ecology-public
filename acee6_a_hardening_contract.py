from __future__ import annotations

"""Additional ACEE6-A architecture, loop, output and dependency contracts."""

PUBLIC_SCHEMA_VERSION = "1.0.0"
PRIMITIVE = "ACEE6_A_HARDENING_CONTRACT"

INTERNAL_SUBSTAGES = {
    "B1": "manifest admission",
    "B2": "dry-run and predictive diff",
    "F1": "candidate-targeted validation",
    "F2": "global validation and evidence binding",
    "G1": "fault injection",
    "G2": "rollback verification and quarantine",
    "I1": "restart reconciliation",
    "I2": "bounded replay and idempotence",
    "J1": "final evidence and hash chain",
    "J2": "quarantine, escalation and diagnostics",
}

TERMINAL_OUTPUTS = {
    "REJECTED": "ACEE_INSTALLATION_REJECTED",
    "COMMITTED": "ACEE_INSTALLATION_EXECUTION_COMPLETE",
    "ROLLED_BACK": "ACEE_INSTALLATION_ROLLED_BACK",
    "ROLLBACK_FAILED": "ACEE_INSTALLATION_ROLLBACK_FAILED",
    "STATE_CORRUPTED": "ACEE_INSTALLATION_STATE_CORRUPTED",
}

QUARANTINE_STATES = frozenset({"ROLLBACK_FAILED", "STATE_CORRUPTED"})

BOUNDED_LOOP_POLICY = {
    "admission_revalidation": {
        "max_attempts": 1,
        "allowed_failure_classes": ("stale_external_evidence",),
        "requires_new_evidence": True,
        "requires_rollback_before_retry": False,
    },
    "transient_infrastructure_retry": {
        "max_attempts": 2,
        "allowed_failure_classes": (
            "lock_timeout",
            "temporary_resource_unavailable",
            "transient_process_timeout",
        ),
        "requires_new_evidence": False,
        "requires_rollback_before_retry": True,
    },
    "rollback_verification": {
        "max_attempts": 1,
        "allowed_failure_classes": ("restoration_verification_mismatch",),
        "requires_new_evidence": False,
        "requires_rollback_before_retry": False,
    },
    "restart_reconciliation": {
        "max_attempts": 1,
        "allowed_failure_classes": ("recoverable_journal_divergence",),
        "requires_new_evidence": False,
        "requires_rollback_before_retry": False,
    },
}

PROHIBITED_LOOPS = frozenset({
    "automatic_code_repair",
    "automatic_candidate_regeneration",
    "unbounded_test_retry",
    "retry_after_semantic_test_failure",
    "retry_after_constitutional_failure",
    "silent_rollback_retry",
})

FAILURE_DISPOSITION = {
    "manifest_or_contract_failure": "REJECT",
    "constitutional_failure": "REJECT",
    "semantic_test_failure_before_mutation": "REJECT",
    "semantic_test_failure_after_mutation": "ROLLBACK",
    "compilation_failure_after_mutation": "ROLLBACK",
    "global_validation_failure_after_mutation": "ROLLBACK",
    "transient_infrastructure_failure_before_mutation": "BOUNDED_RETRY",
    "transient_infrastructure_failure_after_mutation": "ROLLBACK_THEN_BOUNDED_RETRY",
    "rollback_verification_failure": "QUARANTINE",
    "journal_corruption": "QUARANTINE",
    "state_corruption": "QUARANTINE",
}

# Representative cross-family prerequisites. Every identifier is resolved
# against acee6_test_requirements_registry.py by the dependency-graph test.
REQUIREMENT_DEPENDENCIES = {
    "ACEE6-MAN-002": ("ACEE6-MAN-001",),
    "ACEE6-MAN-008": ("ACEE6-MAN-003", "ACEE6-MAN-006", "ACEE6-MAN-007"),
    "ACEE6-PATH-004": ("ACEE6-PATH-002", "ACEE6-PATH-003"),
    "ACEE6-PLAN-001": ("ACEE6-MAN-008",),
    "ACEE6-BAK-002": ("ACEE6-BAK-001",),
    "ACEE6-WRITE-001": ("ACEE6-BAK-002",),
    "ACEE6-COMP-001": ("ACEE6-WRITE-002",),
    "ACEE6-REG-001": ("ACEE6-COMP-001",),
    "ACEE6-VAL-001": ("ACEE6-COMP-003",),
    "ACEE6-GLOB-001": ("ACEE6-VAL-003", "ACEE6-VAL-005", "ACEE6-VAL-006"),
    "ACEE6-RB-005": ("ACEE6-RB-001", "ACEE6-RB-002", "ACEE6-RB-003"),
    "ACEE6-ATOM-001": ("ACEE6-RB-005",),
}


def terminal_output(state):
    return TERMINAL_OUTPUTS.get(state)


def loop_allowed(loop_name, attempt, failure_class, *, new_evidence=False, rolled_back=False):
    policy = BOUNDED_LOOP_POLICY.get(loop_name)
    if policy is None or loop_name in PROHIBITED_LOOPS:
        return False
    if not isinstance(attempt, int) or isinstance(attempt, bool):
        return False
    if attempt < 1 or attempt > policy["max_attempts"]:
        return False
    if failure_class not in policy["allowed_failure_classes"]:
        return False
    if policy["requires_new_evidence"] and not new_evidence:
        return False
    if policy["requires_rollback_before_retry"] and not rolled_back:
        return False
    return True


def failure_disposition(failure_class):
    return FAILURE_DISPOSITION.get(failure_class, "QUARANTINE")
