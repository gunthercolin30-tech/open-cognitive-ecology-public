from pathlib import Path
import json
P=Path.home()/"open-cognitive-ecology/validation_artifacts/p159/occ1i/independent_detector_execution_harness_v1.json"
def d(): return json.loads(P.read_text())
def test_historical_f4e1_blocker_is_preserved():
    x=d(); assert x["status"]=="HARNESS_QUALIFICATION_BLOCKED"; assert x["all_controlled_fixtures_detected"] is False
def test_three_original_families_were_detected():
    x=d(); ok=[r for r in x["runs"] if r["detector_id"]!="STATIC_CONSTITUTIONAL_CHECKER"]; assert len(ok)==3; assert all(r["detected"] is True for r in ok)
def test_static_false_fixture_remains_negative_evidence():
    x=d(); r=[r for r in x["runs"] if r["detector_id"]=="STATIC_CONSTITUTIONAL_CHECKER"][0]; assert r["detected"] is False
def test_integrity_and_boundaries_preserved():
    x=d(); assert x["canonical_integrity_preserved"] is True; assert x["dm045_survived_retained"] is True; assert x["core_mutation_statuses_reclassified"] is False; assert x["p159_final_lock"] is False; assert x["p160_opened"] is False
