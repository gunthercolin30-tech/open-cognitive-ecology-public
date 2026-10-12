\
import json
import math
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path

from acee1_fast_acceptance_suite import build_audit
from ontology.acee_capability_map import AceeCapabilityMap


def main():
    audit = build_audit()
    fixed = {"integration_audit": audit, "map_timestamp_utc": "2026-07-13T13:03:00Z"}
    first = AceeCapabilityMap(root=Path("/nonexistent")).step(inputs=fixed, persist=False)
    second = AceeCapabilityMap(root=Path("/nonexistent")).step(inputs=deepcopy(fixed), persist=False)
    assert first["mapping_hash"] == second["mapping_hash"]
    reversed_audit = deepcopy(audit)
    reversed_audit["existing_modules"] = list(reversed(audit["existing_modules"]))
    reversed_audit["coverage_matrix"] = dict(reversed(list(audit["coverage_matrix"].items())))
    reordered = AceeCapabilityMap(root=Path("/nonexistent")).step(
        inputs={"integration_audit": reversed_audit, "map_timestamp_utc": fixed["map_timestamp_utc"]}, persist=False
    )
    assert first["capability_matrix"] == reordered["capability_matrix"]
    assert first["deferred_capabilities"] == ["ACEE5", "ACEE6"]
    noisy = AceeCapabilityMap(root=Path("/nonexistent")).step(
        inputs={"integration_audit": audit, "weights": {"ACEE0": math.nan, "ACEE1": math.inf}, "map_timestamp_utc": "2026-07-13T13:04:00Z"},
        persist=False,
    )
    assert math.isfinite(noisy["weighted_coverage_score"])
    root = Path(tempfile.mkdtemp(prefix="acee1_history_"))
    try:
        mapper = AceeCapabilityMap(root=root)
        a = mapper.step(inputs={"integration_audit": audit, "map_timestamp_utc": "2026-07-13T13:05:00Z"}, persist=True)
        b = mapper.step(inputs={"integration_audit": audit, "map_timestamp_utc": "2026-07-13T13:06:00Z"}, persist=True)
        assert b["previous_mapping_hash"] == a["mapping_hash"]
        records = [json.loads(line) for line in Path(b["history_path"]).read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(records) == 2
        assert records[1]["previous_mapping_hash"] == records[0]["mapping_hash"]
        Path(b["history_path"]).write_text("{broken\n", encoding="utf-8")
        corrupted = mapper.step(inputs={"integration_audit": audit, "map_timestamp_utc": "2026-07-13T13:07:00Z"}, persist=False)
        assert "history_corrupted" in corrupted["degraded_reasons"]
    finally:
        shutil.rmtree(root, ignore_errors=True)
    for key in ("consciousness_proven", "subjectivity_proven", "qualia_proven", "phenomenology_proven", "collective_consciousness_proven"):
        assert first[key] is False
    print("ACEE1_SPECIALIZED_TESTS_OK")


if __name__ == "__main__":
    main()
