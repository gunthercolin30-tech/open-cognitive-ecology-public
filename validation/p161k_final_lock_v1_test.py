from ontology.p161_final_lock import *
def base(**kw):
 d=dict(protected_hashes={"a":"b"},evidence_hashes={"e":"f"},p160_lock_hash="p",compiled_profile_hash="c",constitutional_snapshot_hash="s",i_report={"root_total":25,"root_pass":25,"root_violated":0,"root_inconclusive":0,"root_skipped":0,"positive_total":10,"positive_pass":10,"status":"PASS"},j_report={"ROOT_SURVIVED":0,"ROOT_INCONCLUSIVE":0,"META_TEST_FAILURE":0,"CONTROL_MUTANT_FAILURE":0,"MUTATION_CONTAMINATION":0,"status":"PASS"},concurrency_report={"total":11,"pass_count":11,"status":"PASS"},global_validation={"passed":True},contract={"unknown_rule":"UNKNOWN_NEVER_GRANTS_EXECUTION"},scope={},residual_risks=[],counterexamples=[]);d.update(kw);return d
def test_candidate_and_lock():r=build_lock_record(**base());assert r["status"]=="LOCK_CANDIDATE";l=lock_candidate(r);assert verify_lock(l,{"a":"b"})["valid"]
def test_root_blockers():r=build_lock_record(**base(i_report={**base()["i_report"],"root_inconclusive":1}));assert r["status"]=="EVIDENCE_INCOMPLETE" and "ROOT_I_INCONCLUSIVE" in r["blockers"]
def test_mutation_blockers():r=build_lock_record(**base(j_report={**base()["j_report"],"ROOT_SURVIVED":1}));assert "ROOT_MUTANT_SURVIVED" in r["blockers"]
def test_positive_liveness_blocker():r=build_lock_record(**base(i_report={**base()["i_report"],"positive_pass":9}));assert "POSITIVE_CONTROL_FAILURE" in r["blockers"]
def test_concurrency_blocker():r=build_lock_record(**base(concurrency_report={"total":11,"pass_count":10,"status":"FAIL"}));assert "CONCURRENCY_CROWN_FAILED" in r["blockers"]
def test_drift_invalidates():l=lock_candidate(build_lock_record(**base()));assert verify_lock(l,{"a":"X"})["status"]=="LOCK_INVALIDATED"
def test_non_sovereign_boundaries():assert "FINAL_LOCK!=AUTHORIZATION" in NON_SOVEREIGN_BOUNDARIES and "AUTHORIZATION_TOKEN!=EXECUTION" in NON_SOVEREIGN_BOUNDARIES
def test_explicit_invalidation():assert invalidate_lock({"status":"LOCKED"},"drift")["status"]=="LOCK_INVALIDATED"
