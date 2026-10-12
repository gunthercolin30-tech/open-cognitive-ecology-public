from pathlib import Path
import hashlib, json
SCHEMA="oce.p159.occ1h.h8.boundary_mechanism_qualification.v1"
DECISION="CURRENT_P159_H8_BOUNDARY_MECHANISMS_NOT_PROVEN"
EXPECTED={
"A078":"STALE_REPORT_CAN_EXIST_BUT_NO_P159_REPORT_CONSUMER_FRESHNESS_GATE_IS_PROVEN",
"A080":"REVOCATION_ACTIVATION_PATH_NOT_PROVEN_AT_P159",
"A081":"RUNTIME_REGISTRY_CONSUMER_BINDING_NOT_PROVEN_AT_P159",
"A082":"RUNTIME_CACHE_CONSUMER_BINDING_NOT_PROVEN_AT_P159",
"A083":"TOKEN_TO_CNP_RUNTIME_BINDING_NOT_PROVEN_AT_P159",
"A084":"CLOCK_DEPENDENT_CONSTITUTIONAL_ENFORCEMENT_NOT_PROVEN_AT_P159",
"A085":"EMERGENCY_REPLAY_ENFORCEMENT_PATH_NOT_PROVEN_AT_P159"}
QUALIFICATIONS={
"A078":"P159_FRESHNESS_CONSUMER_GATE_NOT_PROVEN",
"A080":"REVOCATION_ACTIVATION_REQUIRES_UNMATERIALIZED_LIFECYCLE_PATH",
"A081":"RUNTIME_REGISTRY_TO_CNP_BINDING_NOT_PROVEN",
"A082":"RUNTIME_CACHE_TO_CNP_BINDING_NOT_PROVEN",
"A083":"RUNTIME_TOKEN_TO_CNP_BINDING_NOT_PROVEN",
"A084":"CLOCK_DEPENDENT_CONSTITUTIONAL_ENFORCEMENT_NOT_PROVEN",
"A085":"EMERGENCY_REPLAY_ENFORCEMENT_NOT_PROVEN"}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def locate(root,names):
    for rel in names:
        p=root/rel
        if p.exists(): return p

def build(root):
    root=Path(root)
    paths={"ontology_inventory":root/"ontology_inventory.txt",
           "h8_runner":root/"ontology/occ_constitutional_adversarial_crown_h8.py",
           "h8_bundle":root/"validation_artifacts/p159/occ1h/h8_execution_bundle_v1.json"}
    miss=[k for k,p in paths.items() if not p.exists()]
    if miss: raise RuntimeError("H8_QUALIFICATION_INPUT_MISSING:"+",".join(miss))
    h8=json.loads(paths["h8_bundle"].read_text(encoding="utf-8"))
    rows={r["attack_id"]:r for r in h8["rows"]}
    for aid,reason in EXPECTED.items():
        r=rows.get(aid)
        if not r or r.get("verdict")!="INCONCLUSIVE" or r.get("reason")!=reason:
            raise RuntimeError("H8_CURRENT_EVIDENCE_DRIFT:"+aid)
    optional={
      "runtime_constitutional_integration":["ontology/runtime_constitutional_integration.py"],
      "revocation_conditions_engine":["ontology/revocation_conditions_engine.py"],
      "distributed_constitutional_propagation":["ontology/distributed_constitutional_propagation.py"]}
    neighbors={}
    for k,names in optional.items():
        p=locate(root,names)
        if p: neighbors[k]=p
    hashes={k:sha(p) for k,p in paths.items()}
    hashes.update({"neighbor:"+k:sha(p) for k,p in neighbors.items()})
    e={"schema":SCHEMA,"milestone":"P159/OCC-1H/H8","decision":DECISION,
       "qualified_attack_ids":list(EXPECTED),"qualified_count":7,
       "qualifications":QUALIFICATIONS,"source_hashes":hashes,
       "neighboring_mechanisms_found":sorted(neighbors),
       "neighboring_mechanisms_are_h8_proof":False,
       "verdicts_modified":False,"canonical_sources_modified":False,
       "compiled_profile_modified":False,"h8_modified":False,
       "runtime_created":False,"authorization_created":False,
       "execution_performed":False,"normative_auto_rewrite":False,
       "functional_only":True,"phenomenology_undetermined":True,
       "occ1h_closed":False,"occ1i_opened":False,
       "p159_final_lock":False,"p160_opened":False,
       "limitations":["Qualification explains P159 evidentiary limits; INCONCLUSIVE is not promoted.",
       "Neighboring OCE primitives are not H8 proof without a demonstrated P159 binding.",
       "No P160 runtime or authorization mechanism is created or inferred."]}
    basis=dict(e)
    e["evidence_sha256"]=hashlib.sha256(json.dumps(basis,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return e
