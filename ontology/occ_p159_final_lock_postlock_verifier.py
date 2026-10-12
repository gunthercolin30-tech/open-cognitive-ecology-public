from ontology import occ_p159_final_lock as fl
SCHEMA="oce.p159.occ1k.postlock_verification.v1"
def verify(root=None):
 r=fl.root(root);lp=r/fl.LOCK_REL;ep=r/fl.ELIG_REL;checks={"lock_exists":lp.is_file(),"eligibility_exists":ep.is_file()}
 if not all(checks.values()):return {"schema":SCHEMA,"status":"FAIL","checks":checks,"p160_opened":False}
 lock=fl.load(lp);elig=fl.load(ep)
 checks["lock_schema_status"]=lock.get("schema")==fl.SCHEMA_LOCK and lock.get("status")=="LOCKED"
 checks["eligibility_schema_status"]=elig.get("schema")==fl.SCHEMA_ELIG and elig.get("status")=="ELIGIBLE"
 checks["eligibility_identity"]=lock.get("eligibility_identity_sha256")==elig.get("eligibility_identity_sha256")
 checks["evidence_bindings"]=all((r/fl.EVIDENCE[k]).is_file() and fl.sha(r/fl.EVIDENCE[k])==v for k,v in lock.get("eligibility_evidence_hashes",{}).items())
 checks["module_bindings"]=all((r/k).is_file() and fl.sha(r/k)==v for k,v in lock.get("protected_module_hashes",{}).items())
 checks["lock_identity"]=fl.build_lock(elig,lock.get("global_validation_receipt_sha256")).get("final_lock_identity_sha256")==lock.get("final_lock_identity_sha256")
 checks["boundaries"]=lock.get("authorization_created") is False and lock.get("execution_performed") is False and lock.get("p160_opened") is False
 checks["epistemics"]=lock.get("functional_conclusion_only") is True and lock.get("phenomenology_undetermined") is True
 ok=all(v is True for v in checks.values())
 return {"schema":SCHEMA,"milestone":"P159/OCC-1K","status":"POST_LOCK_VERIFIED" if ok else "FAIL","checks":checks,"p159_final_lock":ok,"p160_opened":False,"authorization_created":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True,"verified_lock_sha256":fl.sha(lp) if lp.is_file() else None,"verified_lock_identity_sha256":lock.get("final_lock_identity_sha256") if ok else None}
