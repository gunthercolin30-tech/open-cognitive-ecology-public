import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c10e5b2/remote_state_input_bounds_provenance.json"
def d():return json.loads(R.read_text())
def test_inputs():
 r=d();assert all(x in r["method"]["parameters"] for x in ["user","host","remote_root","timeout_seconds"]);assert all(r["parameter_bindings"][x] for x in ["user","host","remote_root","timeout_seconds"])
def test_calls():assert len(d()["call_sites"])>=1
def test_unchanged():
 r=d();assert hashlib.sha256((ROOT/r["target"]).read_bytes()).hexdigest()==r["target_sha256"]
def test_limits():
 r=d();assert r["semantic_bounds_proven"] is False and r["new_bounds_introduced"] is False and r["target_modified"] is False and r["contract_created"] is False and r["transport_created"] is False and r["execution_authority_granted"] is False and r["process_bypass_zero_claimed"] is False and r["process_migration_complete"] is False and r["p162g_closure_claimed"] is False
