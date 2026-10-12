#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "fast_acceptance.py"
source = TARGET.read_text(encoding="utf-8")
assert "(?P<substeps>" in source
assert "_natural_substep_key" in source
assert "guard_file(ROOT / script)" in source
assert "validation.main" not in source
spec = importlib.util.spec_from_file_location("fa_lock", TARGET)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
suites = module.discover_suites()
required = ["ay1_d1_fast_acceptance_suite.py", "ay1_d1b_fast_acceptance_suite.py", "ay1_d1c_fast_acceptance_suite.py"]
for name in required:
    assert suites["ay"].count(name) == 1
    assert not module.guard_file(ROOT / name), name
order = ["ay0_fast_acceptance_suite.py", "ay1_fast_acceptance_suite.py"] + required
assert [suites["ay"].index(n) for n in order] == sorted(suites["ay"].index(n) for n in order)
print("AY1_D1C_VALIDATION_HARNESS_FINAL_LOCK_OK")
