import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c8b/contextual_process_classification.json"
def d(): return json.loads(R.read_text())
def test_closed_accounting():
 r=d(); assert r["source_count"]==34; assert r["contextually_classified_count"]==34
 assert sum(r["family_counts"].values())==34; assert r["unresolved_count"]==0
def test_mediated_aliases_recognized():
 r=d(); assert r["already_mediated_count"]>0
 assert any(x["contextual_family"]=="ALREADY_MEDIATED_GIT" for x in r["classified_residuals"])
def test_true_direct_accounting():
 r=d(); assert r["true_direct_residual_count"]==r["source_count"]-r["already_mediated_count"]
 assert r["true_direct_residual_count"]>0
def test_no_premature_closure():
 r=d(); assert r["migration_performed"] is False
 assert r["process_bypass_zero_claimed"] is False
 assert r["p162g_closure_claimed"] is False
