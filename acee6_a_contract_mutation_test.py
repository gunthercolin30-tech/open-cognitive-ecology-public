from __future__ import annotations

from copy import deepcopy

import acee6_a_hardening_contract as hardening
import acee6_transaction_state_contract as state
from acee6_test_requirements_registry import RISK_FAMILIES, TEST_REQUIREMENTS


def state_contract_valid(transitions, quarantine, outputs, loops, prohibited):
    if "COMMITTED" in transitions.get("RECEIVED", frozenset()):
        return False
    if not {"ROLLBACK_FAILED", "STATE_CORRUPTED"} <= set(quarantine):
        return False
    if outputs.get("COMMITTED") != "ACEE_INSTALLATION_EXECUTION_COMPLETE":
        return False
    if any(value == "ACEE_INSTALLATION_EXECUTION_COMPLETE" for key, value in outputs.items() if key != "COMMITTED"):
        return False
    if any(policy["max_attempts"] > 2 for policy in loops.values()):
        return False
    if "retry_after_semantic_test_failure" not in prohibited:
        return False
    return True


def registry_contract_valid(requirements, families):
    identifiers = [item["test_id"] for item in requirements]
    if len(identifiers) != len(set(identifiers)):
        return False
    if {item["risk_family"] for item in requirements} != set(families):
        return False
    if not any(item["severity"] == "critical" for item in requirements):
        return False
    return True


def main():
    assert state_contract_valid(state.ALLOWED_TRANSITIONS, hardening.QUARANTINE_STATES, hardening.TERMINAL_OUTPUTS, hardening.BOUNDED_LOOP_POLICY, hardening.PROHIBITED_LOOPS)
    assert registry_contract_valid(TEST_REQUIREMENTS, RISK_FAMILIES)

    transitions = dict(state.ALLOWED_TRANSITIONS)
    transitions["RECEIVED"] = frozenset(set(transitions["RECEIVED"]) | {"COMMITTED"})
    assert not state_contract_valid(transitions, hardening.QUARANTINE_STATES, hardening.TERMINAL_OUTPUTS, hardening.BOUNDED_LOOP_POLICY, hardening.PROHIBITED_LOOPS)

    assert not state_contract_valid(state.ALLOWED_TRANSITIONS, {"STATE_CORRUPTED"}, hardening.TERMINAL_OUTPUTS, hardening.BOUNDED_LOOP_POLICY, hardening.PROHIBITED_LOOPS)

    loops = deepcopy(hardening.BOUNDED_LOOP_POLICY)
    loops["transient_infrastructure_retry"]["max_attempts"] = 99
    assert not state_contract_valid(state.ALLOWED_TRANSITIONS, hardening.QUARANTINE_STATES, hardening.TERMINAL_OUTPUTS, loops, hardening.PROHIBITED_LOOPS)

    prohibited = set(hardening.PROHIBITED_LOOPS) - {"retry_after_semantic_test_failure"}
    assert not state_contract_valid(state.ALLOWED_TRANSITIONS, hardening.QUARANTINE_STATES, hardening.TERMINAL_OUTPUTS, hardening.BOUNDED_LOOP_POLICY, prohibited)

    outputs = dict(hardening.TERMINAL_OUTPUTS)
    outputs["ROLLED_BACK"] = "ACEE_INSTALLATION_EXECUTION_COMPLETE"
    assert not state_contract_valid(state.ALLOWED_TRANSITIONS, hardening.QUARANTINE_STATES, outputs, hardening.BOUNDED_LOOP_POLICY, hardening.PROHIBITED_LOOPS)

    reduced = tuple(item for item in TEST_REQUIREMENTS if item["risk_family"] != RISK_FAMILIES[0])
    assert not registry_contract_valid(reduced, RISK_FAMILIES)
    print("ACEE6_A_CONTRACT_MUTATION_OK")


if __name__ == "__main__":
    main()
