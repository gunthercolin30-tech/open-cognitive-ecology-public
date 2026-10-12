#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent

def load(root: Path):
    spec = importlib.util.spec_from_file_location("fa_nr", ROOT / "fast_acceptance.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module

legacy = ["acee0_fast_acceptance_suite.py", "acee1_fast_acceptance_suite.py", "al1_fast_acceptance_suite.py", "al2_fast_acceptance_suite.py", "ap_axis_fast_acceptance_suite.py", "ap9_fast_acceptance_suite.py", "ap10_fast_acceptance_suite.py", "ay0_fast_acceptance_suite.py", "ay1_fast_acceptance_suite.py"]
with tempfile.TemporaryDirectory(prefix="ay1d1c_nr_") as tmp:
    fixture = Path(tmp)
    added = ["ay1_d1_fast_acceptance_suite.py", "ay1_d1b_fast_acceptance_suite.py", "ay1_d1c_fast_acceptance_suite.py"]
    for name in legacy + added:
        (fixture / name).write_text("print('OK')\n", encoding="utf-8")
    suites = load(fixture).discover_suites()
    for scope in ("acee", "al", "ap"):
        assert suites[scope] == [n for n in legacy if n.startswith(scope)]
    assert suites["ay"] == [n for n in legacy if n.startswith("ay")] + added
    flattened = [n for axis in sorted(k for k in suites if k != "all") for n in suites[axis]]
    assert suites["all"] == flattened
print("AY1_D1C_VALIDATION_HARNESS_NON_REGRESSION_OK")
