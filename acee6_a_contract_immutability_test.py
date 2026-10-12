from __future__ import annotations

from copy import deepcopy

import acee6_a_hardening_contract as hardening
import acee6_test_requirements_registry as registry
import acee6_transaction_state_contract as transaction


def main():
    requirements_before = deepcopy(registry.TEST_REQUIREMENTS)
    transitions_before = deepcopy(transaction.ALLOWED_TRANSITIONS)
    loops_before = deepcopy(hardening.BOUNDED_LOOP_POLICY)

    derived_requirements = [dict(item) for item in registry.TEST_REQUIREMENTS]
    derived_requirements[0]["severity"] = "medium"
    derived_transitions = {key: set(value) for key, value in transaction.ALLOWED_TRANSITIONS.items()}
    derived_transitions["RECEIVED"].add("COMMITTED")
    derived_loops = deepcopy(hardening.BOUNDED_LOOP_POLICY)
    derived_loops["transient_infrastructure_retry"]["max_attempts"] = 99

    assert registry.TEST_REQUIREMENTS == requirements_before
    assert transaction.ALLOWED_TRANSITIONS == transitions_before
    assert hardening.BOUNDED_LOOP_POLICY == loops_before
    assert isinstance(registry.TEST_REQUIREMENTS, tuple)
    assert all(isinstance(value, frozenset) for value in transaction.ALLOWED_TRANSITIONS.values())
    print("ACEE6_A_CONTRACT_IMMUTABILITY_OK")


if __name__ == "__main__":
    main()
