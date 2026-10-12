from pathlib import Path
import json, hashlib, datetime
ROOT=Path.home()/"open-cognitive-ecology"
V=ROOT/"validation_artifacts/p159/occ1k_r9am2/independent_occ_final_lock_verify_schema_aware_v2.json"
B=ROOT/"validation_artifacts/p159/occ1k_r9ag/final_lock_evidence_bundle_v1.json"
AJ=ROOT/"validation_artifacts/p159/occ1k_r9aj/final_lock_meta_crown_fl_a01_a20_v1.json"
AK=ROOT/"validation_artifacts/p159/occ1k_r9ak/mut_fl_meta_mutation_campaign_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9an/final_lock_manifest_lock_ready_candidate_v1.json"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def build(created_at=None):
 v,b,aj,ak=load(V),load(B),load(AJ),load(AK)
 ok=(v.get("status")=="VERIFIED" and v.get("lock_ready") is True and
     b.get("status")=="BUNDLE_MATERIALIZED_COMPLETE" and
     aj.get("status")=="META_CROWN_FL_A01_A20_PASS" and
     ak.get("status")=="MUT_FL_PASS")
 status="LOCK_READY" if ok else "VALIDATION_PENDING"
 body={
 "schema":"oce.p159.occ1k.final_lock_manifest.v1",
 "lock_id":"P159-OCC1K-EXHAUSTIVE-2026-09",
 "milestone":"P159/OCC-1K",
 "lock_version":"occ1k-exhaustive-v1",
 "created_at":created_at or datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00","Z"),
 "scope":"OCC-1 COMPILER_AND_ASSURANCE_BASELINE_ONLY",
 "source_tool_evidence_hashes":{"r9am2_verifier":sha(V),"r9ag_bundle":sha(B),"r9aj_meta_crown":sha(AJ),"r9ak_mut_fl":sha(AK)},
 "critical_invariants":{"functional_conclusion_only":True,"phenomenology_undetermined":True,
   "compilation_is_not_authorization":True,"locked_is_not_runtime_active":True},
 "blocking_criteria":{"fl_b1_b12":"PASS","fl_a01_a20":"PASS","mut_fl":"PASS","independent_final_lock_verifier":"VERIFIED"},
 "limitations":["LOCK_READY is not LOCKED","OCC-1 LOCKED does not imply runtime ACTIVE","No phenomenal conclusion"],
 "residual_risks":["Future root counterexamples or invalidation triggers may degrade/invalidate current assurance"],
 "status":status,
 "transition_receipt_present":False,"runtime_active":False,"authority_created":False,
 "authorization_created":False,"execution_performed":False,"p160b_opened":False}
 payload=canon(body).encode(); body["manifest_hash"]=hashlib.sha256(payload).hexdigest()
 return body
def write():
 x=build();OUT.parent.mkdir(parents=True,exist_ok=True);tmp=OUT.with_suffix(".json.tmp")
 tmp.write_text(canon(x)+"\n",encoding="utf-8");tmp.replace(OUT);return x,sha(OUT)
def main():
 x,h=write();print("P159_OCC1K_R9AN_LOCK_READY_MANIFEST_CANDIDATE_COMPLETE")
 print("STATUS="+x["status"]);print("MANIFEST_HASH="+x["manifest_hash"])
 print("TRANSITION_RECEIPT_PRESENT=false");print("RUNTIME_ACTIVE=false");print("LOCK_GRANTED=false")
 print("P160B_OPENED=false");print("NEXT=R9AO_GOVERNED_FINAL_LOCK_TRANSITION_RECEIPT")
 print("ARTIFACT_SHA256="+h)
if __name__=="__main__": main()
