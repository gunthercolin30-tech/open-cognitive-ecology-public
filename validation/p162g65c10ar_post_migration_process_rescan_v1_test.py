import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c10ar/post_migration_process_rescan.json"
def d(): return json.loads(R.read_text())
def test_accounting():
 r=d()
 assert r["causal_process_call_count"]==r["trusted_transport_count"]+r["governed_facade_count"]+r["direct_standard_process_count"]
def test_single_trusted_transport():
 r=d(); assert r["trusted_transport_count"]==1
def test_c10a_old_sites_closed():
 r=d(); assert r["c10a_old_direct_site_count"]==0
def test_remaining_direct_are_not_zero_claim():
 r=d(); assert r["process_bypass_zero_claimed"] is False
 assert r["p162g_closure_claimed"] is False
