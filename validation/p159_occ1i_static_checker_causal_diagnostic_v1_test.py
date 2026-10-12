from pathlib import Path
import json
P=Path.home()/"open-cognitive-ecology/validation_artifacts/p159/occ1i/static_checker_causal_diagnostic_v1.json"
def d(): return json.loads(P.read_text())
def test_diagnostic_complete():
    x=d(); assert x["status"]=="DIAGNOSTIC_COMPLETE"; assert x["diagnostic_only"] is True
def test_before_after_captured():
    x=d(); assert "decision" in x["baseline"]; assert "decision" in x["controlled"]; assert isinstance(x["baseline"]["findings"],list); assert isinstance(x["controlled"]["findings"],list)
def test_delta_is_explicit():
    x=d(); assert x["delta"]["introduced_count"]==len(x["delta"]["introduced"]); assert x["delta"]["removed_count"]==len(x["delta"]["removed"])
def test_no_qualification_or_core_reclassification():
    x=d(); assert x["f4e_qualification_changed"] is False; assert x["core_mutation_statuses_reclassified"] is False; assert x["empirical_core_kill_claims_created"]==0; assert x["dm045_survived_retained"] is True
def test_boundaries():
    x=d(); assert x["next_stage_allowed"]=="F4-E2_ANALYSIS"; assert x["extended_opened"] is False; assert x["occ1i_closed"] is False; assert x["p159_final_lock"] is False; assert x["p160_opened"] is False
