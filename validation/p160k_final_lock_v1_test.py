from ontology.p160_final_lock import *
def test_boundaries_and_rti(): assert len(RTI)==18 and "ELIGIBLE_CANDIDATE!=AUTHORIZED" in NON_SOVEREIGN_BOUNDARIES and "FINAL_LOCK!=AUTHORIZATION" in NON_SOVEREIGN_BOUNDARIES
def test_incomplete_without_global_validation():
 r=build_lock_record(protected_hashes={"a":"b"},evidence_hashes={"e":"f"},compiled_profile_hash="c",constitutional_snapshot_hash="s",global_validation={"passed":False},residual_risks=[],counterexamples=[],scope={},dependencies={}); assert r["status"]=="EVIDENCE_INCOMPLETE"
def test_lock_and_drift():
 r=build_lock_record(protected_hashes={"a":"b"},evidence_hashes={"e":"f"},compiled_profile_hash="c",constitutional_snapshot_hash="s",global_validation={"passed":True},residual_risks=[],counterexamples=[],scope={},dependencies={}); l=lock_candidate(r); assert verify_lock(l,{"a":"b"})["valid"] and not verify_lock(l,{"a":"X"})["valid"]
def test_invalidation(): assert invalidate_lock({"status":"LOCKED"},"drift")["status"]=="LOCK_INVALIDATED"
