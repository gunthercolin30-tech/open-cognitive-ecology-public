from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "validation_evidence" / "p016_final_lock_report.json"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    assert REPORT.is_file(), "P016 final lock report missing"
    report = json.loads(REPORT.read_text(encoding="utf-8"))

    assert report.get("milestone") == "P016"
    assert report.get("status") == "LOCKED"
    assert report.get("scope") == "P016_ONLY"
    assert report.get("decision") == "CREATE_THIN_COMPOSITION_LAYER"
    assert report.get("p015_modified") is False
    assert report.get("unknown_promotion") is False
    assert report.get("runtime_authority_extended") is False
    assert report.get("functional_conclusion_only") is True
    assert report.get("phenomenology_undetermined") is True

    hashes = report.get("protected_hashes")
    assert isinstance(hashes, dict) and hashes, "protected_hashes missing"

    for rel, expected in hashes.items():
        path = ROOT / rel
        assert path.is_file(), f"protected file missing: {rel}"
        actual = sha256(path)
        assert actual == expected, f"protected file changed: {rel}"

    print("P016_FINAL_LOCK_INTEGRITY_OK")

if __name__ == "__main__":
    main()
