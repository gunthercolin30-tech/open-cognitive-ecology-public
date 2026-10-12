from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
OUT = ROOT / "validation_evidence" / "p015_final_lock_report.json"

TESTS = (
    "validation.p015_official_dna_definition",
    "validation.p015_functional_test",
    "validation.p015_degradation_test",
    "validation.p015_non_regression_test",
    "validation.p015_non_mutation_test",
    "validation.p015_determinism_test",
    "validation.p015_adversarial_test",
)
PROTECTED = (
    "ontology/minimal_dna.py",
    "validation/p015_official_dna_definition.py",
    "validation/p015_functional_test.py",
    "validation/p015_degradation_test.py",
    "validation/p015_non_regression_test.py",
    "validation/p015_non_mutation_test.py",
    "validation/p015_determinism_test.py",
    "validation/p015_adversarial_test.py",
)

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    results = {}
    for module in TESTS:
        p = subprocess.run(
            [sys.executable, "-m", module],
            cwd=ROOT, text=True, capture_output=True
        )
        results[module] = {
            "returncode": p.returncode,
            "last_stdout_line": p.stdout.strip().splitlines()[-1] if p.stdout.strip() else "",
            "stderr": p.stderr.strip(),
        }
        if p.returncode != 0:
            print(p.stdout)
            print(p.stderr, file=sys.stderr)
            raise SystemExit("P015_FINAL_LOCK_FAIL")

    hashes = {rel: sha256(ROOT / rel) for rel in PROTECTED}
    payload = {
        "milestone": "P015",
        "gate": "G2 DNA Fundamental",
        "status": "LOCKED",
        "schema": "oce.w2.p015.final_lock.v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "P015_ONLY",
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
        "unknown_promotion": False,
        "evidentiary_limit": "P015 semantic/structural definition only; no end-to-end enforcement claim",
        "tests": results,
        "protected_hashes": hashes,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("P015_FINAL_LOCK_OK")
    print("report=" + str(OUT))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
