from pathlib import Path
import json
P=Path.home()/"open-cognitive-ecology/validation_artifacts/p159/occ1i/static_checker_causal_qualification_v1.json"
def d(): return json.loads(P.read_text())
def test_static_checker_causal_transition():
    x=d(); assert x["baseline"]["decision"]!="STATIC_FAIL"; assert x["baseline"]["s3"]["result"]!="FAIL"; assert x["controlled"]["decision"]=="STATIC_FAIL"; assert x["controlled"]["s3"]["result"]=="FAIL"
def test_fixture_is_attributed_to_s3():
    x=d(); assert x["fixture"]["rule_id"] in x["controlled"]["s3"]["evidence"]["bad"]; assert x["causal_attribution_established"] is True
def test_additive_history_preserved():
    x=d(); assert x["additive_evidence_only"] is True; assert x["prior_f4e_blocked_preserved"] is True; assert x["prior_f4e2_negative_diagnostic_preserved"] is True
def test_four_family_support_without_core_upgrade():
    x=d(); assert x["f4e_static_family_qualified"] is True; assert x["combined_four_family_qualification_supported"] is True; assert x["core_mutation_statuses_reclassified"] is False; assert x["empirical_core_kill_claims_created"]==0; assert x["dm045_survived_retained"] is True
def test_boundaries():
    x=d(); assert x["next_stage_allowed"]=="F4-E_CONSOLIDATION"; assert x["extended_opened"] is False; assert x["occ1i_closed"] is False; assert x["p159_final_lock"] is False; assert x["p160_opened"] is False
