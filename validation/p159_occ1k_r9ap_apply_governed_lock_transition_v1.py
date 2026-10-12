from pathlib import Path
import json,hashlib,datetime
ROOT=Path.home()/"open-cognitive-ecology"
M=ROOT/"validation_artifacts/p159/occ1k_r9an/final_lock_manifest_lock_ready_candidate_v1.json"
R=ROOT/"validation_artifacts/p159/occ1k_r9ao2/final_lock_transition_receipt_schema_aware_v2.json"
B=ROOT/"validation_artifacts/p159/occ1k_r9ag/final_lock_evidence_bundle_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9ap/final_lock_manifest_locked_v1.json"
APPLY=ROOT/"validation_artifacts/p159/occ1k_r9ap/final_lock_application_record_v1.json"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def validate(m,r):
 return (
 m.get("status")=="LOCK_READY" and r.get("decision")=="APPROVE_LOCK_TRANSITION"
 and r.get("eligible_for_transition") is True and r.get("canonical_fields_complete") is True
 and r.get("manifest_hash")==m.get("manifest_hash")
 and r.get("manifest_artifact_sha256")==sha(M)
 and r.get("evidence_bundle_hash")==sha(B)
 and r.get("receipt_is_lock") is False and r.get("lock_applied") is False
 and r.get("runtime_active") is False and r.get("p160b_opened") is False)
def build_locked(timestamp=None,m=None,r=None):
 m=m or load(M);r=r or load(R)
 if not validate(m,r): return None
 ts=timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00","Z")
 x=dict(m)
 x["previous_status"]="LOCK_READY";x["status"]="LOCKED";x["locked_at"]=ts
 x["governed_transition_receipt_sha256"]=sha(R)
 x["governed_transition_receipt_hash"]=r.get("receipt_hash")
 x["lock_ready_manifest_hash"]=m.get("manifest_hash")
 x["runtime_active"]=False;x["authority_created"]=False;x["authorization_created"]=False
 x["execution_performed"]=False;x["p160b_opened"]=False
 x["post_lock_verified"]=False;x["global_post_lock_validation"]=False
 x["lock_scope_claim"]="P159/OCC-1 ONLY"
 x.pop("manifest_hash",None)
 x["manifest_hash"]=hashlib.sha256(canon(x).encode()).hexdigest()
 return x
def write():
 m=load(M);r=load(R);x=build_locked(m=m,r=r)
 if x is None: raise SystemExit("R9AP_FAIL_CLOSED_TRANSITION_NOT_APPLIED")
 OUT.parent.mkdir(parents=True,exist_ok=True)
 tmp=OUT.with_suffix(".json.tmp");tmp.write_text(canon(x)+"\n",encoding="utf-8");tmp.replace(OUT)
 rec={"schema":"oce.p159.occ1k.final_lock_application_record.v1","milestone":"P159/OCC-1K",
 "decision":"LOCK_TRANSITION_APPLIED","from_status":"LOCK_READY","to_status":"LOCKED",
 "source_manifest_sha256":sha(M),"transition_receipt_sha256":sha(R),"locked_manifest_sha256":sha(OUT),
 "locked_manifest_hash":x["manifest_hash"],"runtime_active":False,"p160b_opened":False,
 "post_lock_verified":False,"global_post_lock_validation":False}
 tmp2=APPLY.with_suffix(".json.tmp");tmp2.write_text(canon(rec)+"\n",encoding="utf-8");tmp2.replace(APPLY)
 return x,rec
def main():
 x,r=write()
 print("P159_OCC1K_R9AP_GOVERNED_LOCK_TRANSITION_APPLIED")
 print("STATUS="+x["status"]);print("LOCK_SCOPE="+x["lock_scope_claim"])
 print("POST_LOCK_VERIFIED=false");print("GLOBAL_POST_LOCK_VALIDATION=false")
 print("RUNTIME_ACTIVE=false");print("P160B_OPENED=false")
 print("LOCKED_MANIFEST_SHA256="+sha(OUT));print("APPLICATION_RECORD_SHA256="+sha(APPLY))
 print("NEXT=R9AQ_INDEPENDENT_POST_LOCK_VERIFICATION")
if __name__=="__main__":main()
