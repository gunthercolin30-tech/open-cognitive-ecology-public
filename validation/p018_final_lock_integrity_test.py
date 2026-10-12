from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
REPORT = ROOT / "validation_evidence" / "p018_final_lock_report.json"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

def main():
    assert REPORT.is_file()
    report = json.loads(REPORT.read_text(encoding="utf-8"))

    assert report["schema"] == "oce.p018.final_lock.v1"
    assert report["milestone"] == "P018"
    assert report["status"] == "LOCKED"
    assert report["scope"] == "P018_ONLY"
    assert report["decision"] == "CREATE_THIN_DNA_RULE_CONTRACT"
    assert report["functional_conclusion_only"] is True
    assert report["phenomenology_undetermined"] is True
    assert report["unknown_promotion"] is False
    assert report["runtime_authority_granted"] is False

    for rel, expected in report["protected_hashes"].items():
        path = ROOT / rel
        assert path.is_file(), rel
        assert digest(path) == expected, rel

    for rel, expected in report["predecessor_hashes"].items():
        path = ROOT / rel
        assert path.is_file(), rel
        assert digest(path) == expected, rel

    stable = dict(report)
    stable.pop("lock_identity_sha256")
    stable.pop("generated_at_utc")
    identity = hashlib.sha256(canonical_json(stable).encode("utf-8")).hexdigest()
    assert identity == report["lock_identity_sha256"]

    assert all(value == "PASS" for value in report["evidence"].values())

    print("P018_FINAL_LOCK_INTEGRITY_OK")
    print("lock_identity_sha256=" + identity)
    print("protected_file_count=" + str(len(report["protected_hashes"])))

if __name__ == "__main__":
    main()
