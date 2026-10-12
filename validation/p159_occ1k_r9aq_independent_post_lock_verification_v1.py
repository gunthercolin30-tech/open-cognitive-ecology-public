from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
L=ROOT/"validation_artifacts/p159/occ1k_r9ap/final_lock_manifest_locked_v1.json"
A=ROOT/"validation_artifacts/p159/occ1k_r9ap/final_lock_application_record_v1.json"
R=ROOT/"validation_artifacts/p159/occ1k_r9ao2/final_lock_transition_receipt_schema_aware_v2.json"
M=ROOT/"validation_artifacts/p159/occ1k_r9an/final_lock_manifest_lock_ready_candidate_v1.json"
B=ROOT/"validation_artifacts/p159/occ1k_r9ag/final_lock_evidence_bundle_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9aq/independent_post_lock_verification_v1.json"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def self_hash_ok(x):
 y=dict(x);h=y.pop("manifest_hash",None)
 return bool(h) and h==hashlib.sha256(canon(y).encode()).hexdigest()
def verify(overrides=None):
 overrides=overrides or {}
 l=overrides.get("locked",load(L));a=overrides.get("application",load(A))
 r=overrides.get("receipt",load(R));m=overrides.get("ready",load(M))
 checks={
 "locked_status":l.get("status")=="LOCKED",
 "locked_manifest_self_hash":self_hash_ok(l),
 "scope_exact":l.get("lock_scope_claim")=="P159/OCC-1 ONLY",
 "receipt_artifact_bound":l.get("governed_transition_receipt_sha256")==sha(R),
 "receipt_semantic_bound":l.get("governed_transition_receipt_hash")==r.get("receipt_hash"),
 "ready_manifest_bound":l.get("lock_ready_manifest_hash")==m.get("manifest_hash"),
 "application_source_manifest_bound":a.get("source_manifest_sha256")==sha(M),
 "application_receipt_bound":a.get("transition_receipt_sha256")==sha(R),
 "application_locked_artifact_bound":a.get("locked_manifest_sha256")==sha(L),
 "application_locked_semantic_bound":a.get("locked_manifest_hash")==l.get("manifest_hash"),
 "bundle_still_bound":r.get("evidence_bundle_hash")==sha(B),
 "receipt_approved":r.get("decision")=="APPROVE_LOCK_TRANSITION" and r.get("eligible_for_transition") is True,
 "no_runtime_activation":l.get("runtime_active") is False,
 "no_authorization_or_execution":l.get("authorization_created") is False and l.get("execution_performed") is False,
 "p160b_closed":l.get("p160b_opened") is False,
 "post_lock_not_preclaimed":l.get("post_lock_verified") is False and l.get("global_post_lock_validation") is False}
 ok=all(checks.values())
 return {"schema":"oce.p159.occ1k.independent_post_lock_verification.v1","milestone":"P159/OCC-1K",
 "status":"VERIFIED" if ok else "REJECTED","checks":checks,"passed":sum(checks.values()),"total":len(checks),
 "locked_manifest_sha256":sha(L),"application_record_sha256":sha(A),"receipt_sha256":sha(R),
 "repairs_performed":False,"locked_artifact_modified":False,"runtime_active":False,
 "p160b_opened":False,"global_post_lock_validation":False,
 "next_required_step":"R9AR_GLOBAL_POST_LOCK_VALIDATION" if ok else "R9AQ_REMEDIATION",
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 x=verify();OUT.parent.mkdir(parents=True,exist_ok=True);tmp=OUT.with_suffix(".json.tmp")
 tmp.write_text(canon(x)+"\n",encoding="utf-8");tmp.replace(OUT);return x,sha(OUT)
def main():
 x,h=write();print("P159_OCC1K_R9AQ_INDEPENDENT_POST_LOCK_VERIFICATION_COMPLETE")
 print("STATUS="+x["status"]);print(f'CHECKS={x["passed"]}/{x["total"]}')
 print("REPAIRS_PERFORMED=false");print("LOCKED_ARTIFACT_MODIFIED=false")
 print("GLOBAL_POST_LOCK_VALIDATION=false");print("P160B_OPENED=false")
 print("NEXT="+x["next_required_step"]);print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
