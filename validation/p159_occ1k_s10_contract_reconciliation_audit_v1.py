from pathlib import Path
import hashlib,json
ROOT=Path.home()/"open-cognitive-ecology"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9i/s10_contract_reconciliation_audit_v1.json"
CNP=ROOT/"validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json"
RIC=ROOT/"validation_artifacts/p159/occ1e/runtime_interface_contract_v1.json"
R7=ROOT/"validation/p159_occ1k_pre_runtime_static_contract_assessment_v1.py"
R9H=ROOT/"validation_artifacts/p159/occ1k_r9h/post_adoption_independent_replay_v1.json"
COMP=ROOT/"ontology/occ_constitutional_compiler.py"
PROFILE=ROOT/"ontology/occ_compiled_normative_profile.py"
EXPECTED=("NormResolver","CCAD","AuthorizationEngine","CapabilityGate","RecoveryEngine","AssuranceEngine")
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build():
 c=json.loads(CNP.read_text()); ric=json.loads(RIC.read_text()); h=json.loads(R9H.read_text())
 bindings=c.get("enforcement_map",{}).get("rule_bindings",{}); rules=c.get("rules",[])
 unresolved=[rid for rid,b in bindings.items() if b.get("consumer_status")=="UNRESOLVED" or not b.get("consumers")]
 classes={str(r.get("enforcement_class","UNRESOLVED")) for r in rules}
 compiler=COMP.read_text(); profile=PROFILE.read_text(); r7=R7.read_text()
 facts={"rule_count_48":len(rules)==48,"binding_slots_48":len(bindings)==48,"all_48_consumer_bindings_unresolved":len(unresolved)==48,"six_consumer_interfaces_declared":tuple(ric.get("consumers",[]))==EXPECTED,"contract_only":ric.get("contract_only") is True,"runtime_consumer_graph_unproven":ric.get("runtime_consumer_graph_proven") is False,"r7_says_actual_runtime_not_required":"actual_runtime_reachability_required_in_p159" in r7 and "False" in r7,"r7_requires_rule_to_consumer_contract_map":"materialize a P159 contract map from normative rule classes to declared runtime consumer interfaces" in r7,"profile_builder_initializes_unresolved":"consumer_status" in profile and "UNRESOLVED" in profile,"compiler_has_three_compilation_classes":all(x in compiler for x in ("CC1_DETERMINISTIC_ENFORCEMENT","CC2_RUNTIME_EVALUATION","CC3_ESCALATION_HUMAN_CCAD_REQUIRED")),"current_cnp_enforcement_classes_unresolved":classes=={"UNRESOLVED"},"r9h_s10_partial":h.get("s10",{}).get("status")=="PARTIAL"}
 status="GOVERNED_RULE_CONSUMER_SEMANTIC_BINDING_REQUIRED" if all(facts.values()) else "AUDIT_PRECONDITION_DIVERGENCE"
 r={"schema":"oce.p159.occ1k.r9i.s10.contract_reconciliation.audit.v1","milestone":"P159/OCC-1K-R9I","status":status,"facts":facts,"rule_count":len(rules),"binding_slot_count":len(bindings),"unresolved_rule_consumer_bindings":len(unresolved),"declared_consumer_interfaces":list(EXPECTED),"conclusion":{"actual_runtime_reachability_required_in_p159":False,"pre_runtime_rule_to_declared_consumer_map_required":True,"current_rule_to_consumer_map_complete":False,"safe_automatic_mapping_derivable_from_current_cnp":False,"reason":"CURRENT_CNP_HAS_48_UNRESOLVED_ENFORCEMENT_CLASSES_AND_NO_CANONICAL_CLASS_TO_CONSUMER_MAPPING","synthetic_mapping_permitted":False,"human_or_governed_semantic_resolution_required":True},"boundaries":{"runtime_binding_created":False,"runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,"fl_b3":"BLOCKED","lock_ready":False,"lock_granted":False,"p160b_opened":False},"next_required_step":"R9J_GOVERNED_RULE_CONSUMER_BINDING_DECISION_DOSSIER","functional_conclusion_only":True,"phenomenology_undetermined":True}
 r["semantic_hash"]=hashlib.sha256(canon(r)).hexdigest(); return r
def main():
 r=build(); OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_bytes(canon(r)+b"\n")
 print("P159_OCC1K_R9I_S10_CONTRACT_RECONCILIATION_AUDIT_COMPLETE")
 print("STATUS="+r["status"]); print("RULES=%d/48"%r["rule_count"]); print("BINDING_SLOTS=%d/48"%r["binding_slot_count"]); print("UNRESOLVED_RULE_CONSUMER_BINDINGS=%d"%r["unresolved_rule_consumer_bindings"])
 print("ACTUAL_RUNTIME_REACHABILITY_REQUIRED_IN_P159=false"); print("PRE_RUNTIME_RULE_TO_CONSUMER_MAP_REQUIRED=true"); print("SAFE_AUTOMATIC_MAPPING_DERIVABLE=false"); print("SYNTHETIC_MAPPING_CREATED=false"); print("FL_B3=BLOCKED"); print("P160B_OPENED=false"); print("NEXT="+r["next_required_step"]); print("ARTIFACT_SHA256="+sha(OUT))
if __name__=="__main__": main()
