import json
from pathlib import Path
ROOT=Path(__file__).parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4f1b5_3b3_dm038_dm042_residual_diagnostic_v1.json").read_text())
def cs(): return {x["mutation_id"]:x for x in D["cases"]}
def test_scope(): assert set(cs())=={"DM038","DM042"}
def test_dm038(): assert cs()["DM038"]["diagnosis"]=="SCENARIO_SEMANTICS_MISMATCH" and cs()["DM038"]["historical_cnp_detection"] is True
def test_dm042(): assert cs()["DM042"]["diagnosis"]=="SCENARIO_STIMULUS_MISSING" and cs()["DM042"]["existing_hash_tamper_scenario"] is True
def test_no_new_detector(): assert D["summary"]["new_detectors_required"]==0 and D["create_authorized"] is False
def test_no_status_change(): assert D["mutation_statuses_changed"] is False and all(x["current_status"]=="INCONCLUSIVE" for x in D["cases"])
def test_next(): assert D["f4_f1b_5_3b3"]=="DONE" and D["f4_f1b_5_3b4"]=="NEXT"
def test_epistemic(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True
