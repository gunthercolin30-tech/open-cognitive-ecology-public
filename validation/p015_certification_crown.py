from __future__ import annotations
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
LOCK = ROOT / "validation_evidence" / "p015_final_lock_report.json"

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(module, cwd):
    return subprocess.run(
        [sys.executable, "-m", module],
        cwd=cwd, text=True, capture_output=True,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
    )

def check_lock_integrity():
    p = run("validation.p015_final_lock_integrity_test", ROOT)
    assert p.returncode == 0
    assert "P015_FINAL_LOCK_INTEGRITY_OK" in p.stdout

def main():
    payload = json.loads(LOCK.read_text(encoding="utf-8"))
    assert payload["milestone"] == "P015"
    assert payload["status"] == "LOCKED"
    assert payload["scope"] == "P015_ONLY"
    assert payload["unknown_promotion"] is False
    assert payload["functional_conclusion_only"] is True
    assert payload["phenomenology_undetermined"] is True
    print("P015_CERT_EVIDENTIARY_SCOPE_OK")

    protected = {rel: sha256(ROOT / rel) for rel in payload["protected_hashes"]}

    with tempfile.TemporaryDirectory(prefix="oce_p015_cwd_") as tmp:
        p = run("validation.p015_official_dna_definition", Path(tmp))
        assert p.returncode == 0
        assert "P015_OFFICIAL_DNA_DEFINITION_OK" in p.stdout
    print("P015_CERT_CWD_INDEPENDENCE_OK")

    before = {rel: sha256(ROOT / rel) for rel in protected}
    for module in (
        "validation.p015_official_dna_definition",
        "validation.p015_functional_test",
        "validation.p015_degradation_test",
        "validation.p015_non_regression_test",
        "validation.p015_non_mutation_test",
        "validation.p015_determinism_test",
        "validation.p015_adversarial_test",
        "validation.p015_final_lock_integrity_test",
    ):
        p = run(module, ROOT)
        assert p.returncode == 0, (module, p.stdout, p.stderr)
    after = {rel: sha256(ROOT / rel) for rel in protected}
    assert before == after
    print("P015_CERT_VALIDATORS_NON_MUTATING_OK")

    original_lock = LOCK.read_bytes()
    try:
        tampered = json.loads(original_lock.decode("utf-8"))
        first = next(iter(tampered["protected_hashes"]))
        tampered["protected_hashes"][first] = "0" * 64
        LOCK.write_text(json.dumps(tampered, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        p = run("validation.p015_final_lock_integrity_test", ROOT)
        assert p.returncode != 0
    finally:
        LOCK.write_bytes(original_lock)
    check_lock_integrity()
    print("P015_CERT_LOCK_REPORT_TAMPER_DETECTED")

    rel = next(iter(payload["protected_hashes"]))
    target = ROOT / rel
    original_target = target.read_bytes()
    try:
        target.write_bytes(original_target + b"\n# P015 certification tamper probe\n")
        p = run("validation.p015_final_lock_integrity_test", ROOT)
        assert p.returncode != 0
    finally:
        target.write_bytes(original_target)
    check_lock_integrity()
    print("P015_CERT_PROTECTED_FILE_TAMPER_DETECTED")

    baseline_hashes = dict(payload["protected_hashes"])
    p = run("validation.p015_final_lock", ROOT)
    assert p.returncode == 0
    replay = json.loads(LOCK.read_text(encoding="utf-8"))
    assert replay["protected_hashes"] == baseline_hashes
    assert replay["scope"] == "P015_ONLY"
    assert replay["unknown_promotion"] is False
    print("P015_CERT_LOCK_REPLAY_OK")

    check_lock_integrity()
    final = json.loads(LOCK.read_text(encoding="utf-8"))
    assert all(sha256(ROOT / rel) == expected for rel, expected in final["protected_hashes"].items())
    print("P015_CERT_FINAL_INTEGRITY_OK")
    print("P015_CERTIFICATION_CROWN_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
