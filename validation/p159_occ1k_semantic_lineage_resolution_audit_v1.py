from pathlib import Path
import json, hashlib
ROOT=Path.home()/"open-cognitive-ecology"
LEGACY=ROOT/"validation_artifacts/p159/occ1c/compiled_normative_profile_v1.json"
CNP=ROOT/"validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9k/semantic_lineage_resolution_audit_v1.json"
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def classify(r):
    if bool(r.get("human_judgment_required")): return "CC3_ESCALATION_HUMAN_CCAD_REQUIRED"
    if r.get("formalization_level") in ("F0","F1") or r.get("semantic_status") in ("UNKNOWN","CONTESTED","UNSUPPORTED") or bool(r.get("partial_formalization_explicit")): return "CC2_RUNTIME_EVALUATION"
    return "CC1_DETERMINISTIC_ENFORCEMENT"
def build():
    old=json.loads(LEGACY.read_text()); cnp=json.loads(CNP.read_text())
    if len(old.get("rules",[]))!=48 or len(cnp.get("rules",[]))!=48: raise RuntimeError("RULE_COUNT_DIVERGENCE")
    byid={r.get("norm_id"):r for r in old["rules"]}
    counts={k:0 for k in ("CC1_DETERMINISTIC_ENFORCEMENT","CC2_RUNTIME_EVALUATION","CC3_ESCALATION_HUMAN_CCAD_REQUIRED")}
    rows=[]
    for cr in cnp["rules"]:
        rid=cr["rule_id"]; lr=byid.get(rid)
        if lr is None: raise RuntimeError("LEGACY_LINEAGE_MISSING:"+rid)
        cc=classify(lr); counts[cc]+=1
        rows.append({"rule_id":rid,"source_norm_ids":cr.get("source_norm_ids",[]),"nir_node_ids":cr.get("nir_node_ids",[]),"formalization_level":lr.get("formalization_level"),"semantic_status":lr.get("semantic_status"),"human_judgment_required":bool(lr.get("human_judgment_required")),"reconstructed_compilation_class":cc,"consumer_binding_status":cnp["enforcement_map"]["rule_bindings"][rid].get("consumer_status"),"consumer_mapping_derivable_from_compilation_class":False,"reason":"COMPILATION_CLASS_DETERMINES_EVALUATION_MODE_NOT_UNIQUE_RUNTIME_CONSUMER"})
    r={"schema":"oce.p159.occ1k.r9k.semantic.lineage.resolution.audit.v1","milestone":"P159/OCC-1K-R9K","status":"LINEAGE_RECONSTRUCTED_CONSUMER_SEMANTICS_STILL_UNRESOLVED","rule_count":len(rows),"lineage_complete":len(rows)==48,"compilation_class_counts":counts,"rules":rows,"findings":{"source_to_rule_lineage_reconstructible":True,"compilation_classes_reconstructible":True,"norm_ops_policy_reconstructible_from_compiler":True,"unique_rule_to_consumer_mapping_derivable":False,"reason":"NO_CANONICAL_CLASS_TO_CONSUMER_OR_RULE_TO_CONSUMER_SEMANTIC_BINDING_FOUND","synthetic_mapping_forbidden":True},"boundaries":{"cnp_modified":False,"canonical_source_modified":False,"runtime_binding_created":False,"runtime_enforcement_proven":False,"authorization_created":False,"execution_performed":False,"fl_b3":"BLOCKED","lock_ready":False,"lock_granted":False,"p160b_opened":False},"next_required_step":"R9L_GOVERNED_RULE_CONSUMER_SEMANTIC_CONTRACT_SPECIFICATION","functional_conclusion_only":True,"phenomenology_undetermined":True}
    r["semantic_hash"]=hashlib.sha256(canon(r)).hexdigest(); return r
def main():
    r=build(); OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_bytes(canon(r)+b"\n")
    print("P159_OCC1K_R9K_SEMANTIC_LINEAGE_RESOLUTION_AUDIT_COMPLETE"); print("STATUS="+r["status"]); print("RULES=48/48"); print("LINEAGE_COMPLETE=true")
    for k,v in r["compilation_class_counts"].items(): print(k+"="+str(v))
    print("UNIQUE_RULE_TO_CONSUMER_MAPPING_DERIVABLE=false"); print("SYNTHETIC_MAPPING_CREATED=false"); print("FL_B3=BLOCKED"); print("P160B_OPENED=false"); print("NEXT="+r["next_required_step"]); print("ARTIFACT_SHA256="+hashlib.sha256(OUT.read_bytes()).hexdigest())
if __name__=="__main__": main()
