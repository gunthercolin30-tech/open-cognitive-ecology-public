from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
REPORT = ROOT / "validation_evidence" / "p017_final_lock_report.json"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    assert REPORT.is_file(), f"missing Final Lock report: {REPORT}"
    report = json.loads(REPORT.read_text(encoding="utf-8"))

    assert report["schema"] == "oce.p017.final_lock.v1"
    assert report["milestone"] == "P017"
    assert report["status"] == "LOCKED"
    assert report["scope"] == "P017_ONLY"
    assert report["decision"] == "CREATE_THIN_DNA_REGISTRY"
    assert report["unknown_promotion"] is False
    assert report["runtime_authority_extended"] is False
    assert report["functional_conclusion_only"] is True
    assert report["phenomenology_undetermined"] is True

    hashes = report["protected_hashes"]
    assert hashes
    for rel, expected in hashes.items():
        path = ROOT / rel
        assert path.is_file(), f"protected artifact missing: {rel}"
        actual = sha256(path)
        assert actual == expected, (
            f"Final Lock integrity failure: {rel}: "
            f"expected={expected} actual={actual}"
        )

    assert report["test_results"]
    assert all(
        item["returncode"] == 0
        for item in report["test_results"].values()
    )

    print("P017_FINAL_LOCK_INTEGRITY_OK")

if __name__ == "__main__":
    main()
