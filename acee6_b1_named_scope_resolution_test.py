from acee6_b1h3_test_support import run_scope
for scope in ("ACEE6","acee6","ACEE6-B1","acee6-b1"):
    r=run_scope(scope)
    assert r.returncode == 0, (scope,r.stdout)
    assert "Unknown fast acceptance scope" not in r.stdout
    assert r.stdout.count("ACEE6_B1_FAST_ACCEPTANCE_OK")==1
print("ACEE6_B1_NAMED_SCOPE_RESOLUTION_OK")
