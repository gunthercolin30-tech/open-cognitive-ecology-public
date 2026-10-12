from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
REPORT = ROOT / "validation_evidence" / "p015_final_lock_report.json"

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    payload = json.loads(REPORT.read_text(encoding="utf-8"))
    assert payload["milestone"] == "P015"
    assert payload["status"] == "LOCKED"
    assert payload["scope"] == "P015_ONLY"
    assert payload["unknown_promotion"] is False
    assert payload["functional_conclusion_only"] is True
    assert payload["phenomenology_undetermined"] is True
    assert all(item["returncode"] == 0 for item in payload["tests"].values())
    for rel, expected in payload["protected_hashes"].items():
        assert sha256(ROOT / rel) == expected
    print("P015_FINAL_LOCK_INTEGRITY_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
