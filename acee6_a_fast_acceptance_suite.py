from __future__ import annotations

from acee6_test_requirements_registry import TEST_REQUIREMENTS, registry_summary
from acee6_transaction_state_contract import SUCCESS_MARKER, validate_transition_path


def main():
    assert len(TEST_REQUIREMENTS) >= 120
    assert registry_summary()["critical_count"] >= 80
    assert SUCCESS_MARKER == "ACEE_INSTALLATION_EXECUTION_COMPLETE"
    assert validate_transition_path((
        "RECEIVED", "ADMISSIBLE", "PREPARING", "PREPARED", "WRITING",
        "WRITTEN", "COMPILING", "COMPILED", "UPDATING_METADATA",
        "METADATA_UPDATED", "TESTING", "VALIDATING_GLOBAL", "COMMITTING",
        "COMMITTED",
    ))
    print("ACEE6_A_FAST_ACCEPTANCE_OK")


if __name__ == "__main__":
    main()
