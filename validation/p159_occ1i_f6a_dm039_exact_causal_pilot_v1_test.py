import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"validation_artifacts/p159/occ1i/f6a_dm039_exact_causal_pilot_v1.json").read_text())
def test_identity(): assert D["mutation_id"]=="DM039" and D["transformation"]=="SEALED_OR_REVOKED_TO_ACTIVE"
def test_mroot(): assert D["criticality"]=="MROOT" and D["minimum_distinct_detectors"]==2
def test_isolated(): assert D["isolated_copy_only"] is True and D["production_runtime_modified"] is False
def test_effective(): assert D["mutation_effective"] is True
def test_normal_guard(): assert D["normal_transition"]["status"]=="FAIL"
def test_static_detects(): assert D["protective_families"]["static_constitutional_checks"]["detected"] is True
def test_static_verify(): assert D["static_profile_verification"]["status"]=="FAIL"
def test_golden_recorded(): assert D["golden_lifecycle_vector"]["vector_id"]=="EXT.LIFECYCLE"
def test_count_consistent(): assert D["distinct_protective_detections"]==sum(1 for x in D["protective_families"].values() if x["detected"])
def test_verdict_rule(): assert D["causal_verdict"]==("KILLED" if D["distinct_protective_detections"]>=2 else "INCONCLUSIVE")
def test_refine_rule(): assert D["refinement_required"]==(D["causal_verdict"]!="KILLED")
def test_no_create(): assert D["create_authorized"] is False and D["new_detector_created"] is False
def test_hashes(): assert all(len(x)==64 for x in D["evidence_sha256"].values())
def test_scope(): assert D["causal_claim_limited_to_dm039"] is True
def test_epistemics(): assert D["functional_conclusion_only"] is True and D["phenomenology_undetermined"] is True and D["p159_final_lock"] is False and D["p160_opened"] is False
