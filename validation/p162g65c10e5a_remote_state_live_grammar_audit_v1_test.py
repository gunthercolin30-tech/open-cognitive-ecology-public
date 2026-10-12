import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c10e5a/remote_state_live_grammar_audit.json"
def d():return json.loads(R.read_text())
def test_three():
 r=d();assert r["direct_process_count"]==3 and len(r["calls"])==3
def test_families():
 r=d();assert set(r["families"])=={"SSH","SCP"} and sum(r["families"].values())==3 and all(x["family"] in {"SSH","SCP"} for x in r["calls"])
def test_unchanged():
 r=d();assert hashlib.sha256((ROOT/r["target"]).read_bytes()).hexdigest()==r["target_sha256"]
def test_no_claim():
 r=d();assert r["migration_performed"] is False and r["contract_created"] is False and r["transport_created"] is False and r["raw_remote_command_authorized"] is False and r["execution_authority_granted"] is False and r["process_bypass_zero_claimed"] is False and r["process_migration_complete"] is False and r["p162g_closure_claimed"] is False
