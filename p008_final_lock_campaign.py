#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
FINAL_LOCK = ROOT / "p008_final_lock.py"
REPORT = ROOT / "p008_final_lock_report.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute() -> tuple[str, dict]:
    completed = subprocess.run(
        [sys.executable, str(FINAL_LOCK)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=2400,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    output = completed.stdout + completed.stderr
    if completed.returncode != 0 or "P008_FINAL_LOCK_OK" not in output:
        raise RuntimeError(output)
    return output, json.loads(REPORT.read_text(encoding="utf-8"))


protected = [
    ROOT / "validation" / "oce_v2_global_audit.py",
    ROOT / "p008_adversarial_crown.py",
    ROOT / "p008_architectural_completeness_crown.py",
]
before = {str(p.relative_to(ROOT)): sha(p) for p in protected}

out1, r1 = execute()
after1 = {str(p.relative_to(ROOT)): sha(p) for p in protected}
assert before == after1
assert r1["status"] == "LOCKED"
assert r1["functional_conclusion_only"] is True
assert r1["phenomenology_undetermined"] is True
assert r1["consciousness_proven"] is False
assert r1["subjectivity_proven"] is False
assert r1["qualia_proven"] is False
assert r1["phenomenology_proven"] is False
assert r1["architecture_completeness"] == "UNKNOWN"
assert r1["runtime_call_exercised"] == "UNKNOWN"
assert r1["dynamic_import_resolution"] == "UNKNOWN"
assert r1["parse_error_count"] == 1
print("P008_FINAL_LOCK_FUNCTIONAL_OK")

out2, r2 = execute()
after2 = {str(p.relative_to(ROOT)): sha(p) for p in protected}
assert before == after2
assert r1["lock_identity_sha256"] == r2["lock_identity_sha256"]
assert r1["identity_payload"] == r2["identity_payload"]
print("P008_FINAL_LOCK_DETERMINISM_OK")

tampered = json.loads(REPORT.read_text(encoding="utf-8"))
tampered["identity_payload"]["parse_error_count"] = 0
raw = json.dumps(
    tampered["identity_payload"], sort_keys=True, separators=(",", ":")
).encode("utf-8")
recomputed = hashlib.sha256(raw).hexdigest()
assert recomputed != tampered["lock_identity_sha256"]
print("P008_FINAL_LOCK_TAMPER_DETECTED")

assert r2["audit_report_sha256"] == sha(ROOT / "p008_global_audit_report.json")
assert r2["audit_fingerprint_sha256"] == r2["identity_payload"]["audit_fingerprint_sha256"]
assert r2["p007_baseline_identity_sha256"] == r2["identity_payload"]["p007_baseline_identity_sha256"]
print("P008_FINAL_LOCK_BINDING_OK")

print("P008_FINAL_LOCK_CAMPAIGN_OK")
