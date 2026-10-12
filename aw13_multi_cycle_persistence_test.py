import json
import tempfile
from pathlib import Path
from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker

with tempfile.TemporaryDirectory() as directory:
    checker = CivilizationTheoremChecker(Path(directory))
    hashes = []
    timestamps = []
    for index in range(100):
        context = build_context()
        context["tested_at_utc"] = f"2026-08-{1 + index // 24:02d}T{index % 24:02d}:00:00Z"
        context["property_scores"]["prediction_capacity"] = round(0.001 + index * 0.009, 6)
        result = checker.step(context, persist=True)
        hashes.append(result["civilization_test_hash"])
        timestamps.append(result["tested_at_utc"])

    lines = checker.history_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 100
    records = [json.loads(line) for line in lines]
    assert [record["tested_at_utc"] for record in records] == timestamps
    assert [record["civilization_test_hash"] for record in records] == hashes
    assert len(set(hashes)) == 100
    latest = json.loads(checker.latest_path.read_text(encoding="utf-8"))
    assert latest["civilization_test_hash"] == hashes[-1]

print("AW13_MULTI_CYCLE_PERSISTENCE_OK")
