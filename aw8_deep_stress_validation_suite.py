import json
import tempfile
from copy import deepcopy
from pathlib import Path

from aw8_context import build_context
from ontology.civilizational_memory_engine import CivilizationalMemoryEngine


def run(context, persist=False, output_dir=None):
    engine = CivilizationalMemoryEngine()
    if output_dir is not None:
        engine.output_dir = Path(output_dir)
    return engine.step(inputs=context, persist=persist)


def test_permutation_invariance() -> None:
    base = build_context()
    permuted = deepcopy(base)

    permuted["memory_records"] = list(
        reversed(permuted["memory_records"])
    )

    for record in permuted["memory_records"]:
        if isinstance(record.get("replica_ids"), list):
            record["replica_ids"] = list(
                reversed(record["replica_ids"])
            )
        if isinstance(record.get("acknowledged_replica_ids"), list):
            record["acknowledged_replica_ids"] = list(
                reversed(record["acknowledged_replica_ids"])
            )
        if isinstance(record.get("parent_version_ids"), list):
            record["parent_version_ids"] = list(
                reversed(record["parent_version_ids"])
            )

    first = run(base)
    second = run(permuted)

    assert first["result_hash"] == second["result_hash"]
    assert first["memory_hash"] == second["memory_hash"]
    assert first["civilizational_memory_ready"] == second[
        "civilizational_memory_ready"
    ]


def test_quorum_monotonicity() -> None:
    base = build_context()
    degraded = deepcopy(base)

    for record in degraded["memory_records"]:
        acknowledgements = list(
            record.get("acknowledged_replica_ids", [])
        )
        if acknowledgements:
            record["acknowledged_replica_ids"] = acknowledgements[:-1]

    first = run(base)
    second = run(degraded)

    assert second["availability_score"] <= first["availability_score"]
    assert second["loss_tolerance_score"] <= first["loss_tolerance_score"]

    if first["civilizational_memory_ready"] is False:
        assert second["civilizational_memory_ready"] is False


def test_restart_hash_continuity() -> None:
    context = build_context()

    with tempfile.TemporaryDirectory() as tmp:
        persisted = run(
            deepcopy(context),
            persist=True,
            output_dir=tmp,
        )

        path = Path(persisted["output_path"])
        loaded = json.loads(path.read_text(encoding="utf-8"))

        restarted = run(deepcopy(context), persist=False)

        assert loaded["result_hash"] == restarted["result_hash"]
        assert loaded["memory_hash"] == restarted["memory_hash"]
        assert loaded["status"] == restarted["status"]
        assert loaded["integrity_status"] == restarted["integrity_status"]
        assert loaded["consistency_status"] == restarted[
            "consistency_status"
        ]


def test_multiple_duplicate_accounting() -> None:
    context = build_context()
    duplicate = deepcopy(context["memory_records"][0])

    context["memory_records"].append(deepcopy(duplicate))
    context["memory_records"].append(deepcopy(duplicate))

    result = run(context)

    # duplicate_record_count counts distinct duplicated keys.
    assert result["duplicate_record_count"] == 1
    assert len(result["duplicate_record_keys"]) == 1
    assert result["duplicate_record_keys"][0]["count"] == 3
    assert result["integrity_status"] == "INVALID"
    assert result["consistency_status"] == "INCONSISTENT"
    assert result["civilizational_memory_ready"] is False


def test_cycle_detection_determinism() -> None:
    first_context = build_context()
    second_context = build_context()

    for context in (first_context, second_context):
        records = context["memory_records"]
        records[0]["parent_version_ids"] = [
            records[1]["version_id"]
        ]
        records[1]["parent_version_ids"] = [
            records[0]["version_id"]
        ]

    second_context["memory_records"] = list(
        reversed(second_context["memory_records"])
    )

    first = run(first_context)
    second = run(second_context)

    assert first["version_cycle_count"] == second["version_cycle_count"]
    assert first["version_cycle_count"] >= 1
    assert first["civilizational_memory_ready"] is False
    assert second["civilizational_memory_ready"] is False


def test_failure_does_not_raise_epistemic_claims() -> None:
    context = build_context()
    context["memory_records"] = []

    result = run(context)

    assert result["civilizational_memory_ready"] is False
    assert result["collective_consciousness_proven"] is False
    assert result["collective_subjectivity_proven"] is False
    assert result["collective_qualia_proven"] is False
    assert result["collective_phenomenology_proven"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True


def main() -> None:
    test_permutation_invariance()
    test_quorum_monotonicity()
    test_restart_hash_continuity()
    test_multiple_duplicate_accounting()
    test_cycle_detection_determinism()
    test_failure_does_not_raise_epistemic_claims()
    print("AW8_DEEP_STRESS_VALIDATION_OK")


if __name__ == "__main__":
    main()
