from copy import deepcopy

from ontology.civilizational_memory import CivilizationalMemory
from ontology.civilizational_memory_engine import CivilizationalMemoryEngine
from aw8_context import build_context


def test_legacy_coexistence() -> None:
    legacy = CivilizationalMemory().step({
        "knowledge_retention": 0.9,
        "educational_fidelity": 0.8,
        "cultural_reproduction": 0.8,
        "archival_integrity": 0.9,
    })
    assert 0.0 <= legacy["civilizational_memory_index"] <= 1.0
    assert legacy["civilizational_memory_index"] >= 0.5

    result = CivilizationalMemoryEngine().step(
        inputs=build_context(),
        persist=False,
    )
    assert result["status"] == "CIVILIZATIONAL_MEMORY_READY"
    assert result["civilizational_memory_ready"] is True


def test_threshold_boundary() -> None:
    engine = CivilizationalMemoryEngine()
    base = build_context()
    baseline = engine.step(inputs=deepcopy(base), persist=False)
    score = baseline["loss_tolerance_score"]

    at_boundary = deepcopy(base)
    at_boundary["thresholds"] = {
        "minimum_loss_tolerance_score": score,
    }
    assert engine.step(
        inputs=at_boundary,
        persist=False,
    )["civilizational_memory_ready"] is True

    above_boundary = deepcopy(base)
    above_boundary["thresholds"] = {
        "minimum_loss_tolerance_score": min(1.0, score + 0.000001),
    }
    result = engine.step(inputs=above_boundary, persist=False)
    if score < 1.0:
        assert result["civilizational_memory_ready"] is False


def test_orphan_parent_detection() -> None:
    context = build_context()
    context["memory_records"][1]["parent_version_ids"] = [
        "MISSING-PARENT-V0"
    ]
    result = CivilizationalMemoryEngine().step(
        inputs=context,
        persist=False,
    )
    assert result["status"] == "CIVILIZATIONAL_MEMORY_NOT_READY"
    assert result["consistency_status"] == "INCONSISTENT"
    assert "MISSING-PARENT-V0" in result["orphan_parent_version_ids"]


def test_order_invariance() -> None:
    engine = CivilizationalMemoryEngine()
    first = build_context()
    second = build_context()
    second["memory_records"] = list(reversed(second["memory_records"]))

    a = engine.step(inputs=first, persist=False)
    b = engine.step(inputs=second, persist=False)

    assert a["result_hash"] == b["result_hash"]
    assert a["memory_records"] == b["memory_records"]


def test_unknown_rf_rejected() -> None:
    context = build_context()
    context["memory_records"][0]["origin_rf_id"] = "RF-UNKNOWN"
    result = CivilizationalMemoryEngine().step(
        inputs=context,
        persist=False,
    )
    assert result["status"] == "CIVILIZATIONAL_MEMORY_NOT_READY"
    assert result["integrity_status"] == "INVALID"


def test_epistemic_guards() -> None:
    result = CivilizationalMemoryEngine().step(
        inputs=build_context(),
        persist=False,
    )
    assert result["collective_consciousness_proven"] is False
    assert result["collective_subjectivity_proven"] is False
    assert result["collective_qualia_proven"] is False
    assert result["collective_phenomenology_proven"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True


def main() -> None:
    test_legacy_coexistence()
    test_threshold_boundary()
    test_orphan_parent_detection()
    test_order_invariance()
    test_unknown_rf_rejected()
    test_epistemic_guards()
    print("AW8_ADDITIONAL_VALIDATION_OK")


if __name__ == "__main__":
    main()
