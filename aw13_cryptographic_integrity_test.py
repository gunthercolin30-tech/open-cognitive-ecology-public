import json
import tempfile
from pathlib import Path
from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker


def recompute(checker, record):
    payload = dict(record)
    expected = payload.pop("civilization_test_hash")
    payload.pop("tested_at_utc", None)
    payload.pop("persisted", None)
    payload.pop("history_path", None)
    payload.pop("latest_path", None)
    return expected, checker._hash(payload)

with tempfile.TemporaryDirectory() as directory:
    checker = CivilizationTheoremChecker(Path(directory))
    result = checker.step(build_context(), persist=True)
    latest = json.loads(checker.latest_path.read_text(encoding="utf-8"))
    historical = json.loads(checker.history_path.read_text(encoding="utf-8").splitlines()[0])

    for record in (result, latest, historical):
        expected, actual = recompute(checker, record)
        assert expected == actual

    tampered = dict(historical)
    tampered["mean_confidence"] = 0.0
    expected, actual = recompute(checker, tampered)
    assert expected != actual

print("AW13_CRYPTOGRAPHIC_INTEGRITY_OK")
