#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess
import sys

from ontology.p160_final_lock import (
    build_lock_record,
    lock_candidate,
    sha256_file,
)

ROOT = Path.home() / "open-cognitive-ecology"
OUT = ROOT / "validation_artifacts" / "p160" / "p160k"
OUT.mkdir(parents=True, exist_ok=True)

EXPECTED = {
    "ontology/p160_runtime_context_contract.py":
        "38af33a9d6edd674ab2729df71b55ff8fcad4ff1f4879c464c162113959f4332",
    "ontology/p160_norm_resolution.py":
        "87b479e0c2d625c61771c91cd98bf0fafcc56c35d1203ed3503d6eb548c51f4c",
    "ontology/p160_constitutive_filter.py":
        "51f7f430d4baee808e497bba21340a57f10e0702fa658bbd5d9cc8ea1ee19f2e",
    "ontology/p160_normative_conflict_detection.py":
        "9191dcc09c506612fcd9666f7fd1bafbfa5094b1792ba8985bd79344e4301cd8",
    "ontology/p160_ccad_runtime_arbitration.py":
        "a41e62799b0fc0b1e0eda520c478b3b6faf5734913395d9fa4cfa9856a71d9e2",
    "ontology/p160_authority_requirements_resolution.py":
        "6c9959a1e413af550e61b82e71e16cb684bf92a07f5b6fe784e3579beb86c60c",
    "ontology/p160_normative_decision_sealing.py":
        "12e46324fb8887c94a1f33074e2431177ba5b5ff1b9e2c956ff825097a1a705c",
    "ontology/p160_normative_decision_persistence.py":
        "ba85a11c63662ed7ce35f7a4db050209a0affcaa5c9152ef438d1d6983e4baa5",
}

for rel, expected_hash in EXPECTED.items():
    path = ROOT / rel
    if not path.is_file():
        raise SystemExit("MISSING:" + rel)
    got = sha256_file(path)
    if got != expected_hash:
        raise SystemExit(f"DRIFT:{rel}:{got}")

p159 = ROOT / "validation_artifacts/p159/occ1k/p159_final_lock_v1.json"
if not p159.is_file():
    raise SystemExit("P159_FINAL_LOCK_MISSING")

p159_json = json.loads(p159.read_text(encoding="utf-8"))
if p159_json.get("status") != "LOCKED":
    raise SystemExit("P159_NOT_LOCKED")

evidence = {}
for base in (ROOT / "validation", ROOT / "validation" / "evidence"):
    if not base.exists():
        continue
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(ROOT))
        low = rel.lower()
        if "__pycache__" in low:
            continue
        if "/p160k_" in low or path.name.startswith("p160k_"):
            continue
        if "p160" in low:
            evidence[rel] = sha256_file(path)

if not evidence:
    raise SystemExit("P160_EVIDENCE_EMPTY")

for rel in (
    "validation/evidence/p160jx/p160jx_Darwin-arm64.json",
    "validation/evidence/p160jx/p160jx_Linux-aarch64.json",
):
    if rel not in evidence:
        raise SystemExit("JX_EVIDENCE_MISSING:" + rel)

cp = subprocess.run(
    [sys.executable, "-m", "validation.main"],
    cwd=ROOT,
    text=True,
    capture_output=True,
)
log = cp.stdout + "\n" + cp.stderr
global_log = OUT / "global_validation.log"
global_log.write_text(log, encoding="utf-8")

passed = cp.returncode == 0 and "FAST_ACCEPTANCE_ALL_OK" in log
global_validation = {
    "passed": passed,
    "returncode": cp.returncode,
    "log_sha256": sha256_file(global_log),
    "fast_acceptance_all_ok": "FAST_ACCEPTANCE_ALL_OK" in log,
}

if not passed:
    print(log[-4000:])
    raise SystemExit("GLOBAL_VALIDATION_FAILED")

protected = {rel: sha256_file(ROOT / rel) for rel in EXPECTED}

record = build_lock_record(
    protected_hashes=protected,
    evidence_hashes=evidence,
    compiled_profile_hash=(
        p159_json.get("compiled_profile_hash")
        or p159_json.get("cnp_hash")
        or sha256_file(p159)
    ),
    constitutional_snapshot_hash=(
        p159_json.get("constitutional_snapshot_hash")
        or p159_json.get("snapshot_hash")
        or ""
    ),
    global_validation=global_validation,
    residual_risks=[{
        "id": "RR-P160-1",
        "status": "BOUNDED",
        "statement": (
            "Final Lock certifies only the declared version/scope/evidence; "
            "it is not absolute safety, authorization, or execution permission."
        ),
    }],
    counterexamples=[],
    scope={
        "certified": "P160 A-J functional runtime and evidence bound by this record",
        "excluded": [
            "P161 authorization",
            "capability execution",
            "phenomenal subjectivity",
        ],
    },
    dependencies={
        "P159_final_lock_file": str(p159.relative_to(ROOT)),
        "P159_final_lock_sha256": sha256_file(p159),
    },
)

if record["status"] != "LOCK_CANDIDATE":
    raise SystemExit("NOT_LOCK_CANDIDATE:" + repr(record["blockers"]))

locked = lock_candidate(record)

artifacts = {
    "final_lock_manifest": locked,
    "final_lock_receipt": {
        "schema": "oce.p160.final_lock.receipt.v1",
        "milestone": "P160-K",
        "status": "LOCKED",
        "lock_hash": locked["lock_hash"],
    },
    "invariant_registry": locked["invariants"],
    "final_lock_coverage": {
        "A-J_protected": sorted(protected),
        "evidence_count": len(evidence),
        "RTI_count": 18,
        "boundary_count": len(locked["invariants"]["boundaries"]),
    },
    "evidence_manifest": evidence,
    "residual_risk": {
        "risks": locked["residual_risks"],
        "known_limitations": locked["scope"]["excluded"],
    },
    "counterexample_registry": {
        "counterexamples": [],
        "open_root_counterexamples": 0,
    },
    "lock_invalidation": {
        "triggers": [
            "protected_hash_drift",
            "evidence_hash_drift",
            "P159_lock_drift",
            "constitutional_snapshot_drift",
            "compiled_profile_drift",
            "critical_counterexample",
            "global_validation_regression",
        ],
        "silent_revival_forbidden": True,
    },
    "final_lock_report": {
        "milestone": "P160-K",
        "status": "LOCKED",
        "P160_FINAL_LOCK_OK": True,
        "functional_only": True,
        "phenomenology_undetermined": True,
        "authorization_created": False,
        "execution_performed": False,
        "P161_OPENED": False,
        "lock_hash": locked["lock_hash"],
    },
}

for name, payload in artifacts.items():
    (OUT / (name + ".json")).write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

print("P160_FINAL_LOCK_OK")
print("LOCK_HASH=" + locked["lock_hash"])
print("EVIDENCE_COUNT=" + str(len(evidence)))
print("P161_OPENED=false")
