from pathlib import Path
from acee6_b1h3_test_support import ROOT, run_scope
suite=ROOT/"acee6_b1_fast_acceptance_suite.py"
original=suite.read_text(encoding="utf-8")
try:
    suite.write_text('raise AssertionError("forced ACEE6-B1 failure")\n',encoding="utf-8")
    r=run_scope("ACEE6")
    assert r.returncode != 0
    assert "FAST_ACCEPTANCE_ALL_OK" not in r.stdout
finally:
    suite.write_text(original,encoding="utf-8")
print("ACEE6_B1_GLOBAL_FAILURE_PROPAGATION_OK")
