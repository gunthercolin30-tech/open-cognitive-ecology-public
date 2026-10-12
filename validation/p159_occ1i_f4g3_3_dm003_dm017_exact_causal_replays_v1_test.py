import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4g3_3_dm003_dm017_exact_causal_replays_v1.json").read_text())
def test_status(): assert D["status"]=="F4_G3_3_DM003_DM017_EXACT_CAUSAL_REPLAYS_COMPLETE"
def test_threshold(): assert D["minimum_distinct_detectors"]==2
def test_dm003_effective(): assert D["DM003"]["mutation_effective"] is True and D["DM003"]["ivi3_status"]=="FAIL"
def test_dm003_honest(): assert D["DM003"]["distinct_protective_detections"]==1 and D["DM003"]["verdict"]=="INCONCLUSIVE"
def test_dm017_effective(): assert D["DM017"]["mutation_effective"] is True and D["DM017"]["production_one_party_status"]=="FAIL" and D["DM017"]["degraded_one_party_status"]=="PASS"
def test_dm017_honest(): assert D["DM017"]["distinct_protective_detections"]==1 and D["DM017"]["verdict"]=="INCONCLUSIVE"
def test_residual(): assert D["residual_mutations"]==["DM003","DM017"]
def test_isolated(): assert D["production_runtime_modified"] is False and D["isolated_copy_only"] is True
def test_no_create(): assert D["new_detector_created"] is False and D["create_authorized"] is False
def test_no_promotion(): assert D["historical_states_preserved"] is True and D["unresolved_promoted"] is False and D["inconclusive_promoted"] is False
def test_next(): assert D["next_required_stage"]=="F4-G3.4_DM003_DM017_INDEPENDENT_DETECTOR_SURFACE_REFINEMENT"
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False
