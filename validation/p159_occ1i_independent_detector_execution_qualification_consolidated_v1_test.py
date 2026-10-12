from pathlib import Path
import json
P=Path.home()/"open-cognitive-ecology/validation_artifacts/p159/occ1i/independent_detector_execution_qualification_consolidated_v1.json"
def d(): return json.loads(P.read_text())
def test_consolidated_qualification():
    x=d(); assert x["status"]=="HARNESS_QUALIFIED_FOR_CORE_CAUSAL_RECAMPAIGN"; assert x["all_detector_families_qualified"] is True; assert x["detector_count"]==4
def test_history_is_additive_and_preserved():
    x=d(); assert x["evidence_model"]=="ADDITIVE_NON_DESTRUCTIVE"; assert x["history"]["f4e1"]["negative_result_preserved"] is True; assert x["history"]["f4e2"]["negative_diagnostic_preserved"] is True; assert x["history"]["f4e3"]["causal_resolution_preserved"] is True
def test_static_false_fixture_not_reclassified():
    x=d(); assert x["static_checker_false_fixture_not_reclassified"] is True
def test_no_core_claims_created():
    x=d(); assert x["qualification_only"] is True; assert x["core_mutation_statuses_reclassified"] is False; assert x["empirical_core_kill_claims_created"]==0; assert x["dm045_survived_retained"] is True
def test_stage_boundary():
    x=d(); assert x["next_stage_allowed"]=="F4-F"; assert x["extended_opened"] is False; assert x["occ1i_closed"] is False; assert x["p159_final_lock"] is False; assert x["p160_opened"] is False
