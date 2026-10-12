#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from copy import deepcopy
from pathlib import Path

from aw9_context import build_context
from ontology.collective_consciousness_analyzer import (
    CollectiveConsciousnessAnalyzer,
)


def run(context, persist=False, root=None):
    analyzer = CollectiveConsciousnessAnalyzer(root=root)
    return analyzer.step(
        inputs=context,
        persist=persist,
    )


def test_persistence_round_trip_contract() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        result = run(
            build_context(),
            persist=True,
            root=Path(tmp),
        )

        assert result["persisted"] is True
        assert result["output_path"] is not None

        path = Path(result["output_path"])
        assert path.is_file()

        loaded = json.loads(path.read_text(encoding="utf-8"))

        assert loaded["persisted"] is True
        assert loaded["output_path"] == str(path)
        assert loaded["analysis_hash"] == result["analysis_hash"]
        assert loaded["status"] == result["status"]


def test_duplicate_edges_do_not_inflate_integration() -> None:
    baseline_context = build_context()
    duplicated_context = deepcopy(baseline_context)

    edges = duplicated_context["interaction_graph"]["edges"]
    duplicated_context["interaction_graph"]["edges"] = (
        deepcopy(edges) + deepcopy(edges)
    )
    duplicated_context["interaction_graph"]["edge_count"] = len(
        duplicated_context["interaction_graph"]["edges"]
    )

    baseline = run(baseline_context)
    duplicated = run(duplicated_context)

    assert (
        duplicated["distributed_coordination_score"]
        <= baseline["distributed_coordination_score"]
    )
    assert (
        duplicated["functional_collective_integration"]
        <= baseline["functional_collective_integration"]
    )


def test_orphan_edges_do_not_inflate_scores() -> None:
    baseline_context = build_context()
    orphan_context = deepcopy(baseline_context)

    orphan_context["interaction_graph"]["edges"].extend([
        {
            "source_rf_id": "RF-UNKNOWN-A",
            "target_rf_id": "RF-UNKNOWN-B",
            "interaction_strength": 1.0,
        },
        {
            "source_rf_id": "RF-UNKNOWN-C",
            "target_rf_id": "RF-UNKNOWN-D",
            "interaction_strength": 1.0,
        },
    ])
    orphan_context["interaction_graph"]["edge_count"] = len(
        orphan_context["interaction_graph"]["edges"]
    )

    baseline = run(baseline_context)
    orphan = run(orphan_context)

    assert (
        orphan["distributed_coordination_score"]
        <= baseline["distributed_coordination_score"]
    )
    assert (
        orphan["functional_collective_integration"]
        <= baseline["functional_collective_integration"]
    )


def test_centralization_blocker_is_reachable() -> None:
    context = build_context()

    records = context["multi_rf_registry"].get(
        "registry",
        context["multi_rf_registry"].get("rf_records", []),
    )
    rf_ids = [record["rf_id"] for record in records]

    hub = rf_ids[0]
    leaves = rf_ids[1:]

    context["interaction_graph"]["edges"] = [
        {
            "source_rf_id": hub,
            "target_rf_id": leaf,
            "interaction_strength": 1.0,
        }
        for leaf in leaves
    ]
    context["interaction_graph"]["edge_count"] = len(
        context["interaction_graph"]["edges"]
    )
    context["interaction_graph"]["density"] = 1.0
    context["thresholds"] = {
        "maximum_centralization_risk": 0.49,
    }

    result = run(context)

    assert result["centralization_risk_score"] > 0.49
    assert (
        "SINGLE_CONTROLLER_OR_CENTRALIZATION_RISK"
        in result["false_positive_blockers"]
    )
    assert result["collective_rf_analysis_ready"] is False


def test_conflict_monotonicity() -> None:
    baseline_context = build_context()
    degraded_context = deepcopy(baseline_context)

    degraded_context["conflict_detection"]["conflicts"] = [
        {
            "conflict_status": "CONFLICT_DETECTED_FUNCTIONALLY",
            "detected": True,
            "conflict_score": 1.0,
            "participant_rf_ids": baseline_context[
                "multi_rf_registry"
            ].get("registry", [])[0:2],
        }
    ]

    baseline = run(baseline_context)
    degraded = run(degraded_context)

    assert (
        degraded["conflict_pressure_score"]
        >= baseline["conflict_pressure_score"]
    )
    assert (
        degraded["functional_collective_integration"]
        <= baseline["functional_collective_integration"]
    )


def test_fragmentation_monotonicity() -> None:
    baseline_context = build_context()
    degraded_context = deepcopy(baseline_context)

    degraded_context[
        "reference_frame_fragmentation"
    ]["fragmentations"] = [
        {
            "fragmentation_status": (
                "FRAGMENTATION_DETECTED_FUNCTIONALLY"
            ),
            "detected": True,
            "fragmentation_score": 1.0,
        },
        {
            "fragmentation_status": (
                "FRAGMENTATION_DETECTED_FUNCTIONALLY"
            ),
            "detected": True,
            "fragmentation_score": 1.0,
        },
    ]

    baseline = run(baseline_context)
    degraded = run(degraded_context)

    assert (
        degraded["fragmentation_pressure_score"]
        >= baseline["fragmentation_pressure_score"]
    )
    assert (
        degraded["functional_collective_integration"]
        <= baseline["functional_collective_integration"]
    )


def test_threshold_boundary() -> None:
    baseline = run(build_context())
    score = baseline["functional_collective_integration"]

    at_boundary = build_context()
    at_boundary["thresholds"] = {
        "minimum_functional_collective_integration": score,
    }
    result_at = run(at_boundary)
    assert result_at["collective_rf_analysis_ready"] is True

    if score < 1.0:
        above_boundary = build_context()
        above_boundary["thresholds"] = {
            "minimum_functional_collective_integration": min(
                1.0,
                score + 0.000001,
            ),
        }
        result_above = run(above_boundary)
        assert result_above["collective_rf_analysis_ready"] is False
        assert (
            "FUNCTIONAL_INTEGRATION_BELOW_THRESHOLD"
            in result_above["false_positive_blockers"]
        )


def test_hash_scope_excludes_timestamp() -> None:
    first = run(build_context())
    second = run(build_context())

    assert first["analysis_hash"] == second["analysis_hash"]
    assert (
        first["collective_structure_hash"]
        == second["collective_structure_hash"]
    )


def test_material_change_changes_hash() -> None:
    baseline_context = build_context()
    changed_context = deepcopy(baseline_context)

    changed_context[
        "civilizational_memory"
    ]["future_openness_preservation_score"] = 0.0

    baseline = run(baseline_context)
    changed = run(changed_context)

    assert baseline["analysis_hash"] != changed["analysis_hash"]


def test_epistemic_guards_under_failure() -> None:
    result = run({})

    assert result["collective_rf_analysis_ready"] is False
    assert result["collective_consciousness_proven"] is False
    assert result["collective_subjectivity_proven"] is False
    assert result["collective_qualia_proven"] is False
    assert result["collective_phenomenology_proven"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True


def main() -> None:
    test_persistence_round_trip_contract()
    test_duplicate_edges_do_not_inflate_integration()
    test_orphan_edges_do_not_inflate_scores()
    test_centralization_blocker_is_reachable()
    test_conflict_monotonicity()
    test_fragmentation_monotonicity()
    test_threshold_boundary()
    test_hash_scope_excludes_timestamp()
    test_material_change_changes_hash()
    test_epistemic_guards_under_failure()
    print("AW9_DEEP_VALIDATION_OK")


if __name__ == "__main__":
    main()
