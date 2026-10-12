from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
REPORT = ROOT / "validation_evidence" / "p017_final_lock_report.json"

PROTECTED = (
    "ontology/dna_registry.py",
    "validation/p017_dna_registry.py",
    "validation/p017_functional_test.py",
    "validation/p017_degradation_test.py",
    "validation/p017_non_regression_test.py",
    "validation/p017_determinism_test.py",
    "validation/p017_non_mutation_test.py",
    "validation/p017_provenance_version_test.py",
    "validation/p017_adversarial_test.py",
)

TESTS = (
    "validation.p017_dna_registry",
    "validation.p017_functional_test",
    "validation.p017_degradation_test",
    "validation.p017_non_regression_test",
    "validation.p017_determinism_test",
    "validation.p017_non_mutation_test",
    "validation.p017_provenance_version_test",
    "validation.p017_adversarial_test",
)

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    missing = [rel for rel in PROTECTED if not (ROOT / rel).is_file()]
    assert not missing, f"missing protected artifacts: {missing}"

    test_results = {}
    for module in TESTS:
        proc = subprocess.run(
            [sys.executable, "-m", module],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        test_results[module] = {
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip().splitlines()[-1:] if proc.stdout.strip() else [],
            "stderr_present": bool(proc.stderr.strip()),
        }
        assert proc.returncode == 0, (
            module,
            proc.stdout,
            proc.stderr,
        )

    protected_hashes = {
        rel: sha256(ROOT / rel)
        for rel in sorted(PROTECTED)
    }

    report = {
        "schema": "oce.p017.final_lock.v1",
        "milestone": "P017",
        "status": "LOCKED",
        "scope": "P017_ONLY",
        "decision": "CREATE_THIN_DNA_REGISTRY",
        "protected_hashes": protected_hashes,
        "test_results": test_results,
        "unknown_promotion": False,
        "runtime_authority_extended": False,
        "p015_modified_by_lock": False,
        "p016_modified_by_lock": False,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("P017_FINAL_LOCK_OK")
    print(f"report={REPORT}")

if __name__ == "__main__":
    main()
