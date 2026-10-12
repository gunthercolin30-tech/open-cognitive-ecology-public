from acee6_b1h3_test_support import run_scope, read_report
r=run_scope("ACEE6")
assert r.returncode==0
report=read_report()
matches=[s for s in report["suites"] if s["name"]=="acee6_b1_fast_acceptance_suite.py"]
assert len(matches)==1
entry=matches[0]
assert entry["status"]=="passed"
assert entry["returncode"]==0
assert entry["marker"]=="ACEE6_B1_FAST_ACCEPTANCE_OK"
assert entry["duration_seconds"]>=0
print("ACEE6_B1_GLOBAL_REPORT_BINDING_OK")
