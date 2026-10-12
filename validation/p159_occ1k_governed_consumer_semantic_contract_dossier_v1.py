from pathlib import Path
import json,hashlib
ROOT=Path.home()/"open-cognitive-ecology"
R9K=ROOT/"validation_artifacts/p159/occ1k_r9k/semantic_lineage_resolution_audit_v1.json"
RIC=ROOT/"validation_artifacts/p159/occ1e/runtime_interface_contract_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9l/governed_consumer_semantic_contract_dossier_v1.json"
CONSUMERS=("NormResolver","CCAD","AuthorizationEngine","CapabilityGate","RecoveryEngine","AssuranceEngine")
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def build():
 k=json.loads(R9K.read_text()); ric=json.loads(RIC.read_text())
 if k.get("status")!="LINEAGE_RECONSTRUCTED_CONSUMER_SEMANTICS_STILL_UNRESOLVED": raise RuntimeError("R9K_NOT_READY")
 if tuple(ric.get("consumers",[]))!=CONSUMERS: raise RuntimeError("CONSUMER_SET_DIVERGENCE")
 responsibilities=[
 {"consumer":"NormResolver","status":"PROPOSED_NOT_ADOPTED","semantic_role":"resolve and evaluate normative applicability before downstream authority decisions","may_authorize":False,"may_execute":False},
 {"consumer":"CCAD","status":"PROPOSED_NOT_ADOPTED","semantic_role":"handle constitutional conflict, arbitration, and explicitly escalated judgment paths","may_authorize":False,"may_execute":False},
 {"consumer":"AuthorizationEngine","status":"PROPOSED_NOT_ADOPTED","semantic_role":"consume applicable normative results when evaluating authorization; compilation itself grants no authorization","may_authorize":True,"may_execute":False},
 {"consumer":"CapabilityGate","status":"PROPOSED_NOT_ADOPTED","semantic_role":"consume normative constraints when determining capability eligibility; no execution by the contract","may_authorize":False,"may_execute":False},
 {"consumer":"RecoveryEngine","status":"PROPOSED_NOT_ADOPTED","semantic_role":"consume recovery, revocation, expiry, and fail-closed obligations where applicable","may_authorize":False,"may_execute":False},
 {"consumer":"AssuranceEngine","status":"PROPOSED_NOT_ADOPTED","semantic_role":"consume evidence, provenance, assurance, and verification obligations without self-certification","may_authorize":False,"may_execute":False}]
 r={"schema":"oce.p159.occ1k.r9l.governed.consumer.semantic.contract.dossier.v1","milestone":"P159/OCC-1K-R9L","status":"HUMAN_GOVERNED_CONSUMER_SEMANTIC_CONTRACT_DECISION_REQUIRED","consumer_count":6,"responsibilities":responsibilities,
 "derivation_policy":{"contract_defines_responsibility_domains_not_runtime_reachability":True,"rule_binding_requires_explicit_semantic_match_after_contract_adoption":True,"compilation_class_alone_insufficient":True,"multi_consumer_binding_permitted_only_if_semantically_justified":True,"unknown_remains_unresolved":True},
 "decision":{"default":"KEEP_UNRESOLVED","allowed":["ADOPT_CONTRACT","KEEP_UNRESOLVED"],"automatic_adoption":False},
 "boundaries":{"rule_bindings_modified":False,"cnp_modified":False,"canonical_source_modified":False,"runtime_binding_created":False,"runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,"fl_b3":"BLOCKED","lock_ready":False,"lock_granted":False,"p160b_opened":False},
 "next_if_adopted":"R9M_ATOMIC_GOVERNED_CONSUMER_SEMANTIC_CONTRACT_COMMIT","functional_conclusion_only":True,"phenomenology_undetermined":True}
 r["semantic_hash"]=hashlib.sha256(canon(r)).hexdigest(); return r
def main():
 r=build(); OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_bytes(canon(r)+b"\n")
 print("P159_OCC1K_R9L_GOVERNED_CONSUMER_SEMANTIC_CONTRACT_DOSSIER_COMPLETE")
 print("STATUS="+r["status"]); print("CONSUMERS=6/6"); print("AUTOMATIC_ADOPTION=false"); print("RULE_BINDINGS_MODIFIED=false"); print("RUNTIME_BINDING_CREATED=false"); print("FL_B3=BLOCKED"); print("P160B_OPENED=false"); print("DEFAULT_DECISION=KEEP_UNRESOLVED"); print("ARTIFACT_SHA256="+hashlib.sha256(OUT.read_bytes()).hexdigest())
if __name__=="__main__": main()
