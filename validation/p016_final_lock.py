from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "validation_evidence"
REPORT = EVIDENCE / "p016_final_lock_report.json"

PROTECTED = (
    "ontology/dna_stack.py",
    "validation/p016_dna_stack.py",
    "validation/p016_functional_test.py",
    "validation/p016_degradation_test.py",
    "validation/p016_non_regression_test.py",
    "validation/p016_determinism_test.py",
    "validation/p016_non_mutation_test.py",
    "validation/p016_adversarial_test.py",
)

TEST_MODULES = (
    "validation.p016_dna_stack",
    "validation.p016_functional_test",
    "validation.p016_degradation_test",
    "validation.p016_non_regression_test",
    "validation.p016_determinism_test",
    "validation.p016_non_mutation_test",
    "validation.p016_adversarial_test",
)

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def run(module: str) -> None:
    proc = subprocess.run(
        [sys.executable, "-m", module],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"{module} failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )

def main():
    missing = [rel for rel in PROTECTED if not (ROOT / rel).is_file()]
    assert not missing, f"missing protected P016 files: {missing}"

    for module in TEST_MODULES:
        run(module)

    protected_hashes = {rel: sha256(ROOT / rel) for rel in PROTECTED}

    report = {
        "schema": "oce.p016.final_lock.v1",
        "milestone": "P016",
        "status": "LOCKED",
        "scope": "P016_ONLY",
        "decision": "CREATE_THIN_COMPOSITION_LAYER",
        "canonical_layers": [
            "DNA-0", "DNA-1", "DNA-2", "DNA-3", "DNA-4",
            "DNA-5", "DNA-6", "DNA-7", "DNA-X",
        ],
        "p015_modified": False,
        "unknown_promotion": False,
        "runtime_authority_extended": False,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
        "protected_hashes": protected_hashes,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    tmp = REPORT.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    tmp.replace(REPORT)

    print("P016_FINAL_LOCK_OK")
    print(f"report={REPORT}")

if __name__ == "__main__":
    main()
