from __future__ import annotations

import importlib

from acee6_a_contract_snapshot import PUBLIC_CONTRACT


def main():
    for module_name, contract in PUBLIC_CONTRACT.items():
        module = importlib.import_module(module_name)
        for name in contract["constants"]:
            assert hasattr(module, name), (module_name, name)
        for name in contract["callables"]:
            assert callable(getattr(module, name, None)), (module_name, name)

    registry = importlib.import_module("acee6_test_requirements_registry")
    transaction = importlib.import_module("acee6_transaction_state_contract")
    hardening = importlib.import_module("acee6_a_hardening_contract")
    assert isinstance(registry.TEST_REQUIREMENTS, tuple)
    assert isinstance(registry.RISK_FAMILIES, tuple)
    assert isinstance(transaction.ALLOWED_TRANSITIONS, dict)
    assert isinstance(transaction.TERMINAL_STATES, frozenset)
    assert isinstance(hardening.QUARANTINE_STATES, frozenset)
    assert transaction.SUCCESS_MARKER == "ACEE_INSTALLATION_EXECUTION_COMPLETE"
    print("ACEE6_A_SCHEMA_BACKWARD_COMPATIBILITY_OK")


if __name__ == "__main__":
    main()
