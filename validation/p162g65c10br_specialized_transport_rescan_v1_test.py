import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c10br/specialized_transport_rescan.json"
def d(): return json.loads(R.read_text())
def test_occ_closed(): assert d()["old_occ_direct_subprocess_count"]==0
def test_jq_transport():
 r=d(); assert r["classification_counts"]["GOVERNED_JQ_ORACLE_TRANSPORT"]==1
 assert r["jq_specialized_transport_signature_verified"] is True
def test_trusted(): assert d()["classification_counts"]["TRUSTED_PROCESS_TRANSPORT"]==1
def test_accounting():
 r=d(); assert sum(r["classification_counts"].values())==r["causal_process_call_count"]
 assert r["direct_standard_process_count"]==len(r["direct_standard_process_calls"])
def test_no_closure():
 r=d(); assert r["process_bypass_zero_claimed"] is False
 assert r["process_migration_complete"] is False and r["p162g_closure_claimed"] is False
