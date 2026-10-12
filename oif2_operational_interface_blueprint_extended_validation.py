#!/usr/bin/env python3
"""Extended validation for OIF2-0 operational interface blueprint."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

ROOT = Path.home() / "open-cognitive-ecology"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ontology.oif2_operational_interface_blueprint import (  # noqa: E402
    OIF2OperationalInterfaceBlueprint,
)


EXPECTED_LAYERS = [
    "presentation",
    "view_models",
    "governed_application_services",
    "runtime_adapters",
    "persistence_and_audit",
]

EXPECTED_ZONES = {
    "overview",
    "runtime",
    "experiments",
    "science",
    "memory",
    "governance",
    "system",
}

EXPECTED_STATES = {
    "initializing",
    "ready",
    "degraded",
    "busy",
    "approval_required",
    "failed_closed",
    "stopped",
}

EXPECTED_SEQUENCE = [
    "OIF2-0 blueprint and contracts",
    "OIF2-1 isolated UI environment",
    "OIF2-2 read-only application shell",
    "OIF2-3 state and validation adapters",
    "OIF2-4 governed runtime controls",
    "OIF2-5 experiments and history",
    "OIF2-6 governance review workflows",
    "OIF2-7 packaging launcher and recovery",
    "OIF2-8 longitudinal validation and final lock",
]


def canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )


def snapshot_tree(root: Path) -> Dict[str, tuple[int, int]]:
    snapshot: Dict[str, tuple[int, int]] = {}
    if not root.exists():
        return snapshot
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        snapshot[str(path.relative_to(root))] = (
            stat.st_size,
            stat.st_mtime_ns,
        )
    return snapshot


def test_contract_completeness() -> None:
    primitive = OIF2OperationalInterfaceBlueprint()
    result = primitive.step(
        inputs={
            "mode": "audit",
            "nicegui_available": False,
            "ui_environment": "isolated_.venv-oif",
        },
        persist=False,
    )

    assert result["architecture"]["layers"] == EXPECTED_LAYERS
    assert set(result["architecture"]["zones"]) == EXPECTED_ZONES
    assert set(result["operational_states"]) == EXPECTED_STATES
    assert result["implementation_sequence"] == EXPECTED_SEQUENCE

    assert result["architecture"]["shell"]["framework"] == "NiceGUI"
    assert result["architecture"]["shell"]["deployment"] == "local_first"
    assert result["architecture"]["shell"]["installation_required"] is True
    assert (
        result["architecture"]["shell"]["system_python_mutation_allowed"]
        is False
    )

    required_adapters = {
        "state",
        "runtime",
        "dashboard",
        "governance",
        "validation",
    }
    assert set(result["architecture"]["adapters"]) == required_adapters

    print("OIF2_0_EXTENDED_CONTRACT_COMPLETENESS_OK")


def test_epistemic_and_anti_closure_invariants() -> None:
    result = OIF2OperationalInterfaceBlueprint().step(
        inputs={},
        persist=False,
    )

    invariants = result["epistemic_invariants"]
    assert invariants == {
        "consciousness_proven": False,
        "subjectivity_proven": False,
        "qualia_proven": False,
        "phenomenology_proven": False,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
    }

    anti_closure = result["anti_closure_constraints"]
    assert anti_closure
    assert all(value is True for value in anti_closure.values())
    assert anti_closure["retain_cli_and_non_ui_access"] is True
    assert anti_closure["support_replaceable_frontends"] is True

    print("OIF2_0_EXTENDED_EPISTEMIC_ANTI_CLOSURE_OK")


def test_hostile_and_ambiguous_inputs() -> None:
    primitive = OIF2OperationalInterfaceBlueprint()

    cases = [
        None,
        {},
        {"mode": ""},
        {"mode": "   "},
        {"mode": "UNSUPPORTED"},
        {"mode": 123},
        {"nicegui_available": []},
        {"nicegui_available": [1]},
        {"ui_environment": ""},
        {"ui_environment": "   "},
        {"unknown_key": {"nested": ["value"]}},
    ]

    for case in cases:
        result = primitive.step(inputs=case, persist=False)
        assert result["status"] == "OIF2_OPERATIONAL_INTERFACE_BLUEPRINT_READY"
        assert result["functional_scope_only"] is True
        canonical(result)

    unsupported = primitive.step(
        inputs={"mode": "UNSUPPORTED"},
        persist=False,
    )
    assert unsupported["requested_mode"] == "audit"
    assert unsupported["degraded"] is True
    assert (
        unsupported["degradation_reason"]
        == "unsupported_mode_fell_back_to_audit"
    )

    blank_environment = primitive.step(
        inputs={"ui_environment": "   "},
        persist=False,
    )
    assert (
        blank_environment["architecture"]["shell"]["environment"]
        == "isolated_.venv-oif"
    )

    print("OIF2_0_EXTENDED_HOSTILE_INPUTS_OK")


def test_fail_closed_persistence_values() -> None:
    primitive = OIF2OperationalInterfaceBlueprint()

    forbidden_values = [True, 1, "false", "", [], {}, object()]
    for value in forbidden_values:
        try:
            primitive.step(inputs={}, persist=value)  # type: ignore[arg-type]
        except ValueError:
            continue
        raise AssertionError(
            f"persist={value!r} should have failed closed"
        )

    primitive.step(inputs={}, persist=False)
    print("OIF2_0_EXTENDED_PERSISTENCE_FAIL_CLOSED_OK")


def test_deepcopy_and_input_immutability() -> None:
    primitive = OIF2OperationalInterfaceBlueprint()
    inputs = {
        "mode": "audit",
        "nicegui_available": False,
        "ui_environment": "isolated_.venv-oif",
        "nested_unrecognized": {
            "items": ["a", "b"],
        },
    }
    before = deepcopy(inputs)

    first = primitive.step(inputs=inputs, persist=False)
    assert inputs == before

    first["architecture"]["zones"]["overview"]["access"] = "mutated"
    first["permission_model"]["read"] = "mutated"
    first["implementation_sequence"].append("mutated")

    second = primitive.step(inputs=inputs, persist=False)
    assert second["architecture"]["zones"]["overview"]["access"] == "read_only"
    assert (
        second["permission_model"]["read"]
        == "allowed_by_default_for_declared_sources"
    )
    assert "mutated" not in second["implementation_sequence"]

    print("OIF2_0_EXTENDED_DEEPCOPY_IMMUTABILITY_OK")


def test_no_filesystem_or_environment_side_effects() -> None:
    primitive = OIF2OperationalInterfaceBlueprint()
    environment_before = dict(os.environ)

    with tempfile.TemporaryDirectory(prefix="oif2_0_side_effect_") as temp_dir:
        root = Path(temp_dir)
        before = snapshot_tree(root)

        old_cwd = Path.cwd()
        os.chdir(root)
        try:
            for _ in range(10):
                primitive.step(
                    inputs={
                        "mode": "audit",
                        "nicegui_available": False,
                    },
                    persist=False,
                )
        finally:
            os.chdir(old_cwd)

        after = snapshot_tree(root)

    assert before == after
    assert dict(os.environ) == environment_before
    print("OIF2_0_EXTENDED_NO_SIDE_EFFECTS_OK")


def test_serialization_and_schema_stability() -> None:
    primitive = OIF2OperationalInterfaceBlueprint()
    baseline = primitive.step(inputs={}, persist=False)
    encoded = canonical(baseline)
    decoded = json.loads(encoded)
    assert decoded == baseline

    top_level_keys = set(baseline)
    for nicegui_available in (False, True):
        candidate = primitive.step(
            inputs={
                "mode": "audit",
                "nicegui_available": nicegui_available,
            },
            persist=False,
        )
        assert set(candidate) == top_level_keys
        assert (
            candidate["architecture"]["shell"]["installation_required"]
            is (not nicegui_available)
        )

    print("OIF2_0_EXTENDED_SERIALIZATION_SCHEMA_STABILITY_OK")


def test_deterministic_campaign_and_performance() -> None:
    primitive = OIF2OperationalInterfaceBlueprint()
    iterations = 1000
    expected = None

    start = time.perf_counter()
    for _ in range(iterations):
        result = primitive.step(
            inputs={
                "mode": "audit",
                "nicegui_available": False,
                "ui_environment": "isolated_.venv-oif",
            },
            persist=False,
        )
        digest = canonical(result)
        if expected is None:
            expected = digest
        else:
            assert digest == expected
    elapsed = time.perf_counter() - start

    # Loose guardrail: detects pathological regressions without being
    # hardware-sensitive on the user's M1 machine.
    assert elapsed < 10.0, (
        f"{iterations} iterations took {elapsed:.3f}s, expected < 10s"
    )

    print(
        "OIF2_0_EXTENDED_1000_ITERATION_DETERMINISM_OK "
        f"elapsed={elapsed:.3f}s"
    )


def test_registry_presence() -> None:
    inventory_txt = ROOT / "ontology_inventory.txt"
    dependency_registry = ROOT / "dependency_registry.py"
    ontology_inventory_py = ROOT / "ontology_inventory.py"

    assert inventory_txt.is_file()
    assert dependency_registry.is_file()
    assert ontology_inventory_py.is_file()

    primitive_name = "oif2_operational_interface_blueprint"
    assert primitive_name in inventory_txt.read_text(
        encoding="utf-8",
        errors="replace",
    )
    assert primitive_name in dependency_registry.read_text(
        encoding="utf-8",
        errors="replace",
    )
    assert primitive_name in ontology_inventory_py.read_text(
        encoding="utf-8",
        errors="replace",
    )

    print("OIF2_0_EXTENDED_REGISTRY_INTEGRATION_OK")


def main() -> int:
    if not ROOT.is_dir():
        raise SystemExit(f"Repository not found: {ROOT}")

    test_contract_completeness()
    test_epistemic_and_anti_closure_invariants()
    test_hostile_and_ambiguous_inputs()
    test_fail_closed_persistence_values()
    test_deepcopy_and_input_immutability()
    test_no_filesystem_or_environment_side_effects()
    test_serialization_and_schema_stability()
    test_deterministic_campaign_and_performance()
    test_registry_presence()

    print("OIF2_0_EXTENDED_VALIDATION_ALL_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
