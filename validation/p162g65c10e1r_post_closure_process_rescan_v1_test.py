import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c10e1r/post_closure_process_rescan.json"
def d(): return json.loads(R.read_text())
def test_collab_zero():
 r=d(); assert r["external_collaboration_direct_process_count"]==0 and r["external_collaboration_command_space_closed"] is True
def test_transports():
 c=d()["classification_counts"]; assert c["GOVERNED_ACEE_VALIDATION_TRANSPORT"]==1 and c["GOVERNED_JQ_ORACLE_TRANSPORT"]==1 and c["TRUSTED_PROCESS_TRANSPORT"]==1
def test_accounting():
 r=d(); assert sum(r["classification_counts"].values())==r["causal_process_call_count"] and r["direct_standard_process_count"]==len(r["direct_standard_process_calls"])
def test_no_claim():
 r=d(); assert r["snapshot_counts_are_observations_not_authority"] is True and r["process_bypass_zero_claimed"] is False and r["process_migration_complete"] is False and r["p162g_closure_claimed"] is False
