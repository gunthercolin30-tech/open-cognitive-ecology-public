from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
L=ROOT/"validation_artifacts/p159/occ1k_r9ap/final_lock_manifest_locked_v1.json"
Q=ROOT/"validation_artifacts/p159/occ1k_r9aq/independent_post_lock_verification_v1.json"
B=ROOT/"validation_artifacts/p159/occ1k_r9ag/final_lock_evidence_bundle_v1.json"
OLD1=ROOT/"validation_artifacts/p159/occ1k_r9as/exhaustive_closure_certification_v1.json"
OLD2=ROOT/"validation_artifacts/p159/occ1k_r9as2/exhaustive_closure_certification_schema_aware_v2.json"
REPORT=ROOT/"ontology_integration_report.txt"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9as3/exhaustive_closure_certification_json_aware_v3.json"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def parse_report(text):
 try: return json.loads(text.split("\n",1)[1])
 except Exception: return None
def report_ok(text):
 d=parse_report(text)
 if not isinstance(d,dict): return False
 suites=d.get("suites")
 return (d.get("validation_mode")=="fast_acceptance" and d.get("success") is True
         and d.get("returncode")==0 and isinstance(suites,list) and len(suites)>0
         and all(s.get("status")=="passed" and s.get("returncode")==0 for s in suites)
         and any(s.get("marker")=="FAST_ACCEPTANCE_ALL_OK" for s in suites)
         and "FAST_ACCEPTANCE_ALL_OK" in str(d.get("output","")))
def certify(overrides=None):
 o=overrides or {};l=o.get("locked",load(L));q=o.get("post",load(Q));b=o.get("bundle",load(B))
 txt=o.get("report",REPORT.read_text(encoding="utf-8",errors="replace"))
 checks={
 "locked":l.get("status")=="LOCKED","lock_scope_exact":l.get("lock_scope_claim")=="P159/OCC-1 ONLY",
 "post_lock_verified":q.get("status")=="VERIFIED" and q.get("passed")==q.get("total")==16,
 "post_lock_bound_to_locked":q.get("locked_manifest_sha256")==sha(L),
 "bundle_complete":b.get("status")=="BUNDLE_MATERIALIZED_COMPLETE","global_validation_pass":report_ok(txt),
 "functional_only":q.get("functional_conclusion_only") is True and q.get("phenomenology_undetermined") is True
   and b.get("functional_conclusion_only") is True and b.get("phenomenology_undetermined") is True,
 "runtime_inactive":l.get("runtime_active") is False,
 "no_authorization_execution":l.get("authorization_created") is False and l.get("execution_performed") is False,
 "p160b_not_opened":l.get("p160b_opened") is False}
 ok=all(checks.values())
 return {"schema":"oce.p159.occ1k.exhaustive_closure_certification.json_aware.v3","milestone":"P159/OCC-1K",
 "status":"P159_EXHAUSTIVE_CLOSURE_CERTIFIED" if ok else "P159_EXHAUSTIVE_CLOSURE_NOT_CERTIFIED",
 "checks":checks,"passed":sum(checks.values()),"total":len(checks),"locked_manifest_sha256":sha(L),
 "post_lock_verification_sha256":sha(Q),"evidence_bundle_sha256":sha(B),"global_validation_report_sha256":sha(REPORT),
 "historical_r9as_sha256":sha(OLD1),"historical_r9as2_sha256":sha(OLD2),
 "historical_failed_certifications_preserved":OLD1.is_file() and OLD2.is_file(),
 "historical_failed_certifications_rewritten":False,"claim_scope":"FUNCTIONAL P159/OCC-1 ONLY",
 "runtime_active":False,"p160b_opened":False,"p160b_authorized_to_resume":ok,"production_modified":False}
def write():
 x=certify();OUT.parent.mkdir(parents=True,exist_ok=True);t=OUT.with_suffix(".json.tmp")
 t.write_text(canon(x)+"\n",encoding="utf-8");t.replace(OUT);return x,sha(OUT)
def main():
 x,h=write();print("P159_OCC1K_R9AS3_JSON_AWARE_EXHAUSTIVE_CLOSURE_CERTIFICATION_COMPLETE")
 print("STATUS="+x["status"]);print(f'CHECKS={x["passed"]}/{x["total"]}')
 print("HISTORICAL_FAILED_CERTIFICATIONS_PRESERVED="+str(x["historical_failed_certifications_preserved"]).lower())
 print("CLAIM_SCOPE="+x["claim_scope"]);print("P160B_OPENED=false")
 print("P160B_AUTHORIZED_TO_RESUME="+str(x["p160b_authorized_to_resume"]).lower());print("ARTIFACT_SHA256="+h)
if __name__=="__main__":main()
