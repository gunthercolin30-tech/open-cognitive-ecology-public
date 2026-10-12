from acee6_b1h3_test_support import run_scope
r=run_scope("DOES_NOT_EXIST")
assert r.returncode != 0
assert "Unknown fast acceptance scope" in r.stdout
assert "ACEE6_B1_FAST_ACCEPTANCE_OK" not in r.stdout
assert "FAST_ACCEPTANCE_ALL_OK" not in r.stdout
print("ACEE6_B1_UNKNOWN_SCOPE_FAIL_CLOSED_OK")
