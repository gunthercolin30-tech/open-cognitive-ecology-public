#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent

def load(root: Path):
    spec = importlib.util.spec_from_file_location("fa_deg", ROOT / "fast_acceptance.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module

with tempfile.TemporaryDirectory(prefix="ay1d1c_deg_") as tmp:
    fixture = Path(tmp)
    accepted = {"ay1_fast_acceptance_suite.py", "ay1_d1_fast_acceptance_suite.py", "ay1_d1b_fast_acceptance_suite.py"}
    rejected = {"ay1_d_fast_acceptance_suite.py", "ay1_dX_fast_acceptance_suite.py", "ay1__d1_fast_acceptance_suite.py", "ay1_d1_fast_acceptance_suite.txt", "ay1_d1_nested_fast_acceptance_suite.py"}
    for name in accepted | rejected:
        (fixture / name).write_text("print('OK')\n", encoding="utf-8")
    discovered = set(load(fixture).discover_suites()["ay"])
    assert accepted <= discovered, discovered
    assert not (rejected & discovered), discovered
print("AY1_D1C_VALIDATION_HARNESS_DEGRADATION_OK")
