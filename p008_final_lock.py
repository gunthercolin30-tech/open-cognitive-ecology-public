#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
REPORT = ROOT / "p008_final_lock_report.json"

EXPECTED = {
    "validation/oce_v2_global_audit.py": "f6f74afacff7b5f05dee559fd3f30affafae0afee29ab1fdf3d0ff309769bce2",
    "p008_adversarial_crown.py": "25b6779663e98634098aa610c7090952baa0975d9d32a5a62b7547f21f997704",
    "p008_architectural_completeness_crown.py": "82cae6584a8f94f7f3ab63fa288a341003f4d6aa62a74ef100aaa6459173aff8",
}
EXPECTED_AUDIT_FINGERPRINT = "366ed5ed3698d89011246a6df90b94d238f8185d046267170a3c495caddebb95"
EXPECTED_P007_IDENTITY = "4d72de2a035cff30d1b91cc99f243a0c5ced225afe5cedee7565a8412652df50"
EXPECTED_PARSE_ERROR_COUNT = 1
EXPECTED_FINDING_PATH = "ao5_extended_acceptance_suite_v2.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(rel: str, marker: str, timeout: int = 900) -> str:
    completed = subprocess.run(
        [sys.executable, str(ROOT / rel)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    output = completed.stdout + completed.stderr
    if completed.returncode != 0 or marker not in output:
        raise RuntimeError(f"{rel} failed\n{output}")
    return output


def stable_identity(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


for rel, expected in EXPECTED.items():
    path = ROOT / rel
    if not path.is_file():
        raise RuntimeError(f"missing protected file: {rel}")
    actual = sha(path)
    if actual != expected:
        raise RuntimeError(f"protected file drift: {rel} expected={expected} actual={actual}")

e1 = run("p008_adversarial_crown.py", "P008_ADVERSARIAL_CROWN_OK")
e2 = run("p008_architectural_completeness_crown.py", "P008_ARCHITECTURAL_COMPLETENESS_CROWN_OK")
audit_output = run("validation/oce_v2_global_audit.py", "P008_GLOBAL_AUDIT_OK")

audit_report_path = ROOT / "p008_global_audit_report.json"
if not audit_report_path.is_file():
    raise RuntimeError("missing p008_global_audit_report.json")
audit_report = json.loads(audit_report_path.read_text(encoding="utf-8"))

if audit_report.get("schema") != "oce.p008.global_audit.v1":
    raise RuntimeError("unexpected P008 audit schema")
if audit_report.get("audit_fingerprint_sha256") != EXPECTED_AUDIT_FINGERPRINT:
    raise RuntimeError("P008 audit fingerprint drift")
if audit_report.get("baseline_comparison", {}).get("baseline_identity_sha256") != EXPECTED_P007_IDENTITY:
    raise RuntimeError("P007 baseline identity drift")
summary = audit_report.get("summary", {})
if summary.get("audit_execution_status") != "COMPLETED":
    raise RuntimeError("P008 audit not completed")
if summary.get("parse_error_count") != EXPECTED_PARSE_ERROR_COUNT:
    raise RuntimeError("unexpected parse_error_count")
findings = audit_report.get("syntax_findings", [])
if len(findings) != 1 or findings[0].get("path") != EXPECTED_FINDING_PATH:
    raise RuntimeError("known baseline syntax finding contract drift")
if findings[0].get("classification") != "BASELINE_SYNTAX_FINDING":
    raise RuntimeError("known finding classification drift")

ep = audit_report.get("epistemic_status", {})
required_epistemic = {
    "architecture_completeness": "UNKNOWN",
    "runtime_call_exercised": "UNKNOWN",
    "dynamic_import_resolution": "UNKNOWN",
    "phenomenal_subjectivity": "UNDETERMINED",
    "functional_conclusion_only": True,
}
for key, expected in required_epistemic.items():
    if ep.get(key) != expected:
        raise RuntimeError(f"epistemic invariant drift: {key}")

protected_hashes = {rel: sha(ROOT / rel) for rel in sorted(EXPECTED)}
audit_report_sha256 = sha(audit_report_path)

identity_payload = {
    "milestone": "P008",
    "schema": "oce.p008.final_lock.identity.v1",
    "protected_hashes": protected_hashes,
    "audit_fingerprint_sha256": EXPECTED_AUDIT_FINGERPRINT,
    "p007_baseline_identity_sha256": EXPECTED_P007_IDENTITY,
    "parse_error_count": EXPECTED_PARSE_ERROR_COUNT,
    "known_baseline_syntax_finding": EXPECTED_FINDING_PATH,
    "e1_validated": True,
    "e2_validated": True,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}
lock_identity = stable_identity(identity_payload)

report = {
    "schema": "oce.p008.final_lock.v1",
    "milestone": "P008",
    "status": "LOCKED",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "lock_identity_sha256": lock_identity,
    "identity_payload": identity_payload,
    "audit_report_sha256": audit_report_sha256,
    "audit_report_schema": audit_report["schema"],
    "audit_fingerprint_sha256": EXPECTED_AUDIT_FINGERPRINT,
    "p007_baseline_identity_sha256": EXPECTED_P007_IDENTITY,
    "python_source_count": summary.get("python_source_count"),
    "parse_error_count": summary.get("parse_error_count"),
    "known_baseline_syntax_finding": EXPECTED_FINDING_PATH,
    "architecture_completeness": "UNKNOWN",
    "runtime_call_exercised": "UNKNOWN",
    "dynamic_import_resolution": "UNKNOWN",
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
    "e1_adversarial_crown_validated": True,
    "e2_architectural_completeness_crown_validated": True,
}
REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

print(e1, end="")
print(e2, end="")
print(audit_output, end="")
print(f"lock_identity_sha256={lock_identity}")
print(f"audit_report_sha256={audit_report_sha256}")
print("P008_FINAL_LOCK_OK")
