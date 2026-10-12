from pathlib import Path
import hashlib,json
BLOCKERS=["A021","A040","A041","A042","A046","A047","A049","A050","A051","A058","A059","A060","A061","A062","A070","A071","A075","A078","A080","A081","A082","A083","A084","A085","A095","A097","A100","A101","A105"]
GROUPS={
"G1_SOURCE_NORMATIVE_REPRESENTATION":["A021","A040","A041","A042"],
"G2_SCOPE_AUTHORITY_GRAPH":["A046","A047","A049","A050","A051"],
"G3_COMPOSITION_MULTI_ACTOR_EVIDENCE_REPUTATION":["A058","A059","A060","A061","A062"],
"G4_VERIFIER_INDEPENDENCE_AND_LIFECYCLE":["A070","A071","A075"],
"G5_LIFECYCLE_FRESHNESS_RUNTIME_BINDING":["A078","A080","A081","A082","A083","A084","A085"],
"G6_CROSS_LAYER_PROVENANCE":["A095"],
"G7_CIS_SOVEREIGNTY_TRANSITION":["A100"],
"G8_DERIVED_COMPOUND_BLOCKERS":["A097","A101","A105"]}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def build(root):
    root=Path(root); b=root/"validation_artifacts/p159/occ1h"
    paths={"inventory":root/"ontology_inventory.txt","h13":b/"h1_h3_execution_bundle_v1.json","h4":b/"h4_execution_bundle_v1.json","h5":b/"h5_mechanism_qualification_v1.json","h6":b/"h6_a058_a062_mechanism_qualification_v1.json","h7":b/"h7_a070_a071_a075_mechanism_qualification_v1.json","h8":b/"h8_boundary_mechanism_qualification_v1.json","h10":b/"h10_final_inconclusive_qualification_v1.json"}
    missing=[k for k,p in paths.items() if not p.exists()]
    if missing: raise RuntimeError("STRUCTURAL_INPUT_MISSING:"+",".join(missing))
    flattened=[a for g in GROUPS.values() for a in g]
    if sorted(flattened)!=sorted(BLOCKERS) or len(flattened)!=len(set(flattened)): raise RuntimeError("STRUCTURAL_GROUP_PARTITION_INVALID")
    h10=load(paths["h10"]); cq=h10["causal_qualifications"]
    if cq.get("A097")!="DEPENDS_ON_UNRESOLVED_A060_A062": raise RuntimeError("A097_CAUSAL_DRIFT")
    if cq.get("A101")!="DEPENDS_ON_UNRESOLVED_A075": raise RuntimeError("A101_CAUSAL_DRIFT")
    if "A095_A097_A100_A101" not in cq.get("A105",""): raise RuntimeError("A105_CAUSAL_DRIFT")
    # Exact upstream qualification coverage.
    expected={"h5":{"A046","A047","A049","A050","A051"},"h6":{"A058","A059","A060","A061","A062"},"h7":{"A070","A071","A075"},"h8":{"A078","A080","A081","A082","A083","A084","A085"}}
    for k,ids in expected.items():
        d=load(paths[k]); got=set(d.get("qualified_attack_ids") or d.get("qualifications",{}))
        if got!=ids: raise RuntimeError("QUALIFICATION_SET_DRIFT:"+k)
    interventions={
"G1_SOURCE_NORMATIVE_REPRESENTATION":"Materialize only source-backed normative strength, temporal and purpose semantics; otherwise preserve the representation boundary.",
"G2_SCOPE_AUTHORITY_GRAPH":"Extend declarative NIR/CNP scope dimensions, role identity relations and authority-cycle graph without granting authority.",
"G3_COMPOSITION_MULTI_ACTOR_EVIDENCE_REPUTATION":"Extend static relational modeling for capability/data-tool composition, Sybil identity, evidence identity and reputation topology.",
"G4_VERIFIER_INDEPENDENCE_AND_LIFECYCLE":"Add independent differential assurance for parser/shared-TCB risk and a governed verifier-lifecycle model without verifier self-authorization.",
"G5_LIFECYCLE_FRESHNESS_RUNTIME_BINDING":"Define P159-verifiable lifecycle, freshness and binding contracts without opening or implementing P160 execution.",
"G6_CROSS_LAYER_PROVENANCE":"Materialize an end-to-end provenance contract from provider-derived input through theory transformation to policy derivation.",
"G7_CIS_SOVEREIGNTY_TRANSITION":"Materialize a constitutional transition model sufficient to test CIS-to-sovereignty escalation without creating such authority.",
"G8_DERIVED_COMPOUND_BLOCKERS":"No independent patch: re-run after prerequisite structural groups are resolved."}
    e={"schema":"oce.p159.occ1h.29_blockers.structural_consolidation.v1","milestone":"P159/OCC-1H","root_inconclusive_count":29,"blockers":BLOCKERS,"groups":GROUPS,"independent_structural_gap_count":7,"derived_compound_group_count":1,"intervention_hypotheses":interventions,"dependency_edges":{"A097":["A060","A062"],"A101":["A075"],"A105":["A095","A097","A100","A101"]},"source_hashes":{k:sha(p) for k,p in paths.items()},"verdicts_modified":False,"mechanisms_created":False,"authorization_created":False,"runtime_created":False,"normative_auto_rewrite":False,"functional_only":True,"phenomenology_undetermined":True,"occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False,"scientific_conclusion":"The 29 ROOT+INCONCLUSIVE observations consolidate into seven independent structural gap classes plus one derived compound class. This is a causal engineering hypothesis, not evidence that resolving seven interventions will necessarily eliminate all 29 inconclusive verdicts."}
    e["evidence_sha256"]=hashlib.sha256(json.dumps(e,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return e
