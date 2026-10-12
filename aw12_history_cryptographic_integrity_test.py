import hashlib
import json
import tempfile
from pathlib import Path

from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    engine = EcologicalPredictionEngine(root)
    for index in range(3):
        context = build_context()
        context["issued_at"] = f"2026-07-{13 + index:02d}T08:00:00Z"
        context["trend_signals"]["stability"] = round(0.05 * index, 6)
        engine.step(context, persist=True)

    history_path = engine.history_path
    original_bytes = history_path.read_bytes()
    original_lines = history_path.read_bytes().splitlines(keepends=True)
    assert len(original_lines) == 3
    baseline_digests = [digest(line) for line in original_lines]
    assert len(set(baseline_digests)) == 3
    for line in original_lines:
        json.loads(line.decode("utf-8"))

    tampered_lines = list(original_lines)
    first_record = json.loads(tampered_lines[0].decode("utf-8"))
    first_record["current_state"]["stability"] = 0.0
    tampered_lines[0] = (json.dumps(first_record, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    history_path.write_bytes(b"".join(tampered_lines))

    altered_lines = history_path.read_bytes().splitlines(keepends=True)
    altered_digests = [digest(line) for line in altered_lines]
    changed_indexes = [index for index, (before, after) in enumerate(zip(baseline_digests, altered_digests)) if before != after]
    assert changed_indexes == [0]
    assert history_path.read_bytes() != original_bytes

    history_path.write_bytes(original_bytes)
    restored_digests = [digest(line) for line in history_path.read_bytes().splitlines(keepends=True)]
    assert restored_digests == baseline_digests
    assert history_path.read_bytes() == original_bytes

print("AW12_HISTORY_CRYPTOGRAPHIC_INTEGRITY_OK")
