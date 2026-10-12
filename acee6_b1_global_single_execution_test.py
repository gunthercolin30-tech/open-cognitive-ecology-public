from acee6_b1h3_test_support import run_scope
for scope in (None,"ACEE6","ACEE6-B1"):
    r=run_scope(scope)
    assert r.returncode==0
    assert r.stdout.count("ACEE6_B1_FAST_ACCEPTANCE_OK")==1, scope
print("ACEE6_B1_GLOBAL_SINGLE_EXECUTION_OK")
