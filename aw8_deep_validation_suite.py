import json
import tempfile
from copy import deepcopy
from pathlib import Path

from aw8_context import build_context
from ontology.civilizational_memory_engine import CivilizationalMemoryEngine


def run_engine(context):
    return CivilizationalMemoryEngine().step(
        inputs=context,
        persist=False,
    )


def test_duplicate_record_rejected() -> None:
    context = build_context()
    context["memory_records"].append(
        deepcopy(context["memory_records"][0])
    )
    result = run_engine(context)
    assert result["civilizational_memory_ready"] is False
    assert result["integrity_status"] == "INVALID"


def test_version_cycle_rejected() -> None:
    context = build_context()
    records = context["memory_records"]
    assert len(records) >= 2
    records[0]["parent_version_ids"] = [records[1]["version_id"]]
    records[1]["parent_version_ids"] = [records[0]["version_id"]]
    result = run_engine(context)
    assert result["civilizational_memory_ready"] is False
    assert result["consistency_status"] == "INCONSISTENT"


def test_hash_scope_excludes_timestamp() -> None:
    engine = CivilizationalMemoryEngine()
    first = engine.step(inputs=build_context(), persist=False)
    second = engine.step(inputs=build_context(), persist=False)

    assert first["timestamp_utc"] != ""
    assert second["timestamp_utc"] != ""
    assert first["result_hash"] == second["result_hash"]
    assert first["memory_hash"] == second["memory_hash"]


def test_payload_change_changes_hash() -> None:
    base = build_context()
    changed = build_context()

    changed["memory_records"][0]["content"] = {
        "payload": "materially changed"
    }

    first = run_engine(base)
    second = run_engine(changed)

    assert first["result_hash"] != second["result_hash"]
    assert first["memory_hash"] != second["memory_hash"]


def test_quorum_exact_boundary() -> None:
    context = build_context()
    context["thresholds"] = {
        "minimum_quorum_ratio": 2 / 3,
    }

    record = context["memory_records"][0]
    record["replica_ids"] = ["R1", "R2", "R3"]
    record["acknowledged_replica_ids"] = ["R1", "R2"]

    result = run_engine(context)
    assert result["quorum_status"] == "QUORUM_REACHED"


def test_quorum_below_boundary() -> None:
    context = build_context()
    context["thresholds"] = {
        "minimum_quorum_ratio": 0.67,
    }

    record = context["memory_records"][0]
    record["replica_ids"] = ["R1", "R2", "R3"]
    record["acknowledged_replica_ids"] = ["R1", "R2"]

    result = run_engine(context)
    assert result["quorum_status"] != "QUORUM_REACHED"
    assert result["civilizational_memory_ready"] is False


def test_persisted_json_round_trip() -> None:
    engine = CivilizationalMemoryEngine()
    original_output_dir = engine.output_dir

    with tempfile.TemporaryDirectory() as tmp:
        engine.output_dir = Path(tmp)
        result = engine.step(
            inputs=build_context(),
            persist=True,
        )

        assert result["persisted"] is True
        assert result["output_path"] is not None

        path = Path(result["output_path"])
        assert path.is_file()

        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded["status"] == result["status"]
        assert loaded["result_hash"] == result["result_hash"]
        assert loaded["memory_hash"] == result["memory_hash"]

    engine.output_dir = original_output_dir


def test_input_schema_degradation() -> None:
    result = run_engine({
        "memory_records": "not-a-list",
        "rf_registry": {},
    })
    assert result["civilizational_memory_ready"] is False
    assert result["integrity_status"] == "INVALID"


def test_unknown_parent_and_unknown_rf_combined() -> None:
    context = build_context()
    context["memory_records"][0]["origin_rf_id"] = "RF-UNKNOWN"
    context["memory_records"][1]["parent_version_ids"] = [
        "MISSING-VERSION"
    ]

    result = run_engine(context)

    assert result["civilizational_memory_ready"] is False
    assert result["integrity_status"] == "INVALID"
    assert result["consistency_status"] == "INCONSISTENT"
    assert "MISSING-VERSION" in result["orphan_parent_version_ids"]


def test_functional_epistemic_boundary_under_failure() -> None:
    context = build_context()
    context["memory_records"] = []

    result = run_engine(context)

    assert result["civilizational_memory_ready"] is False
    assert result["collective_consciousness_proven"] is False
    assert result["collective_subjectivity_proven"] is False
    assert result["collective_qualia_proven"] is False
    assert result["collective_phenomenology_proven"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True


def main() -> None:
    test_duplicate_record_rejected()
    test_version_cycle_rejected()
    test_hash_scope_excludes_timestamp()
    test_payload_change_changes_hash()
    test_quorum_exact_boundary()
    test_quorum_below_boundary()
    test_persisted_json_round_trip()
    test_input_schema_degradation()
    test_unknown_parent_and_unknown_rf_combined()
    test_functional_epistemic_boundary_under_failure()
    print("AW8_DEEP_VALIDATION_OK")


if __name__ == "__main__":
    main()
