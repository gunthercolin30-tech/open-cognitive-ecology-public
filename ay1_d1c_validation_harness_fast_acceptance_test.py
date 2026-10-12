#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent

def load(root: Path):
    spec = importlib.util.spec_from_file_location("fa_test", ROOT / "fast_acceptance.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module

with tempfile.TemporaryDirectory(prefix="ay1d1c_") as tmp:
    fixture = Path(tmp)
    names = ["ay1_d1c_fast_acceptance_suite.py", "ay0_fast_acceptance_suite.py", "ay1_fast_acceptance_suite.py", "ay1_d1b_fast_acceptance_suite.py", "ay1_d1_fast_acceptance_suite.py"]
    for name in names:
        (fixture / name).write_text("print('OK')\n", encoding="utf-8")
    suites = load(fixture).discover_suites()
    expected = ["ay0_fast_acceptance_suite.py", "ay1_fast_acceptance_suite.py", "ay1_d1_fast_acceptance_suite.py", "ay1_d1b_fast_acceptance_suite.py", "ay1_d1c_fast_acceptance_suite.py"]
    assert suites["ay"] == expected, suites["ay"]
    assert suites["all"] == expected, suites["all"]
    assert len(suites["ay"]) == len(set(suites["ay"]))
print("AY1_D1C_VALIDATION_HARNESS_FAST_ACCEPTANCE_OK")
