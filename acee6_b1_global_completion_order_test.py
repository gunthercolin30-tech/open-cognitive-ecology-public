from acee6_b1h3_test_support import run_scope


def exact_marker_indexes(output, marker):
    return tuple(
        index
        for index, line in enumerate(output.splitlines())
        if line.startswith(marker)
    )


r = run_scope()
assert r.returncode == 0

acee6_indexes = exact_marker_indexes(r.stdout, "ACEE6_B1_FAST_ACCEPTANCE_OK")
global_indexes = exact_marker_indexes(r.stdout, "FAST_ACCEPTANCE_ALL_OK")

assert len(acee6_indexes) == 1
assert len(global_indexes) == 1
assert acee6_indexes[0] < global_indexes[0]
print("ACEE6_B1_GLOBAL_COMPLETION_ORDER_OK")
