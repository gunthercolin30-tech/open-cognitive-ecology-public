from __future__ import annotations

import importlib

from acee6_b1h3_test_support import run_scope

vm = importlib.import_module("validation.main")


def exact_marker_indexes(output, marker):
    return tuple(
        index
        for index, line in enumerate(output.splitlines())
        if line.startswith(marker)
    )


assert vm.ACEE6_ALIASES == frozenset({"ACEE6", "acee6", "ACEE6-B1", "acee6-b1"})
assert vm.ACEE6_SUITE == "acee6_b1_fast_acceptance_suite.py"
assert vm.ACEE6_MARKER == "ACEE6_B1_FAST_ACCEPTANCE_OK"

for scope in sorted(vm.ACEE6_ALIASES):
    result = run_scope(scope)
    assert result.returncode == 0, (scope, result.stdout)
    assert "Unknown fast acceptance scope" not in result.stdout
    assert len(exact_marker_indexes(result.stdout, vm.ACEE6_MARKER)) == 1

unknown = run_scope("does_not_exist_acee6_scope")
assert unknown.returncode != 0
assert "Unknown fast acceptance scope" in unknown.stdout
assert not exact_marker_indexes(unknown.stdout, vm.ACEE6_MARKER)

global_result = run_scope(None)
assert global_result.returncode == 0

acee6_indexes = exact_marker_indexes(global_result.stdout, vm.ACEE6_MARKER)
global_indexes = exact_marker_indexes(global_result.stdout, vm.GLOBAL_MARKER)

assert len(acee6_indexes) == 1
assert len(global_indexes) == 1
assert acee6_indexes[0] < global_indexes[0]

print("ACEE6_GLOBAL_VALIDATION_SCOPE_OK")
