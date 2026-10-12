import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c10cr/acee_backend_post_migration_rescan.json"
def d(): return json.loads(R.read_text())
def test_runner_zero(): assert d()["acee_runner_direct_process_count"]==0
def test_acee():
 r=d(); assert r["classification_counts"]["GOVERNED_ACEE_VALIDATION_TRANSPORT"]==1 and r["acee_backend_closed_signature_verified"] is True
def test_core():
 r=d(); assert r["classification_counts"]["GOVERNED_JQ_ORACLE_TRANSPORT"]==1 and r["classification_counts"]["TRUSTED_PROCESS_TRANSPORT"]==1
def test_accounting():
 r=d(); assert sum(r["classification_counts"].values())==r["causal_process_call_count"] and r["direct_standard_process_count"]==len(r["direct_standard_process_calls"])
def test_no_closure():
 r=d(); assert r["process_bypass_zero_claimed"] is False and r["process_migration_complete"] is False and r["p162g_closure_claimed"] is False
