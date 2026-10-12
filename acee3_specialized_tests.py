\
from __future__ import annotations

import json
import math
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path

from acee3_fast_acceptance_suite import SAMPLES
from ontology.acee_bridge_adapter import AceeBridgeAdapter


def main() -> None:
    adapter = AceeBridgeAdapter(root=Path("/nonexistent"))
    fixed = {
        "source_module": "controlled_evolution_orchestrator",
        "source_result": SAMPLES["controlled_evolution_orchestrator"],
        "adapter_timestamp_utc": "2026-07-13T15:42:00Z",
    }
    first = adapter.step(inputs=fixed, persist=False)
    second = adapter.step(inputs=deepcopy(fixed), persist=False)
    assert first["normalized_hash"] == second["normalized_hash"]

    reordered_result = dict(reversed(list(SAMPLES["controlled_evolution_orchestrator"].items())))
    reordered = adapter.step(
        inputs={**fixed, "source_result": reordered_result},
        persist=False,
    )
    assert first["normalized_hash"] == reordered["normalized_hash"]
    assert reordered["raw_result"] == reordered_result

    contradictory = adapter.step(
        inputs={
            "source_module": "controlled_evolution_orchestrator",
            "source_result": {
                "approved": True,
                "executed": False,
                "rollback_available": False,
                "rollback_performed": True,
                "pipeline_score": math.nan,
                "confidence": math.inf,
            },
            "adapter_timestamp_utc": "2026-07-13T15:43:00Z",
        },
        persist=False,
    )
    assert contradictory["status"] == "rolled_back"
    assert contradictory["score"] is None
    assert contradictory["confidence"] is None
    assert "approved_not_executed" in contradictory["normalization_warnings"]
    assert "rollback_performed_but_marked_unavailable" in contradictory["normalization_warnings"]

    root = Path(tempfile.mkdtemp(prefix="acee3_history_"))
    try:
        persistent = AceeBridgeAdapter(root=root)
        a = persistent.step(inputs=fixed, persist=True)
        b = persistent.step(inputs={**fixed, "adapter_timestamp_utc": "2026-07-13T15:44:00Z"}, persist=True)
        assert b["previous_normalized_hash"] == a["normalized_hash"]
        records = [json.loads(line) for line in Path(b["history_path"]).read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(records) == 2
        assert records[1]["previous_normalized_hash"] == records[0]["normalized_hash"]
        Path(b["history_path"]).write_text("{broken\n", encoding="utf-8")
        corrupted = persistent.step(inputs=fixed, persist=False)
        assert "history_corrupted" in corrupted["degraded_reasons"]
    finally:
        shutil.rmtree(root, ignore_errors=True)

    for key in (
        "consciousness_proven",
        "subjectivity_proven",
        "qualia_proven",
        "phenomenology_proven",
        "collective_consciousness_proven",
    ):
        assert first[key] is False
    print("ACEE3_SPECIALIZED_TESTS_OK")


if __name__ == "__main__":
    main()
