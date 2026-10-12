from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
CNP=ROOT/"validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json"
RIC=ROOT/"validation_artifacts/p159/occ1e/runtime_interface_contract_v1.json"
R9I=ROOT/"validation_artifacts/p159/occ1k_r9i/s10_contract_reconciliation_audit_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9j/governed_rule_consumer_binding_decision_dossier_v1.json"
ALLOWED=("NormResolver","CCAD","AuthorizationEngine","CapabilityGate","RecoveryEngine","AssuranceEngine")
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def classify(rule,binding):
 evidence={
  "rule_id":rule.get("rule_id") or rule.get("id"),
  "source_norm_ids":rule.get("source_norm_ids",[]),
  "evaluation_phase":rule.get("evaluation_phase"),
  "normative_effect":rule.get("normative_effect"),
  "enforcement_class":rule.get("enforcement_class","UNRESOLVED"),
  "existing_consumers":binding.get("consumers",[]),
  "existing_consumer_status":binding.get("consumer_status","UNRESOLVED"),
 }
 # Fail closed: only an already explicit, allowed, uniquely bound consumer is determinate.
 explicit=[x for x in evidence["existing_consumers"] if x in ALLOWED]
 if evidence["existing_consumer_status"] not in ("UNRESOLVED",None) and len(explicit)==1:
  cls="DETERMINATE"; candidates=explicit; reason="EXPLICIT_EXISTING_ALLOWED_UNIQUE_CONSUMER_BINDING"
 elif len(explicit)>1:
  cls="AMBIGUOUS"; candidates=explicit; reason="MULTIPLE_EXPLICIT_ALLOWED_CONSUMERS"
 else:
  cls="UNRESOLVED"; candidates=[]; reason="NO_SOURCE_BACKED_RULE_TO_CONSUMER_BINDING_PRESENT"
 return {"classification":cls,"consumer_candidates":candidates,"reason":reason,"evidence":evidence}
def build():
 c=json.loads(CNP.read_text()); ric=json.loads(RIC.read_text()); a=json.loads(R9I.read_text())
 if a.get("status")!="GOVERNED_RULE_CONSUMER_SEMANTIC_BINDING_REQUIRED": raise RuntimeError("R9I_NOT_READY")
 declared=tuple(ric.get("consumers",[]))
 if declared!=ALLOWED: raise RuntimeError("CONSUMER_INTERFACE_SET_DIVERGENCE")
 bindings=c.get("enforcement_map",{}).get("rule_bindings",{})
 decisions=[]
 for rule in c.get("rules",[]):
  rid=rule.get("rule_id") or rule.get("id")
  if rid not in bindings: raise RuntimeError("MISSING_BINDING_SLOT:"+str(rid))
  d=classify(rule,bindings[rid]); d["rule_id"]=rid; decisions.append(d)
 counts={k:sum(d["classification"]==k for d in decisions) for k in ("DETERMINATE","AMBIGUOUS","UNRESOLVED")}
 r={"schema":"oce.p159.occ1k.r9j.governed.rule.consumer.binding.decision.dossier.v1","milestone":"P159/OCC-1K-R9J","status":"GOVERNED_DECISION_DOSSIER_READY","rule_count":len(decisions),"counts":counts,"allowed_consumer_interfaces":list(ALLOWED),"decisions":decisions,
 "decision_policy":{"source_backed_only":True,"semantic_guessing_forbidden":True,"automatic_adoption":False,"proposal_is_not_adoption":True},
 "boundaries":{"cnp_modified":False,"canonical_source_modified":False,"runtime_binding_created":False,"runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,"fl_b3":"BLOCKED","lock_ready":False,"lock_granted":False,"p160b_opened":False},
 "next_required_step":"R9K_GOVERNED_SEMANTIC_RESOLUTION_OF_UNRESOLVED_RULE_CONSUMER_BINDINGS",
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
 r["semantic_hash"]=hashlib.sha256(canon(r)).hexdigest(); return r
def main():
 r=build(); OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_bytes(canon(r)+b"\n")
 print("P159_OCC1K_R9J_GOVERNED_RULE_CONSUMER_BINDING_DECISION_DOSSIER_COMPLETE")
 print("STATUS="+r["status"]); print("RULES="+str(r["rule_count"]))
 for k in ("DETERMINATE","AMBIGUOUS","UNRESOLVED"): print(k+"="+str(r["counts"][k]))
 print("AUTOMATIC_ADOPTION=false"); print("CNP_MODIFIED=false"); print("RUNTIME_BINDING_CREATED=false"); print("AUTHORIZATION_CREATED=false"); print("EXECUTION_PERFORMED=false"); print("FL_B3=BLOCKED"); print("P160B_OPENED=false"); print("NEXT="+r["next_required_step"]); print("ARTIFACT_SHA256="+sha(OUT))
if __name__=="__main__": main()
