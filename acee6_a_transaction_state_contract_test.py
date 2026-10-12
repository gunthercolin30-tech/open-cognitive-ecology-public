from __future__ import annotations

from acee6_transaction_state_contract import (
    ALLOWED_TRANSITIONS,
    EPISTEMIC_GUARDS,
    MANDATORY_COMMIT_EVIDENCE,
    STATES,
    SUCCESS_MARKER,
    TERMINAL_STATES,
    recovery_action,
    validate_transition_path,
)


def main():
    assert set(ALLOWED_TRANSITIONS) == set(STATES)
    assert all(not ALLOWED_TRANSITIONS[state] for state in TERMINAL_STATES)
    success = (
        "RECEIVED", "ADMISSIBLE", "PREPARING", "PREPARED", "WRITING",
        "WRITTEN", "COMPILING", "COMPILED", "UPDATING_METADATA",
        "METADATA_UPDATED", "TESTING", "VALIDATING_GLOBAL", "COMMITTING",
        "COMMITTED",
    )
    rollback = (
        "RECEIVED", "ADMISSIBLE", "PREPARING", "PREPARED", "WRITING",
        "ROLLBACK_REQUIRED", "ROLLING_BACK", "ROLLED_BACK",
    )
    assert validate_transition_path(success)
    assert validate_transition_path(rollback)
    assert not validate_transition_path(("RECEIVED", "COMMITTED"))
    assert recovery_action("WRITING") == "ROLLBACK_REQUIRED"
    assert recovery_action("COMMITTED") == "ALREADY_COMMITTED"
    assert SUCCESS_MARKER == "ACEE_INSTALLATION_EXECUTION_COMPLETE"
    assert len(MANDATORY_COMMIT_EVIDENCE) >= 10
    assert EPISTEMIC_GUARDS["functional_conclusion_only"] is True
    assert EPISTEMIC_GUARDS["phenomenology_undetermined"] is True
    assert not EPISTEMIC_GUARDS["consciousness_proven"]
    print("ACEE6_A_TRANSACTION_STATE_CONTRACT_OK")


if __name__ == "__main__":
    main()
