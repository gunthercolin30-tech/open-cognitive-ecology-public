#!/usr/bin/env python3
from pathlib import Path
import json

from ontology.p160_final_lock import (
    REQUIRED_ARTIFACT_KEYS,
    sha256_file,
    verify_lock,
)

ROOT = Path.home() / "open-cognitive-ecology"
OUT = ROOT / "validation_artifacts" / "p160" / "p160k"

missing = [
    key for key in REQUIRED_ARTIFACT_KEYS
    if not (OUT / (key + ".json")).is_file()
]
if missing:
    raise SystemExit("MISSING:" + ",".join(missing))

manifest = json.loads(
    (OUT / "final_lock_manifest.json").read_text(encoding="utf-8")
)

current = {}
for rel in manifest["protected_hashes"]:
    path = ROOT / rel
    current[rel] = sha256_file(path) if path.is_file() else "MISSING"

verification = verify_lock(manifest, current)

for rel, expected_hash in manifest["evidence_hashes"].items():
    path = ROOT / rel
    if not path.is_file():
        verification["issues"].append("EVIDENCE_MISSING:" + rel)
    elif sha256_file(path) != expected_hash:
        verification["issues"].append("EVIDENCE_DRIFT:" + rel)

for key in REQUIRED_ARTIFACT_KEYS:
    json.loads((OUT / (key + ".json")).read_text(encoding="utf-8"))

report = json.loads(
    (OUT / "final_lock_report.json").read_text(encoding="utf-8")
)

if report.get("authorization_created"):
    verification["issues"].append("AUTHORIZATION_CREATED")
if report.get("execution_performed"):
    verification["issues"].append("EXECUTION_PERFORMED")
if report.get("P161_OPENED"):
    verification["issues"].append("P161_OPENED_PREMATURELY")
if not report.get("functional_only"):
    verification["issues"].append("FUNCTIONAL_ONLY_INVARIANT_LOST")
if not report.get("phenomenology_undetermined"):
    verification["issues"].append("PHENOMENOLOGY_INVARIANT_LOST")
if report.get("lock_hash") != manifest.get("lock_hash"):
    verification["issues"].append("REPORT_LOCK_HASH_MISMATCH")

if verification["issues"]:
    print("\n".join(verification["issues"]))
    raise SystemExit(1)

print("P160K_INDEPENDENT_FINAL_LOCK_VERIFIED")
print("LOCK_HASH=" + manifest["lock_hash"])
print("P160_FINAL_LOCK_OK=true")
print("P161_OPENED=false")
