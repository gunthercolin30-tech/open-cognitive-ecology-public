import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f4g3_12_create_candidate_consolidated_qualification_v3.json").read_text())
S={"DM003","DM015","DM017","DM018","DM022","DM033"}
def test_status(): assert D["status"]=="F4_G3_12_CREATE_CANDIDATE_CONSOLIDATED_QUALIFICATION_COMPLETE"
def test_scope(): assert set(D["scope"])==S and len(D["scope"])==6
def test_all_killed(): assert D["all_six_killed"] is True and all(D["verdicts"][x]=="KILLED" for x in S)
def test_no_create_authorized(): assert D["create_authorized_at_any_resolution"] is False
def test_no_new_primitive(): assert D["new_primitive_required"] is False
def test_no_new_norm(): assert D["new_norm_required"] is False
def test_no_new_authority(): assert D["new_authority_required"] is False
def test_no_new_detector(): assert D["new_detector_module_required"] is False
def test_policy(): assert D["resolution_policy"]=="REUSE_OR_REFINE_BEFORE_CREATE"
def test_no_consolidation_mutation(): assert D["production_runtime_modified_by_consolidation"] is False and D["historical_artifacts_modified_by_consolidation"] is False
def test_g39_strict_schema(): assert D["g3_9_schema_read_mode"]=="STRICT_ROOT_DM_OBJECTS"
def test_prior_attempts_not_proofs(): assert D["prior_g3_12_v1_v2_status"]=="ABORTED_NO_QUALIFICATION"
def test_core_identity(): assert D["core_total"]==32 and D["core_killed"]==32 and D["remaining_core_blockers"]==0
def test_g3_ready(): assert D["g3_create_candidate_resolved"] is True and D["g3_ready_for_g4"] is True
def test_evidence_hashes(): assert len(D["evidence_sha256"])==4 and all(len(v)==64 for v in D["evidence_sha256"].values())
def test_next(): assert D["next_required_stage"]=="F4-G4_CONSOLIDATED_BLOCKER_RESOLUTION_CLOSURE"
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False
