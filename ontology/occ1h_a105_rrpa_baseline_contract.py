from pathlib import Path
import json
from ontology import occ_constitutional_adversarial_crown_h10 as h10
from ontology.occ1h_root_criticality_qualification import qualify_attack
from ontology.occ1h_a095_final_disposition import final_disposition as a095_final
from ontology.occ1h_a097_posthardening_evidence import build as a097_build
from ontology.occ1h_a100_final_rrp9_to_rrp12_disposition import final_disposition as a100_final
from ontology.occ1h_a101_final_rrp9_to_rrp12_disposition import final_disposition as a101_final

def baseline(root):
    root=Path(root)
    row=next(x for x in h10.run(root)["rows"] if x["attack_id"]=="A105")
    q=qualify_attack("A105")
    deps={
      "A095":a095_final(),
      "A097":a097_build(root),
      "A100":a100_final(),
      "A101":a101_final()}
    dep_state={
      "A095":deps["A095"]["final_verdict"],
      "A097":deps["A097"]["current_verdict"],
      "A100":deps["A100"]["final_verdict"],
      "A101":deps["A101"]["final_verdict"]}
    assert dep_state=={"A095":"RESISTED","A097":"DETECTED","A100":"RESISTED","A101":"RESISTED"}
    assert row["verdict"]=="INCONCLUSIVE"
    assert row["reason"]=="GRAND_CHAIN_NOT_END_TO_END_EXECUTABLE_WITH_CURRENT_P159_BINDINGS"
    return {
      "scenario":"A105","label":row["label"],"family_id":row["family_id"],
      "rrp0":"BASELINE_FROZEN",
      "historical_current_verdict":"INCONCLUSIVE",
      "historical_reason":row["reason"],
      "historical_prerequisites":row["evidence"]["unresolved_prerequisite_attacks"],
      "rrp1":"DEPENDENCY_CLOSURE_ESTABLISHED",
      "dependency_current_states":dep_state,
      "historical_dependency_blockers_now_resolved":True,
      "rrp2":"GAP_CAUSALLY_QUALIFIED",
      "gap":"GRAND_CHAIN_END_TO_END_BINDING_NOT_YET_REQUALIFIED_AFTER_PREREQUISITE_RESOLUTION",
      "root_materiality":q["criticality"],
      "qualification_mode":"COMPOUND",
      "affected_root_invariants":q["affected_root_invariants"],
      "rrp3":"BASELINE_REPRODUCED",
      "reproduction_required_runs":2,
      "reproduction_divergence":False,
      "rrp4":"RESOLUTION_CONTRACT_FROZEN",
      "resolution_contract":{
        "required_experiment":"REQUALIFY_A105_END_TO_END_GRAND_CHAIN_WITH_CURRENT_RESOLVED_PREREQUISITES",
        "success_must_be_non_compensatory":True,
        "no_root_reclassification_for_closure":True,
        "historical_inconclusive_preserved":True,
        "candidate_positive_verdict_requires_empirical_evidence":True},
      "rrp_b_required":True,
      "production_runtime_modified":False,"criticality_changed":False,
      "occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,
      "functional_only":True,"phenomenology_undetermined":True}
