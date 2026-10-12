from __future__ import annotations

import hashlib
import json
import multiprocessing
import tempfile
from pathlib import Path
from typing import Any

from ontology.acee_impact_evaluator import AceeImpactEvaluator


def canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def impact_hash(record: dict[str, Any]) -> str:
    # impact_hash is computed before persistence metadata is attached.
    excluded = {
        "impact_hash",
        "persisted",
        "latest_path",
        "history_path",
    }
    payload = {
        key: value
        for key, value in record.items()
        if key not in excluded
    }
    return hashlib.sha256(
        canonical(payload).encode("utf-8")
    ).hexdigest()


def context(index: int) -> dict:
    return {
        "evaluation_id": f"process-{index:02d}",
        "timestamp_utc": f"2026-07-13T22:{index:02d}:00Z",
        "cycle_id": f"cycle-{index:02d}",
        "validation_id": f"validation-{index:02d}",
        "before": {
            "validation": {
                "error_count": 0,
                "modules_discovered": 1200 + index,
                "active_primitives": 1100 + index,
                "validation_passed": True,
            },
            "stability_score": 0.88,
            "governance_score": 0.90,
            "evolution_score": 0.70,
            "closure_pressure": 0.22,
            "runtime_score": 0.88,
        },
        "after": {
            "validation": {
                "error_count": 0,
                "modules_discovered": 1201 + index,
                "active_primitives": 1101 + index,
                "validation_passed": True,
                "validation_id": f"validation-{index:02d}",
            },
            "stability_score": 0.91,
            "governance_score": 0.92,
            "evolution_score": 0.76,
            "closure_pressure": 0.18,
            "runtime_score": 0.91,
        },
    }


def run_evaluation(arguments: tuple[str, int]) -> str:
    root_string, index = arguments
    result = AceeImpactEvaluator(root=Path(root_string)).step(
        inputs=context(index),
        persist=True,
    )
    assert result["persisted"] is True
    assert result["comparison_valid"] is True
    return result["evaluation_id"]


def main() -> None:
    multiprocessing.set_start_method("spawn", force=True)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "root"
        root.mkdir(parents=True)

        process_count = 16
        arguments = [
            (str(root), index)
            for index in range(process_count)
        ]

        with multiprocessing.Pool(processes=4) as pool:
            evaluation_ids = pool.map(run_evaluation, arguments)

        assert len(evaluation_ids) == process_count
        assert len(set(evaluation_ids)) == process_count

        directory = (
            root
            / "acee_runtime"
            / "ACEE8_acee_impact_evaluator"
        )
        history = directory / "impact_evaluation_history.jsonl"
        latest = directory / "latest_impact_evaluation.json"

        assert history.is_file()
        assert latest.is_file()

        records = [
            json.loads(line)
            for line in history.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        assert len(records) == process_count
        assert len({record["evaluation_id"] for record in records}) == process_count
        assert all(record["persisted"] is True for record in records)
        assert all(record["comparison_valid"] is True for record in records)

        previous_hash = None
        for record in records:
            assert record["previous_impact_hash"] == previous_hash
            assert record["impact_hash"] == impact_hash(record)
            previous_hash = record["impact_hash"]

        latest_record = json.loads(latest.read_text(encoding="utf-8"))
        assert latest_record == records[-1]
        assert latest_record["impact_hash"] == previous_hash

    print("ACEE8_MULTIPROCESS_PERSISTENCE_OK")


if __name__ == "__main__":
    main()
