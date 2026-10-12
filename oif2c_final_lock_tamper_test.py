from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path.home() / "open-cognitive-ecology"
LOCK = ROOT / "oif2c_json_schema_yaml_final_lock.py"
REPORT = ROOT / "oif2c_json_schema_yaml_final_lock_report.json"
SCHEMA = ROOT / "oif" / "schemas" / "oif_interface_schema_v1.json"
YAML_EXAMPLE = ROOT / "oif" / "schemas" / "examples" / "minimal_interface.yaml"
SERIALIZATION = ROOT / "oif" / "interface" / "serialization.py"


def execute_lock():
    return subprocess.run(
        [sys.executable, str(LOCK)],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=1800,
    )


def require_lock_success():
    run = execute_lock()
    if run.returncode:
        raise AssertionError("Final Lock failed unexpectedly:\n%s" % run.stdout)
    return json.loads(REPORT.read_text(encoding="utf-8"))


def bound_hashes(report):
    return dict(report["bound_files"])


baseline = require_lock_success()
baseline_lock = baseline["lock_sha256"]
baseline_hashes = bound_hashes(baseline)
baseline_report_bytes = REPORT.read_bytes()

with tempfile.TemporaryDirectory(prefix="oce-oif2c-tamper.") as td:
    td = Path(td)

    # 1. Destructive schema tamper: fast acceptance must fail closed.
    schema_backup = td / "schema.bak"
    shutil.copy2(SCHEMA, schema_backup)
    try:
        with SCHEMA.open("ab") as handle:
            handle.write(b"\nOIF2C_INVALID_JSON_TAMPER\n")
        tampered_hash = hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
        assert tampered_hash != baseline_hashes[str(SCHEMA.relative_to(ROOT))]
        failed = execute_lock()
        if failed.returncode == 0:
            raise AssertionError("invalid JSON schema tamper was accepted")
        # A failed lock must not replace the previously valid report.
        assert REPORT.read_bytes() == baseline_report_bytes
    finally:
        shutil.copy2(schema_backup, SCHEMA)

    restored = require_lock_success()
    assert restored["lock_sha256"] == baseline_lock
    assert bound_hashes(restored) == baseline_hashes

    # 2. Semantically inert textual tampers: lock succeeds but proves drift.
    for index, target in enumerate((YAML_EXAMPLE, SERIALIZATION), start=1):
        relative = str(target.relative_to(ROOT))
        backup = td / ("%d.bak" % index)
        shutil.copy2(target, backup)
        try:
            with target.open("ab") as handle:
                handle.write(b"\n# OIF2C_INERT_TAMPER_TEST\n")

            current_hash = hashlib.sha256(target.read_bytes()).hexdigest()
            assert current_hash != baseline_hashes[relative]

            tampered = require_lock_success()
            tampered_hashes = bound_hashes(tampered)
            assert tampered_hashes[relative] == current_hash
            assert tampered_hashes[relative] != baseline_hashes[relative]
            assert tampered["lock_sha256"] != baseline_lock
        finally:
            shutil.copy2(backup, target)

        restored = require_lock_success()
        assert bound_hashes(restored)[relative] == baseline_hashes[relative]
        assert restored["lock_sha256"] == baseline_lock

print("OIF2C_FINAL_LOCK_TAMPER_HYBRID_OK")
