from __future__ import annotations

"""ACEE6 transaction-state contract, without installation side effects."""

PUBLIC_SCHEMA_VERSION = "1.0.0"
PRIMITIVE = "ACEE6_TRANSACTION_STATE_CONTRACT"

STATES = (
    "RECEIVED",
    "REJECTED",
    "ADMISSIBLE",
    "PREPARING",
    "PREPARED",
    "WRITING",
    "WRITTEN",
    "COMPILING",
    "COMPILED",
    "UPDATING_METADATA",
    "METADATA_UPDATED",
    "TESTING",
    "VALIDATING_GLOBAL",
    "COMMITTING",
    "COMMITTED",
    "ROLLBACK_REQUIRED",
    "ROLLING_BACK",
    "ROLLED_BACK",
    "ROLLBACK_FAILED",
    "STATE_CORRUPTED",
)

TERMINAL_STATES = frozenset({
    "REJECTED", "COMMITTED", "ROLLED_BACK", "ROLLBACK_FAILED", "STATE_CORRUPTED"
})

SUCCESS_STATE = "COMMITTED"
SUCCESS_MARKER = "ACEE_INSTALLATION_EXECUTION_COMPLETE"

ALLOWED_TRANSITIONS = {
    "RECEIVED": frozenset({"REJECTED", "ADMISSIBLE", "STATE_CORRUPTED"}),
    "ADMISSIBLE": frozenset({"PREPARING", "REJECTED", "STATE_CORRUPTED"}),
    "PREPARING": frozenset({"PREPARED", "ROLLBACK_REQUIRED", "STATE_CORRUPTED"}),
    "PREPARED": frozenset({"WRITING", "ROLLBACK_REQUIRED", "STATE_CORRUPTED"}),
    "WRITING": frozenset({"WRITTEN", "ROLLBACK_REQUIRED", "STATE_CORRUPTED"}),
    "WRITTEN": frozenset({"COMPILING", "ROLLBACK_REQUIRED", "STATE_CORRUPTED"}),
    "COMPILING": frozenset({"COMPILED", "ROLLBACK_REQUIRED", "STATE_CORRUPTED"}),
    "COMPILED": frozenset({"UPDATING_METADATA", "ROLLBACK_REQUIRED", "STATE_CORRUPTED"}),
    "UPDATING_METADATA": frozenset({"METADATA_UPDATED", "ROLLBACK_REQUIRED", "STATE_CORRUPTED"}),
    "METADATA_UPDATED": frozenset({"TESTING", "ROLLBACK_REQUIRED", "STATE_CORRUPTED"}),
    "TESTING": frozenset({"VALIDATING_GLOBAL", "ROLLBACK_REQUIRED", "STATE_CORRUPTED"}),
    "VALIDATING_GLOBAL": frozenset({"COMMITTING", "ROLLBACK_REQUIRED", "STATE_CORRUPTED"}),
    "COMMITTING": frozenset({"COMMITTED", "ROLLBACK_REQUIRED", "STATE_CORRUPTED"}),
    "ROLLBACK_REQUIRED": frozenset({"ROLLING_BACK", "STATE_CORRUPTED"}),
    "ROLLING_BACK": frozenset({"ROLLED_BACK", "ROLLBACK_FAILED", "STATE_CORRUPTED"}),
    "REJECTED": frozenset(),
    "COMMITTED": frozenset(),
    "ROLLED_BACK": frozenset(),
    "ROLLBACK_FAILED": frozenset(),
    "STATE_CORRUPTED": frozenset(),
}

RECOVERY_POLICY = {
    "RECEIVED": "REVALIDATE",
    "ADMISSIBLE": "REVALIDATE",
    "PREPARING": "ROLLBACK_REQUIRED",
    "PREPARED": "ROLLBACK_REQUIRED",
    "WRITING": "ROLLBACK_REQUIRED",
    "WRITTEN": "ROLLBACK_REQUIRED",
    "COMPILING": "ROLLBACK_REQUIRED",
    "COMPILED": "ROLLBACK_REQUIRED",
    "UPDATING_METADATA": "ROLLBACK_REQUIRED",
    "METADATA_UPDATED": "ROLLBACK_REQUIRED",
    "TESTING": "ROLLBACK_REQUIRED",
    "VALIDATING_GLOBAL": "ROLLBACK_REQUIRED",
    "COMMITTING": "ROLLBACK_REQUIRED",
    "COMMITTED": "ALREADY_COMMITTED",
    "ROLLBACK_REQUIRED": "ROLLBACK_REQUIRED",
    "ROLLING_BACK": "ROLLBACK_REQUIRED",
    "ROLLED_BACK": "ALREADY_ROLLED_BACK",
    "ROLLBACK_FAILED": "MANUAL_RECOVERY_REQUIRED",
    "REJECTED": "REJECTED",
    "STATE_CORRUPTED": "MANUAL_RECOVERY_REQUIRED",
}

MANDATORY_COMMIT_EVIDENCE = (
    "transaction_id",
    "proposal_id",
    "acee5_manifest_hash",
    "pre_installation_hashes",
    "backup_hashes",
    "post_installation_hashes",
    "compilation_results",
    "test_results",
    "global_validation_report_hash",
    "rollback_performed",
    "previous_transaction_hash",
    "result_hash",
)

EPISTEMIC_GUARDS = {
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "collective_consciousness_proven": False,
    "collective_subjectivity_proven": False,
    "collective_qualia_proven": False,
    "collective_phenomenology_proven": False,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}


def can_transition(current, target):
    return target in ALLOWED_TRANSITIONS.get(current, frozenset())


def validate_transition_path(path):
    sequence = tuple(path)
    if not sequence or sequence[0] != "RECEIVED":
        return False
    if any(state not in STATES for state in sequence):
        return False
    return all(can_transition(a, b) for a, b in zip(sequence, sequence[1:]))


def is_success_state(state):
    return state == SUCCESS_STATE


def recovery_action(state):
    return RECOVERY_POLICY.get(state, "STATE_CORRUPTED")
