import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c10e5b1/remote_state_parameter_provenance_audit.json"
def d(): return json.loads(R.read_text())
def test_all_parameters_have_provenance():
 r=d(); assert set(r["parameter_assignments"])=={"ssh_options","scp_options","target","remote_dir","remote_file"}
 assert all(r["parameter_assignments"][k] for k in r["parameter_assignments"])
def test_three_effect_lines_one_container():
 r=d(); assert len(r["remote_process_lines"])==3 and r["remote_effect_container"]["name"]
def test_source_unchanged():
 r=d(); assert hashlib.sha256((ROOT/r["target"]).read_bytes()).hexdigest()==r["target_sha256"]
def test_no_inference_or_power():
 r=d(); assert r["target_modified"] is False and r["contract_created"] is False and r["transport_created"] is False
 assert r["bounds_inferred"] is False and r["execution_authority_granted"] is False
 assert r["process_bypass_zero_claimed"] is False and r["process_migration_complete"] is False and r["p162g_closure_claimed"] is False
