from pathlib import Path
import hashlib,json,platform,sys
from datetime import datetime,timezone
STATUSES=("DRAFT","EVIDENCE_INCOMPLETE","LOCK_CANDIDATE","LOCKED","LOCK_INVALIDATED","SUPERSEDED")
REQUIRED_ARTIFACT_KEYS=("final_lock_manifest","final_lock_receipt","invariant_registry","final_lock_coverage","evidence_manifest","residual_risk","counterexample_registry","lock_invalidation","final_lock_report")
RTI=tuple(f"RTI-{i}" for i in range(1,19))
NON_SOVEREIGN_BOUNDARIES=("NORM_RESOLUTION!=CONFLICT_ARBITRATION","CONFLICT_ARBITRATION!=AUTHORITY_RESOLUTION","AUTHORITY_RESOLUTION!=AUTHORIZATION","AUTHORIZATION!=EXECUTION","ELIGIBLE_CANDIDATE!=AUTHORIZED","FINAL_LOCK!=AUTHORIZATION","FINAL_LOCK!=EXECUTION_PERMISSION")
def _canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def _hash_obj(x): return hashlib.sha256(_canon(x)).hexdigest()
def sha256_file(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def utc_now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def build_lock_record(*,protected_hashes,evidence_hashes,compiled_profile_hash,constitutional_snapshot_hash,global_validation,residual_risks,counterexamples,scope,dependencies):
 blockers=[]
 if not global_validation.get("passed"): blockers.append("GLOBAL_VALIDATION_NOT_PASSED")
 if not protected_hashes: blockers.append("PROTECTED_HASHES_MISSING")
 if not evidence_hashes: blockers.append("EVIDENCE_HASHES_MISSING")
 if not compiled_profile_hash: blockers.append("COMPILED_PROFILE_HASH_MISSING")
 base={"schema":"oce.p160.final_lock.v1","milestone":"P160-K","status":"LOCK_CANDIDATE" if not blockers else "EVIDENCE_INCOMPLETE","scope":scope,"protected_hashes":dict(sorted(protected_hashes.items())),"evidence_hashes":dict(sorted(evidence_hashes.items())),"compiled_profile_hash":compiled_profile_hash,"constitutional_snapshot_hash":constitutional_snapshot_hash,"invariants":{"RTI":list(RTI),"boundaries":list(NON_SOVEREIGN_BOUNDARIES),"functional_only":True,"phenomenology_undetermined":True,"authorization_created":False,"execution_performed":False,"p161_opened":False},"global_validation":global_validation,"residual_risks":residual_risks,"counterexamples":counterexamples,"dependencies":dependencies,"blockers":blockers,"toolchain":{"python":sys.version.split()[0],"platform":platform.platform()}}
 base["semantic_hash"]=_hash_obj(base); return base
def lock_candidate(record):
 r=dict(record)
 if r.get("status")!="LOCK_CANDIDATE" or r.get("blockers"): raise ValueError("not lock eligible")
 inv=r["invariants"]
 if inv.get("authorization_created") or inv.get("execution_performed") or inv.get("p161_opened"): raise ValueError("sovereignty boundary violation")
 r["status"]="LOCKED"; r["locked_at"]=utc_now(); r["lock_hash"]=_hash_obj({k:v for k,v in r.items() if k!="lock_hash"}); return r
def verify_lock(record,current_hashes):
 issues=[]
 if record.get("status")!="LOCKED": issues.append("NOT_LOCKED")
 for n,h in record.get("protected_hashes",{}).items():
  if current_hashes.get(n)!=h: issues.append("DRIFT:"+n)
 inv=record.get("invariants",{})
 if inv.get("authorization_created") or inv.get("execution_performed") or inv.get("p161_opened"): issues.append("SOVEREIGNTY_BOUNDARY_VIOLATION")
 if record.get("lock_hash")!=_hash_obj({k:v for k,v in record.items() if k!="lock_hash"}): issues.append("LOCK_HASH_MISMATCH")
 return {"valid":not issues,"issues":issues,"status":"VERIFIED" if not issues else "LOCK_INVALIDATED"}
def invalidate_lock(record,reason):
 r=dict(record); r["status"]="LOCK_INVALIDATED"; r["invalidation_reason"]=str(reason); return r
