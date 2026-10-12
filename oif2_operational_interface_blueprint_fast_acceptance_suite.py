#!/usr/bin/env python3
from __future__ import annotations

import json
from copy import deepcopy

from ontology.oif2_operational_interface_blueprint import (
    OIF2OperationalInterfaceBlueprint,
)


def main() -> int:
    primitive = OIF2OperationalInterfaceBlueprint()

    baseline_inputs = {
        "mode": "audit",
        "nicegui_available": False,
        "ui_environment": "isolated_.venv-oif",
    }
    before = deepcopy(baseline_inputs)
    result = primitive.step(inputs=baseline_inputs, persist=False)

    assert baseline_inputs == before
    assert result["status"] == "OIF2_OPERATIONAL_INTERFACE_BLUEPRINT_READY"
    assert result["functional_scope_only"] is True
    assert result["architecture"]["shell"]["system_python_mutation_allowed"] is False
    assert result["permission_model"]["shell_execution_from_renderer"] is False
    assert result["permission_model"]["direct_persistence_from_renderer"] is False
    assert result["epistemic_invariants"]["consciousness_proven"] is False
    assert result["epistemic_invariants"]["functional_conclusion_only"] is True
    print("OIF2_0_FUNCTIONAL_OK")

    second = primitive.step(inputs=baseline_inputs, persist=False)
    assert json.dumps(result, sort_keys=True) == json.dumps(second, sort_keys=True)
    result["architecture"]["layers"].append("mutation")
    third = primitive.step(inputs=baseline_inputs, persist=False)
    assert "mutation" not in third["architecture"]["layers"]
    print("OIF2_0_DETERMINISM_AND_ISOLATION_OK")

    degraded = primitive.step(inputs={"mode": "unsupported"}, persist=False)
    assert degraded["requested_mode"] == "audit"
    assert degraded["degraded"] is True
    assert degraded["degradation_reason"] == "unsupported_mode_fell_back_to_audit"

    try:
        primitive.step(inputs=[], persist=False)
    except TypeError:
        pass
    else:
        raise AssertionError("non-mapping input must fail")

    try:
        primitive.step(inputs={}, persist=True)
    except ValueError:
        pass
    else:
        raise AssertionError("persist=True must fail closed")
    print("OIF2_0_DEGRADATION_AND_FAIL_CLOSED_OK")

    zones = third["architecture"]["zones"]
    assert {"overview", "runtime", "experiments", "science", "memory", "governance", "system"} <= set(zones)
    assert third["anti_closure_constraints"]["retain_cli_and_non_ui_access"] is True
    assert third["anti_closure_constraints"]["support_replaceable_frontends"] is True
    print("OIF2_0_NON_REGRESSION_CONTRACT_OK")

    print("OIF2_0_FAST_ACCEPTANCE_ALL_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
