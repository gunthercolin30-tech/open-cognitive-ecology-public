from __future__ import annotations

import importlib

vm = importlib.import_module("validation.main")

assert vm.ACEE6_ALIASES == frozenset({"ACEE6", "acee6", "ACEE6-B1", "acee6-b1"})
assert vm.ACEE6_SUITE == "acee6_b1_fast_acceptance_suite.py"
assert vm.ACEE6_MARKER == "ACEE6_B1_FAST_ACCEPTANCE_OK"
assert vm.GLOBAL_MARKER == "FAST_ACCEPTANCE_ALL_OK"
assert callable(vm._fast_validation)
assert callable(vm._write_fast_report)

print("ACEE6_B1H3_GLOBAL_VALIDATION_SEMANTICS_FINAL_LOCK_OK")
