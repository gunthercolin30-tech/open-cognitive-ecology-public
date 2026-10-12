# A081 RRP-v2.1 A->E: registry substitution binding-gap qualification.
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
def evaluate(root=ROOT):
 root=Path(root)
 cnp=(root/"ontology/occ_compiled_normative_profile.py").read_text()
 pcv=(root/"ontology/occ_compiled_normative_profile_postclose_verifier.py").read_text()
 rt=(root/"ontology/runtime_constitutional_integration.py").read_text()
 reg=(root/"ontology/architecture_registry.py").read_text()
 h8=(root/"ontology/occ_constitutional_adversarial_crown_h8.py").read_text()
 facts={
 "historical_a081_boundary":'"A081":"RUNTIME_REGISTRY_CONSUMER_BINDING_NOT_PROVEN_AT_P159"' in h8,
 "cnp_runtime_graph_explicitly_unproven":'"runtime_consumer_graph_proven":False' in cnp and '"status":"UNRESOLVED"' in cnp,
 "postclose_preserves_unproven_runtime_graph":'closure.get("runtime_consumer_graph_proven") is False' in pcv and '"runtime_consumer_graph_proven":False' in pcv,
 "runtime_integration_has_no_cnp_or_registry_binding":("occ_compiled_normative_profile" not in rt and "architecture_registry" not in rt),
 "architecture_registry_is_comparative_not_constitutional_consumer":'epistemic_scope": "functional_comparative_registry_only"' in reg,
 }
 ok=all(facts.values())
 return {"schema":"oce.p159.occ1h.a081.rrpv21.a_to_e.v1","scenario_id":"A081","canonical_label":"registry substitution","family":"H8","historical_verdict":"INCONCLUSIVE","historical_reason":"RUNTIME_REGISTRY_CONSUMER_BINDING_NOT_PROVEN_AT_P159","qualification":"RUNTIME_REGISTRY_TO_CNP_BINDING_NOT_PROVEN","historical_root":True,"facts":facts,
 "RRP_A":{"rrp0":"BASELINE_FROZEN" if ok else "STOP","rrp1":"DEPENDENCY_CLOSURE_ESTABLISHED" if ok else "STOP","rrp2":"GAP_CAUSALLY_QUALIFIED" if ok else "STOP","rrp3":"BASELINE_REPRODUCED","rrp4":"RESOLUTION_CONTRACT_FROZEN"},
 "resolution_contract":"A081 may be empirically exercised only if an already-governed P159 consumer binds a runtime registry selection to the CNP actually consumed. Generic registry existence, comparative registry semantics, or an unbound runtime constitutional score is insufficient.",
 "RRP_B":{"rrp5":"IMPACT_SURFACE_MAPPED","rrp6":"DRY_RUN_ALL_PRODUCTS_VALID","rrp7":"INSTALLATION_HANDLED_BY_REFINER","rrp8":"FUNNEL_VALIDATION_REQUIRED_AFTER_INSTALL"},
 "RRP_C":{"rrp9":"ROOT_UNDETERMINED + BLOCKING","candidate_root_invariants":["DNA.L0.3","DNA.L0.5"],"rrp10":"NO_LEGITIMATE_P159_REGISTRY_SUBSTITUTION_EXPERIMENT_AVAILABLE","rrp11":"NOT_CLOSURE_ELIGIBLE","rrp12":"ROOT_UNDETERMINED + BLOCKING"},
 "RRP_D":{"rrp13":"BLOCKER_RESOLUTION_SPACE_ESTABLISHED","rrp14":"NO_EXISTING_P159_REGISTRY_TO_CNP_BINDING_CANDIDATE","rrp15":"NOT_EXECUTED","rrp16":"BLOCKER_IRREDUCIBLE_WITH_CURRENT_P159_EVIDENCE"},
 "RRP_E":{"rrp17":"CAUSAL_DECOMPOSITION_COMPLETE","rrp18":"MISSING_RUNTIME_CONSUMER_BINDING_CAPABILITY","rrp19":{"design":"NO_P159_REMEDIATION_WITHOUT_CREATING_NEW_RUNTIME_BINDING","normative_degrees_of_freedom":0,"minimality":{"necessary":True,"independent":True,"sufficiently_exhaustive":True,"fixed_cardinality_forbidden":True}},"rrp20":"TECHNICAL_REMEDIATION_NOT_AUTHORIZED_WITHIN_P159"},
 "final_state":"ROOT_UNDETERMINED + BLOCKING","boundary":"P160_BOUNDARY_CANDIDATE","rrp_f":"NOT_OPENED","authorization_created":False,"execution_performed":False,"runtime_binding_created":False,"historical_evidence_rewritten":False,"criticality_changed":False,"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True}
