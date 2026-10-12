from pathlib import Path
import hashlib,json,platform,sys
from datetime import datetime,timezone
STATUSES=("DRAFT","EVIDENCE_INCOMPLETE","LOCK_CANDIDATE","LOCKED","LOCK_INVALIDATED","SUPERSEDED")
NON_SOVEREIGN_BOUNDARIES=("AUTHORITY!=AUTHORIZATION","NORMATIVE_ELIGIBILITY!=AUTHORIZATION","APPROVAL!=AUTHORIZATION","AUTHORIZATION_TOKEN!=AUTHORITY","AUTHORIZATION_TOKEN!=CAPABILITY","AUTHORIZATION_TOKEN!=EXECUTION","FINAL_LOCK!=AUTHORIZATION","FINAL_LOCK!=EXECUTION")
ABSOLUTE_BLOCKERS=("ROOT_I_VIOLATED","ROOT_I_INCONCLUSIVE","ROOT_I_SKIPPED","ROOT_MUTANT_SURVIVED","ROOT_MUTANT_INCONCLUSIVE","META_TEST_FAILURE","CONTROL_MUTANT_FAILURE","MUTATION_CONTAMINATION","CONCURRENCY_CROWN_FAILED","POSITIVE_CONTROL_FAILURE","GLOBAL_VALIDATION_NOT_PASSED","PROTECTED_HASHES_MISSING","EVIDENCE_HASHES_MISSING","P160_NOT_LOCKED")
def _canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def _hash(x):return hashlib.sha256(_canon(x)).hexdigest()
def sha256_file(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def utc_now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def build_lock_record(*,protected_hashes,evidence_hashes,p160_lock_hash,compiled_profile_hash,constitutional_snapshot_hash,i_report,j_report,concurrency_report,global_validation,contract,scope,residual_risks,counterexamples):
 b=[]
 if not protected_hashes:b.append("PROTECTED_HASHES_MISSING")
 if not evidence_hashes:b.append("EVIDENCE_HASHES_MISSING")
 if not p160_lock_hash:b.append("P160_NOT_LOCKED")
 if i_report.get("root_violated"):b.append("ROOT_I_VIOLATED")
 if i_report.get("root_inconclusive"):b.append("ROOT_I_INCONCLUSIVE")
 if i_report.get("root_skipped"):b.append("ROOT_I_SKIPPED")
 if i_report.get("positive_pass")!=i_report.get("positive_total"):b.append("POSITIVE_CONTROL_FAILURE")
 if j_report.get("ROOT_SURVIVED"):b.append("ROOT_MUTANT_SURVIVED")
 if j_report.get("ROOT_INCONCLUSIVE"):b.append("ROOT_MUTANT_INCONCLUSIVE")
 for k in ("META_TEST_FAILURE","CONTROL_MUTANT_FAILURE","MUTATION_CONTAMINATION"):
  if j_report.get(k):b.append(k)
 if concurrency_report.get("status")!="PASS":b.append("CONCURRENCY_CROWN_FAILED")
 if not global_validation.get("passed"):b.append("GLOBAL_VALIDATION_NOT_PASSED")
 r={"schema":"oce.p161.final_lock.v1","milestone":"P161-K","status":"LOCK_CANDIDATE" if not b else "EVIDENCE_INCOMPLETE","protected_hashes":dict(sorted(protected_hashes.items())),"evidence_hashes":dict(sorted(evidence_hashes.items())),"P160_lock_hash":p160_lock_hash,"compiled_profile_hash":compiled_profile_hash,"constitutional_snapshot_hash":constitutional_snapshot_hash,"I_metrics":{k:i_report.get(k) for k in ("root_total","root_pass","root_violated","root_inconclusive","root_skipped","positive_total","positive_pass","status")},"J_metrics":{k:j_report.get(k) for k in ("ROOT_SURVIVED","ROOT_INCONCLUSIVE","META_TEST_FAILURE","CONTROL_MUTANT_FAILURE","MUTATION_CONTAMINATION","status")},"concurrency_metrics":{"total":concurrency_report.get("total"),"pass_count":concurrency_report.get("pass_count"),"status":concurrency_report.get("status")},"invariants":{"boundaries":list(NON_SOVEREIGN_BOUNDARIES),"functional_only":True,"phenomenology_undetermined":True,"capability_created":False,"execution_performed":False,"p162_opened":False},"global_validation":global_validation,"P161_to_P162_contract":contract,"scope":scope,"residual_risks":residual_risks,"counterexamples":counterexamples,"blockers":b,"toolchain":{"python":sys.version.split()[0],"platform":platform.platform()}}
 r["semantic_hash"]=_hash(r);return r
def lock_candidate(r):
 x=dict(r)
 if x.get("status")!="LOCK_CANDIDATE" or x.get("blockers"):raise ValueError("not lock eligible")
 if x["invariants"].get("capability_created") or x["invariants"].get("execution_performed") or x["invariants"].get("p162_opened"):raise ValueError("sovereignty boundary violation")
 x["status"]="LOCKED";x["locked_at"]=utc_now();x["lock_hash"]=_hash({k:v for k,v in x.items() if k!="lock_hash"});return x
def verify_lock(r,current_hashes):
 issues=[]
 if r.get("status")!="LOCKED":issues.append("NOT_LOCKED")
 for n,h in r.get("protected_hashes",{}).items():
  if current_hashes.get(n)!=h:issues.append("DRIFT:"+n)
 if r.get("lock_hash")!=_hash({k:v for k,v in r.items() if k!="lock_hash"}):issues.append("LOCK_HASH_MISMATCH")
 inv=r.get("invariants",{})
 if inv.get("capability_created") or inv.get("execution_performed") or inv.get("p162_opened"):issues.append("SOVEREIGNTY_BOUNDARY_VIOLATION")
 return {"valid":not issues,"issues":issues,"status":"VERIFIED" if not issues else "LOCK_INVALIDATED"}
def invalidate_lock(r,reason):
 x=dict(r);x["status"]="LOCK_INVALIDATED";x["invalidation_reason"]=str(reason);return x
