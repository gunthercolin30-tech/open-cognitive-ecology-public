from pathlib import Path
from ontology.occ1h_a105_rrpd_blocker_resolution import blocker_resolution

def authority_gate(root):
    r=blocker_resolution(root)
    assert r["rrp16"]=="BLOCKER_IRREDUCIBLE_WITH_CURRENT_EVIDENCE"
    return {**r,
      "rrp17":"BLOCKER_CAUSALLY_DECOMPOSED",
      "causal_decomposition":[
        "A095/A097/A100/A101 component evidence exists under already governed semantics",
        "A105 lacks one bounded executable composition binding those component semantics end-to-end",
        "component verdict aggregation is not end-to-end evidence",
        "production wiring is not required to test bounded defensive composition",
        "creating new constitutional semantics or authority solely to obtain closure is forbidden"],
      "rrp18":"MISSING_ASSURANCE_CAPABILITY_CLASSIFIED",
      "gap_class":"TECHNICAL_COMPOSITIONAL_ASSURANCE_GAP_NOT_NORMATIVE_RULE_GAP",
      "normative_gap_detected":False,"production_capability_required":False,
      "rrp19":"LEGITIMATE_REMEDIATION_DESIGNED",
      "remediation":"BOUNDED_NON_PRODUCTION_A105_COMPOSITIONAL_SURROGATE_HARNESS",
      "remediation_contract":[
        "reuse existing governed A095/A097/A100/A101 semantics without changing them",
        "bind them only inside an isolated temporary non-production fixture",
        "exercise intact-control and controlled broken-link cases across the composed chain",
        "require non-compensatory fail-closed discrimination at every link",
        "do not infer production grand-chain resistance from the bounded experiment",
        "persist evidence only; never simulated runtime mutation",
        "independent RRP22 requalification required"],
      "normative_degrees_of_freedom":0,
      "normative_dof_minimality":{"necessary":True,"independent":True,"sufficiently_exhaustive":True,"fixed_cardinality_forbidden":True},
      "minimality":"NO_NEW_NORMATIVE_CHOICE_NEEDED_FOR_BOUNDED_COMPOSITIONAL_ASSURANCE_EXPERIMENT",
      "existing_authority_basis":["existing RRP defensive-validation authority","already governed component semantics and frozen A105 resolution contract","fail-closed and non-compensatory ROOT requirements"],
      "new_normative_decision_required":False,
      "rrp20":"TECHNICAL_REMEDIATION_AUTHORIZED",
      "authority_basis":"existing RRP defensive-validation authority authorizes bounded non-production assurance only; no production, constitutional, or normative authority is created",
      "production_path_authorized":False,"rrp21_authorized":True,
      "rrp21_authorized_scope":"BOUNDED_NON_PRODUCTION_A105_COMPOSITIONAL_ASSURANCE_EXPERIMENT_ONLY",
      "rrp_f_required":True,"current_verdict":"INCONCLUSIVE",
      "production_runtime_modified":False,"criticality_changed":False,
      "occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,
      "functional_only":True,"phenomenology_undetermined":True}
