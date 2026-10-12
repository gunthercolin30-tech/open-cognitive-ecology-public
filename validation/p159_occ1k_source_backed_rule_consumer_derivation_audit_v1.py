from pathlib import Path
import json, hashlib
ROOT=Path.home()/"open-cognitive-ecology"
CNP=ROOT/"validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json"
CONTRACT=ROOT/"validation_artifacts/p159/occ1k_r9m/governed_consumer_semantic_contract_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9n/source_backed_rule_consumer_derivation_audit_v1.json"
ALLOWED=("NormResolver","CCAD","AuthorizationEngine","CapabilityGate","RecoveryEngine","AssuranceEngine")
def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
 cnp=load(CNP); con=load(CONTRACT)
 roles={x["consumer"]:x["semantic_role"] for x in con["responsibilities"]}
 rows=[]
 for r in cnp["rules"]:
  rid=r["rule_id"]; src=r.get("source_norm_ids",[])
  guaranteed=[]; candidates=[]; unresolved=[]
  # Contract-level applicability is common to machine-evaluated normative rules.
  if rid!="GENESIS.G0":
   guaranteed.append("NormResolver")
  # CCAD canonical rules are explicitly conflict/arbitration semantics.
  if rid.startswith("CCAD."):
   guaranteed.append("CCAD")
  # No further consumer is promoted from names/keywords alone.
  if rid.startswith("DNA."):
   candidates=["AuthorizationEngine","CapabilityGate","RecoveryEngine","AssuranceEngine"]
   unresolved.append("DOWNSTREAM_CONSUMER_REQUIRES_GOVERNED_RULE_LEVEL_SEMANTIC_BINDING")
  elif rid=="GENESIS.G0":
   candidates=["CCAD"]
   unresolved.append("F0_HUMAN_JUDGMENT_REQUIRED_NO_AUTOMATIC_CONSUMER_BINDING")
  rows.append({"rule_id":rid,"source_norm_ids":src,"evaluation_phase":r.get("evaluation_phase"),
   "enforcement_class":r.get("enforcement_class"),"guaranteed_contract_consumers":guaranteed,
   "candidate_not_adopted_consumers":candidates,"unresolved_reasons":unresolved})
 counts={"rules":len(rows),"fully_resolved":sum(not x["unresolved_reasons"] for x in rows),
         "partially_resolved":sum(bool(x["guaranteed_contract_consumers"]) and bool(x["unresolved_reasons"]) for x in rows),
         "unresolved":sum(not x["guaranteed_contract_consumers"] for x in rows)}
 return {"schema":"oce.p159.occ1k.r9n.source.backed.rule.consumer.derivation.audit.v1",
  "milestone":"P159/OCC-1K-R9N","status":"PARTIAL_DERIVATION_GOVERNED_RULE_LEVEL_BINDING_REQUIRED",
  "inputs":{"cnp_sha256":sha(CNP),"governed_contract_sha256":sha(CONTRACT)},
  "allowed_consumers":list(ALLOWED),"responsibility_roles":roles,"counts":counts,"rules":rows,
  "derivation_policy":{"keyword_only_binding_forbidden":True,"compilation_class_alone_insufficient":True,
   "contract_role_may_establish_common_applicability_consumer":True,
   "ccad_canonical_identity_may_establish_ccad_consumer":True,
   "candidate_is_not_binding":True,"unknown_preserved":True},
  "boundaries":{"cnp_modified":False,"rule_bindings_modified":False,"runtime_binding_created":False,
   "runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,
   "fl_b3":"BLOCKED","lock_ready":False,"lock_granted":False,"p160b_opened":False},
  "next_required_step":"R9O_GOVERNED_RULE_LEVEL_CONSUMER_BINDING_DOSSIER",
  "functional_conclusion_only":True,"phenomenology_undetermined":True}
def write():
 d=build(); OUT.parent.mkdir(parents=True,exist_ok=True)
 b=(json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()
 OUT.write_bytes(b); return d,hashlib.sha256(b).hexdigest()
def main():
 d,h=write(); c=d["counts"]
 print("P159_OCC1K_R9N_SOURCE_BACKED_RULE_CONSUMER_DERIVATION_AUDIT_COMPLETE")
 print("STATUS="+d["status"]); print("RULES=%d/48"%c["rules"])
 print("FULLY_RESOLVED=%d"%c["fully_resolved"]); print("PARTIALLY_RESOLVED=%d"%c["partially_resolved"]); print("UNRESOLVED=%d"%c["unresolved"])
 print("KEYWORD_ONLY_BINDING=false"); print("RULE_BINDINGS_MODIFIED=false"); print("RUNTIME_BINDING_CREATED=false")
 print("FL_B3=BLOCKED"); print("P160B_OPENED=false"); print("NEXT="+d["next_required_step"]); print("ARTIFACT_SHA256="+h)
if __name__=="__main__": main()
