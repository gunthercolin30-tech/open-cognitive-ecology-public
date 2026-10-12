from acee6_b1h3_test_support import run_scope
r=run_scope("ACEE6")
assert r.returncode==0
assert "ACEE6_B1_FAST_ACCEPTANCE_OK" in r.stdout
assert "ACEE0_FAST_ACCEPTANCE_OK" not in r.stdout
assert "AW14_FAST_ACCEPTANCE_OK" not in r.stdout
print("ACEE6_B1_SCOPE_ISOLATION_OK")
