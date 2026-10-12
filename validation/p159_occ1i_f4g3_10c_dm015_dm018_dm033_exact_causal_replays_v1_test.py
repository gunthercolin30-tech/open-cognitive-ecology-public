import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4g3_10c_dm015_dm018_dm033_exact_causal_replays_v1.json").read_text())
def test_status(): assert D["status"]=="F4_G3_10C_DM015_DM018_DM033_EXACT_CAUSAL_REPLAYS_COMPLETE"
def test_effective(): assert all(D["results"][x]["mutation_effective"] is True for x in ("DM015","DM018","DM033"))
def test_first_family(): assert all(D["results"][x]["production_first_family_status"]=="FAIL" for x in D["results"])
def test_weakened_passes(): assert all(D["results"][x]["isolated_weakened_first_family_status"]=="PASS" for x in D["results"])
def test_second_family(): assert all(D["results"][x]["second_family_status"]=="FAIL" for x in D["results"])
def test_independent_modules(): assert all(D["results"][x]["independent_module_surfaces"] is True for x in D["results"])
def test_two_detections(): assert all(D["results"][x]["distinct_protective_detections"]==2 for x in D["results"])
def test_verdicts(): assert all(D["results"][x]["verdict"]=="KILLED" for x in D["results"])
def test_all_three(): assert D["all_three_killed"] is True
def test_no_runtime_change(): assert D["production_runtime_modified"] is False and D["isolated_copy_only"] is True
def test_no_create(): assert D["new_detector_created"] is False and D["create_authorized"] is False
def test_next(): assert D["next_required_stage"]=="F4-G3.11_DM022_EXACT_CAUSAL_REQUALIFICATION"
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False
