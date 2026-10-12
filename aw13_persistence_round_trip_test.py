import json, tempfile
from pathlib import Path
from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker
with tempfile.TemporaryDirectory() as directory:
    checker = CivilizationTheoremChecker(Path(directory)); result = checker.step(build_context(), persist=True)
    latest = json.loads(Path(result["latest_path"]).read_text(encoding="utf-8")); lines = Path(result["history_path"]).read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1 and latest["civilization_test_hash"] == result["civilization_test_hash"]
print("AW13_PERSISTENCE_ROUND_TRIP_OK")
