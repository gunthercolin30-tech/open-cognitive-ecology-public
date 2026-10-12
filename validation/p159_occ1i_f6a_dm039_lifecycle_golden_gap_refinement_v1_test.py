from __future__ import annotations
import json
from copy import deepcopy
from pathlib import Path
from ontology import occ_golden_constitutional_vectors as g
ROOT=Path(__file__).resolve().parents[1]
A=json.loads((ROOT/"validation_artifacts/p159/occ1i/f6a_dm039_lifecycle_golden_gap_refinement_v1.json").read_text())
def profile(): return json.loads((ROOT/"validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json").read_text())
def vector(): return [x for x in g.build_extended() if x["vector_id"]=="EXT.LIFECYCLE"][0]
def test_refinement_recorded(): assert A["strategy"]=="REFINE_EXISTING_GOLDEN_LIFECYCLE_VECTOR"
def test_backup_integrity(): assert A["pre_sha256"]==A["backup_sha256"]
def test_hash_changed(): assert A["post_sha256"]!=A["pre_sha256"]
def test_same_vector(): assert A["vector_id_preserved"]=="EXT.LIFECYCLE" and A["family_preserved"]=="lifecycle"
def test_no_new_detector(): assert A["new_detector_created"] is False and A["create_authorized"] is False
def test_nominal_lifecycle_passes():
 p=profile(); v=vector(); assert g._semantic_observation(v,p)=="PASS"; assert g.run_corpus({"vectors":[v]},p)[0]["vector_verdict"]=="PASS"
def test_dm039_active_degradation_detected():
 p=deepcopy(profile()); p["profile_state"]="ACTIVE"; v=vector(); assert g._semantic_observation(v,p)=="FAIL"; assert g.run_corpus({"vectors":[v]},p)[0]["vector_verdict"]=="FAIL"
def test_self_activation_degradation_still_detected():
 p=deepcopy(profile()); p.setdefault("lifecycle_model",{})["self_activation"]=True; assert g._semantic_observation(vector(),p)=="FAIL"
def test_sealed_allowed():
 p=deepcopy(profile()); p["profile_state"]="SEALED"; p.setdefault("lifecycle_model",{})["self_activation"]=False; assert g._semantic_observation(vector(),p)=="PASS"
def test_revoked_not_falsely_active():
 p=deepcopy(profile()); p["profile_state"]="REVOKED"; p.setdefault("lifecycle_model",{})["self_activation"]=False; assert g._semantic_observation(vector(),p)=="PASS"
def test_replay_required(): assert A["causal_verdict_assigned_by_refinement"] is False and A["replay_required"] is True
def test_next(): assert A["next_required_stage"]=="F6_A_DM039_CAUSAL_REPLAY_AFTER_REFINEMENT"
def test_epistemics(): assert A["functional_conclusion_only"] is True and A["phenomenology_undetermined"] is True
def test_no_p160(): assert A["p159_final_lock"] is False and A["p160_opened"] is False
