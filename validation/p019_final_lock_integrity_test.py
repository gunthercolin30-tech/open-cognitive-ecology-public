from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
REPORT = ROOT / "validation_evidence/p019_final_lock_report.json"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def canonical_hash(payload) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def main():
    assert REPORT.is_file()
    report = json.loads(REPORT.read_text(encoding="utf-8"))

    assert report["schema"] == "oce.p019.final_lock.v1"
    assert report["milestone"] == "P019"
    assert report["status"] == "LOCKED"
    assert report["scope"] == "P019_ONLY"
    assert report["decision"] == "CREATE_THIN_DNA_SEVERITY_MODEL"
    assert report["levels"] == ["ADVISORY", "STANDARD", "STRICT", "CONSTITUTIONAL"]
    assert report["rank"] == {"ADVISORY": 0, "STANDARD": 1, "STRICT": 2, "CONSTITUTIONAL": 3}
    assert report["functional_conclusion_only"] is True
    assert report["phenomenology_undetermined"] is True
    assert report["unknown_promotion"] is False
    assert report["runtime_authority_granted"] is False
    assert all(v == "PASS" for v in report["evidence"].values())

    for rel, expected in report["protected_hashes"].items():
        assert sha(ROOT / rel) == expected, rel
    for rel, expected in report["predecessor_hashes"].items():
        assert sha(ROOT / rel) == expected, rel

    stable = dict(report)
    identity = stable.pop("lock_identity_sha256")
    stable.pop("generated_at_utc")
    assert canonical_hash(stable) == identity

    print("P019_FINAL_LOCK_INTEGRITY_OK")
    print("lock_identity_sha256=" + identity)
    print("protected_file_count=" + str(len(report["protected_hashes"])))

if __name__ == "__main__":
    main()
