import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4g3_5a_dm003_replay_interface_diagnostic_v1.json").read_text())
def test_status(): assert D["status"]=="F4_G3_5A_DM003_REPLAY_INTERFACE_DIAGNOSTIC_COMPLETE"
def test_prior_abort(): assert D["prior_g3_5_scientific_experiment_executed"] is False and D["prior_g3_5_abort_class"]=="HARNESS_INTERFACE_ASSUMPTION_ERROR"
def test_mutation(): assert D["DM003"]["mutation_effective"] is True
def test_api(): assert D["DM003"]["static_checker_api"].startswith("check_profile(")
def test_static_blind(): assert D["DM003"]["static_checker_detected_missing_norm"] is False
def test_independent_hit(): assert D["DM003"]["independent_verifier_detected_missing_norm"] is True and D["DM003"]["independent_verifier_ivi3_status"]=="FAIL"
def test_count(): assert D["DM003"]["demonstrated_independent_detector_count"]==1
def test_verdict(): assert D["DM003"]["verdict"]=="INCONCLUSIVE"
def test_correction(): assert D["g3_4_correction_required"] is True and D["DM003"]["g3_4_second_oracle_assumption_falsified"] is True
def test_history(): assert D["historical_g3_3_inconclusive_preserved"] is True
def test_isolation(): assert D["production_runtime_modified"] is False and D["isolated_copy_only"] is True and D["new_detector_created"] is False and D["create_authorized"] is False
def test_next(): assert D["next_required_stage"]=="F4-G3.5B_DM003_G3_4_CLASSIFICATION_CORRECTION"
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False
