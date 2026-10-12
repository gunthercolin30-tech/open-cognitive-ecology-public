#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
MANIFEST = ROOT / "acee6_i2_suite_manifest.json"
FINAL_LOCK = ROOT / "acee6_i2_final_lock.py"
CLOSURE_SUITE = ROOT / "acee6_i2_closure_micro_crown_suite.py"

assert MANIFEST.is_file(), MANIFEST
assert FINAL_LOCK.is_file(), FINAL_LOCK
assert CLOSURE_SUITE.is_file(), CLOSURE_SUITE

data = json.loads(MANIFEST.read_text(encoding="utf-8"))
assert data["axis"] == "ACEE6-I2"
assert data["schema_version"] == "1.0"
assert data["public_schema_version"] == "0.14.0"
assert data["canonical_identifier_policy"] == "NFC+casefold"

files = data["files"]
assert len(files) == 15, len(files)

for name, expected_hash in sorted(files.items()):
    path = ROOT / name
    assert path.is_file(), path
    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual_hash == expected_hash, (name, expected_hash, actual_hash)

final_lock_source = FINAL_LOCK.read_text(encoding="utf-8")
closure_source = CLOSURE_SUITE.read_text(encoding="utf-8")

for required in (
    "acee6_i2_suite_manifest.json",
    "acee6_i2_closure_micro_crown_suite.py",
):
    assert required in final_lock_source, required

assert (
    "acee6_i2_suite_integrity_test.py"
    in closure_source
), "closure suite does not invoke integrity test"

for required in (
    "acee6_i2_public_schema_compatibility_test.py",
    "acee6_i2_unicode_casefold_collision_test.py",
):
    assert required in closure_source, required

print("ACEE6_I2_SUITE_INTEGRITY_OK")
