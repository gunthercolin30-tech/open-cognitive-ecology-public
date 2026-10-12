import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c9c/standard_subprocess_effect_classification.json"
def d(): return json.loads(R.read_text())
def test_accounting():
 r=d(); assert r["source_standard_subprocess_count"]==len(r["classified_calls"])
 assert sum(r["family_counts"].values())==r["source_standard_subprocess_count"]
def test_remote_effect_not_collapsed_to_probe():
 r=d()
 remote=[x for x in r["classified_calls"] if x["family"]=="REMOTE_STATE_EFFECT"]
 assert remote
 assert all(x["effect_semantics"]=="CAUSAL_REMOTE_EFFECT" for x in remote)
def test_runner_explicit():
 assert any(x["family"]=="ACEE_VALIDATION_BACKEND" for x in d()["classified_calls"])
def test_no_migration_or_closure():
 r=d(); assert r["migration_performed"] is False
 assert r["process_bypass_zero_claimed"] is False
 assert r["p162g_closure_claimed"] is False
