from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from ontology.baseline_integrity import write_manifest, verify_manifest

ROOT = Path(__file__).resolve().parent
PROTECTED = (
    "ontology/baseline_integrity.py",
    "p007_baseline_functional_test.py",
    "p007_baseline_determinism_test.py",
    "p007_baseline_degradation_test.py",
    "p007_baseline_non_regression_test.py",
    "p007_fast_acceptance_suite.py",
    "p007_final_lock.py",
)

suite = subprocess.run([sys.executable, str(ROOT / "p007_fast_acceptance_suite.py")], cwd=str(ROOT),
                       text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
print(suite.stdout or "", end="")
assert suite.returncode == 0
assert "P007_FAST_ACCEPTANCE_OK" in (suite.stdout or "")
assert "P007_CANONICAL_ARTIFACT_COVERAGE_OK" in (suite.stdout or "")
assert "P007_CANONICAL_ARTIFACT_DRIFT_DETECTED" in (suite.stdout or "")
assert "P007_CANONICAL_ARTIFACT_REMOVAL_DETECTED" in (suite.stdout or "")

manifest_path = ROOT / "p007_baseline_manifest.json"
manifest = write_manifest(manifest_path)
verified = verify_manifest(manifest_path)
assert verified["ok"] is True, verified

hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in PROTECTED}
report = {
    "milestone": "P007", "gate": "G0_BASELINE_INTEGRITY", "status": "LOCKED",
    "schema": manifest["schema"],
    "baseline_identity_sha256": manifest["baseline_identity_sha256"],
    "baseline_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
    "functional_file_count": manifest["functional_file_count"],
    "canonical_artifact_count": manifest["canonical_artifact_count"],
    "canonical_baseline_artifacts": manifest["canonical_baseline_artifacts"],
    "git": manifest["git"], "dependencies": manifest["dependencies"], "invariants": manifest["invariants"],
    "functional_only": True, "phenomenology_undetermined": True, "protected_hashes": hashes,
}
path = ROOT / "p007_final_lock_report.json"
tmp = path.with_suffix(path.suffix + ".tmp")
tmp.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
tmp.replace(path)
print("P007_FINAL_LOCK_OK")
print("baseline_identity_sha256=" + manifest["baseline_identity_sha256"])
print("canonical_artifact_count=" + str(manifest["canonical_artifact_count"]))
