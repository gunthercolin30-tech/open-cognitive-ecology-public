#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,sys
from ontology.p161_final_lock import build_lock_record,lock_candidate,sha256_file
from validation.p161i_authorization_defensive_crown_v1 import run_canonical_root_crown
from validation.p161j_semantic_mutation_crown_v1 import run_canonical_mutation_campaign
from validation.p161j_race_final_compare_crown_v1 import run_canonical_concurrency_crown
ROOT=Path.home()/"open-cognitive-ecology";OUT=ROOT/"validation_artifacts"/"p161"/"p161k";OUT.mkdir(parents=True,exist_ok=True)
PROTECTED=[
"ontology/p161_authorization_request.py","ontology/p161_normative_decision_verification.py","ontology/p161_authority_revalidation.py","ontology/p161_approval_consent_quorum_evidence.py","ontology/p161_human_decision_integrity.py","ontology/p161_authorization_scope_construction.py","ontology/p161_authorization_token_binding.py","ontology/p161_authorization_token_lifecycle.py","ontology/p161_authorization_token_persistence.py",
"validation/p161i_authorization_defensive_crown_v1.py","validation/p161j_semantic_mutation_crown_v1.py","validation/p161j_race_final_compare_crown_v1.py","validation/p161_pre_k_canonical_completion_audit_v1_test.py"]
for rel in PROTECTED:
 if not (ROOT/rel).is_file():raise SystemExit("MISSING:"+rel)
p160=ROOT/"validation_artifacts/p160/p160k/final_lock_manifest.json"
if not p160.is_file():raise SystemExit("P160_FINAL_LOCK_MISSING")
p160j=json.loads(p160.read_text(encoding="utf-8"))
if p160j.get("status")!="LOCKED":raise SystemExit("P160_NOT_LOCKED")
i=run_canonical_root_crown();j=run_canonical_mutation_campaign();c=run_canonical_concurrency_crown()
cp= subprocess.run([sys.executable,"-m","pytest","-q","validation/p161_pre_k_canonical_completion_audit_v1_test.py","-k","not p161_k_and_p162_still_unopened"],cwd=ROOT,text=True,capture_output=True)
prelog=cp.stdout+"\n"+cp.stderr;(OUT/"pre_k_validation.log").write_text(prelog,encoding="utf-8")
if cp.returncode:print(prelog);raise SystemExit("PRE_K_VALIDATION_FAILED")
gv=subprocess.run([sys.executable,"-m","validation.main"],cwd=ROOT,text=True,capture_output=True)
glog=gv.stdout+"\n"+gv.stderr;(OUT/"global_validation.log").write_text(glog,encoding="utf-8")
passed=gv.returncode==0 and "FAST_ACCEPTANCE_ALL_OK" in glog
if not passed:print(glog[-4000:]);raise SystemExit("GLOBAL_VALIDATION_FAILED")
protected={x:sha256_file(ROOT/x) for x in PROTECTED}
evidence={}
for rel in ["validation/p161_afgh_canonical_completion_v1_test.py","validation/p161i_canonical_root_crown_v2_test.py","validation/p161i_authorization_defensive_crown_v1_test.py","validation/p161j_canonical_completion_v2_test.py","validation/p161j_mutation_persistence_concurrency_v1_test.py","validation/p161j_race_final_compare_crown_v1_test.py"]:
 evidence[rel]=sha256_file(ROOT/rel)
evidence["validation_artifacts/p161/p161k/pre_k_validation.log"]=sha256_file(OUT/"pre_k_validation.log")
evidence["validation_artifacts/p161/p161k/global_validation.log"]=sha256_file(OUT/"global_validation.log")
contract={"schema":"oce.p161.p162.contract.v1","token_schema":"oce.p161.authorization_token.v1","required_verifications":["token_integrity","current_authority","current_approval_consent_quorum","current_human_integrity_if_required","current_dependency_vector","current_lifecycle_state","scope_subset","environment_binding","purpose_binding","target_binding","executor_binding"],"current_state_queries":["revocation","expiry","consumption","authority","approval","consent","quorum","profile","target","budget","pending_composition"],"consumption_protocol":"reserve_before_execution_and_commit_after_confirmed_effect","failure_statuses":["INVALID","REVOKED","EXPIRED","STALE","CONSUMED","UNKNOWN","INDETERMINATE"],"unknown_rule":"UNKNOWN_NEVER_GRANTS_EXECUTION","postcondition_contract":"material_effect_must_be_recorded_and_single_use_or_budget_consumption_committed","executable_scope_rule":"EXECUTABLE_SCOPE subset_of AUTHORIZED_SCOPE","p162_may_not_widen":True}
record=build_lock_record(protected_hashes=protected,evidence_hashes=evidence,p160_lock_hash=p160j.get("lock_hash",""),compiled_profile_hash=p160j.get("compiled_profile_hash",""),constitutional_snapshot_hash=p160j.get("constitutional_snapshot_hash",""),i_report=i,j_report=j,concurrency_report=c,global_validation={"passed":passed,"returncode":gv.returncode,"fast_acceptance_all_ok":"FAST_ACCEPTANCE_ALL_OK" in glog,"log_sha256":sha256_file(OUT/"global_validation.log")},contract=contract,scope={"certified":"P161 A-J functional authorization-token construction, lifecycle, defense and mutation/concurrency evidence","excluded":["P162 capability gate","capability execution","phenomenal subjectivity"]},residual_risks=[{"id":"RR-P161-1","status":"BOUNDED","statement":"Final Lock certifies only declared functional scope/evidence and creates no authority, capability, execution right or phenomenological conclusion."}],counterexamples=[])
if record["status"]!="LOCK_CANDIDATE":raise SystemExit("NOT_LOCK_CANDIDATE:"+repr(record["blockers"]))
locked=lock_candidate(record)
arts={"final_lock_manifest":locked,"final_lock_receipt":{"schema":"oce.p161.final_lock.receipt.v1","milestone":"P161-K","status":"LOCKED","lock_hash":locked["lock_hash"]},"invariant_registry":locked["invariants"],"final_lock_coverage":{"protected":sorted(protected),"evidence_count":len(evidence),"root_I":i,"mutation_J":j,"concurrency_J":c},"evidence_manifest":evidence,"residual_risk":{"risks":locked["residual_risks"],"known_limitations":locked["scope"]["excluded"]},"counterexample_registry":{"counterexamples":[],"open_root_counterexamples":0},"lock_invalidation":{"triggers":["protected_hash_drift","evidence_hash_drift","P160_lock_drift","constitutional_snapshot_drift","compiled_profile_drift","token_schema_change","authority_model_change","approval_or_lifecycle_change","crypto_change","root_counterexample","persistence_or_concurrency_regression"],"silent_revival_forbidden":True},"p161_p162_contract":contract,"final_lock_report":{"milestone":"P161-K","status":"LOCKED","P161_FINAL_LOCK_OK":True,"functional_only":True,"phenomenology_undetermined":True,"capability_created":False,"execution_performed":False,"P162_OPENED":False,"lock_hash":locked["lock_hash"]}}
for n,v in arts.items():(OUT/(n+".json")).write_text(json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("P161_FINAL_LOCK_OK");print("LOCK_HASH="+locked["lock_hash"]);print("EVIDENCE_COUNT="+str(len(evidence)));print("P162_OPENED=false")
