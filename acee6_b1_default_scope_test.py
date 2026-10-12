from acee6_b1h3_test_support import run_scope


def exact_marker_lines(output, marker):
    return tuple(
        line
        for line in output.splitlines()
        if line.startswith(marker)
    )


r = run_scope()
assert r.returncode == 0
assert "ACEE0_FAST_ACCEPTANCE_OK" in r.stdout
assert "AW14_FAST_ACCEPTANCE_OK" in r.stdout
assert len(exact_marker_lines(r.stdout, "ACEE6_B1_FAST_ACCEPTANCE_OK")) == 1
assert len(exact_marker_lines(r.stdout, "FAST_ACCEPTANCE_ALL_OK")) == 1
print("ACEE6_B1_DEFAULT_SCOPE_OK")
