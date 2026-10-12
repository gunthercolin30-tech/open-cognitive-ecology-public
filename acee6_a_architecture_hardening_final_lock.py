from acee6_a_architecture_hardening_suite import main as suite_main
from acee6_a_hardening_contract import BOUNDED_LOOP_POLICY, PROHIBITED_LOOPS, QUARANTINE_STATES


def main():
    suite_main()
    assert QUARANTINE_STATES == {"ROLLBACK_FAILED", "STATE_CORRUPTED"}
    assert "unbounded_test_retry" in PROHIBITED_LOOPS
    assert all(policy["max_attempts"] <= 2 for policy in BOUNDED_LOOP_POLICY.values())
    print("ACEE6_A2_ARCHITECTURE_HARDENING_FINAL_LOCK_OK")


if __name__ == "__main__":
    main()
