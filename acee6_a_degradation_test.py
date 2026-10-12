from __future__ import annotations

from acee6_transaction_state_contract import recovery_action, validate_transition_path


def main():
    assert not validate_transition_path(())
    assert not validate_transition_path(("PREPARED", "WRITING"))
    assert not validate_transition_path(("RECEIVED", "ADMISSIBLE", "COMMITTED"))
    assert not validate_transition_path(("RECEIVED", "UNKNOWN"))
    assert recovery_action("UNKNOWN") == "STATE_CORRUPTED"
    print("ACEE6_A_DEGRADATION_OK")


if __name__ == "__main__":
    main()
