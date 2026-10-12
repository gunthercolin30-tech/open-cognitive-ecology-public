import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4g3_11_dm022_exact_causal_requalification_v1.json").read_text())
def test_status(): assert D["status"]=="F4_G3_11_DM022_EXACT_CAUSAL_REQUALIFICATION_COMPLETE"
def test_id(): assert D["mutation_id"]=="DM022" and D["mutation"]=="ADD_DIRECT_AUTHORIZATION_OPCODE"
def test_effective(): assert D["mutation_effective"] is True
def test_not_inherited(): assert D["historical_killed_inherited"] is False
def test_two_surfaces(): assert len(D["protective_families"])==2 and D["protective_families"][0]!=D["protective_families"][1]
def test_two_detections(): assert D["distinct_protective_detections"]==2
def test_killed(): assert D["verdict"]=="KILLED"
def test_core32(): assert D["core_killed_after_g3_11"]==32 and D["remaining_core_blockers"]==0
def test_no_runtime(): assert D["production_runtime_modified"] is False and D["isolated_model_only"] is True
def test_no_create(): assert D["new_detector_created"] is False and D["new_norm_created"] is False and D["new_authority_created"] is False and D["create_authorized"] is False
def test_next(): assert D["next_required_stage"]=="F4-G3.12_CREATE_CANDIDATE_CONSOLIDATED_QUALIFICATION"
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False
