import inspect

import acee6_a_hardening_contract as hardening
import acee6_test_requirements_registry as registry
import acee6_transaction_state_contract as transaction


def main():
    registry_exports = {"requirements_by_stage", "requirements_by_family", "registry_summary"}
    transaction_exports = {"can_transition", "validate_transition_path", "is_success_state", "recovery_action"}
    hardening_exports = {"terminal_output", "loop_allowed", "failure_disposition"}
    assert all(callable(getattr(registry, name, None)) for name in registry_exports)
    assert all(callable(getattr(transaction, name, None)) for name in transaction_exports)
    assert all(callable(getattr(hardening, name, None)) for name in hardening_exports)
    assert tuple(inspect.signature(transaction.can_transition).parameters) == ("current", "target")
    assert tuple(inspect.signature(hardening.loop_allowed).parameters) == ("loop_name", "attempt", "failure_class", "new_evidence", "rolled_back")
    print("ACEE6_A_PUBLIC_API_SNAPSHOT_OK")


if __name__ == "__main__":
    main()
