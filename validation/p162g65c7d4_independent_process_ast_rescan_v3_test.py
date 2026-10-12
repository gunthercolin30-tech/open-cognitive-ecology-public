import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c7d4/independent_process_ast_rescan_v3.json"
def data(): return json.loads(R.read_text())
def test_single_trusted_transport():
 r=data(); assert r["trusted_transport_call_count"]==1
 assert r["trusted_transport"][0]["file"]=="ontology/governed_process_effector.py"
def test_residuals_are_explicit_not_zero_claimed():
 r=data(); assert r["direct_process_residual_call_count"]>0
 assert r["direct_process_residual_module_count"]>0
 assert r["process_bypass_zero_claimed"] is False
 assert r["process_migration_complete"] is False
def test_runner_remains_residual_backend():
 r=data(); assert any(x["file"]=="ontology/acee_validation_runner.py" and x["primitive"]=="subprocess.Popen" for x in r["direct_process_residuals"])
def test_accounting_identity():
 r=data(); assert r["ontology_process_call_count"]==r["trusted_transport_call_count"]+r["direct_process_residual_call_count"]
