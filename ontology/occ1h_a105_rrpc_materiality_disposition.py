from pathlib import Path
from ontology.occ1h_a105_rrpb_impact_dryrun import rrp_b
from ontology.occ1h_a095_rrpf_bounded_provenance_assurance import experiment as e95
from ontology.occ1h_a097_posthardening_evidence import build as e97
from ontology.occ1h_a100_rrpf_governed_transition_requalification import experiment as e100
from ontology.occ1h_a101_rrpf_bounded_assurance_requalification import experiment as e101

def materiality(root):
 r=rrp_b(root); a95=e95(); a97=e97(root); a100=e100(); a101=e101()
 evidence={
  "A095_bounded_provenance_assurance":a95.get("experiment_passed") is True,
  "A097_compound_joint_detection":a97.get("current_verdict")=="DETECTED" and a97.get("compound_execution") is True,
  "A100_governed_transition_discrimination":a100.get("rrp21_discrimination_ok") is True and a100.get("rrp22_discrimination_ok") is True,
  "A101_bounded_verifier_weakening_discrimination":a101.get("discrimination_ok") is True}
 components_all_supported=all(evidence.values())
 # Crucial non-compositionality rule: separate bounded component evidence is not an
 # executable A105 grand-chain trajectory. No connector in current evidence binds
 # A095 -> A097 -> A100 -> A101 into one end-to-end execution.
 end_to_end_materialized=False
 return {
  "scenario":"A105","rrp9":"ROOT_MATERIALITY_RESOLVED",
  "root_materiality":"ROOT","qualification_mode":"COMPOUND",
  "component_evidence":evidence,"components_all_supported":components_all_supported,
  "end_to_end_grand_chain_materialized":end_to_end_materialized,
  "composition_inference_forbidden":True,
  "rrp10":"INCONCLUSIVE_ELIMINATION_EXHAUSTED_WITH_CURRENT_EVIDENCE",
  "rrp11":"NOT_CLOSURE_ELIGIBLE",
  "rrp12":"ROOT + BLOCKING_INCONCLUSIVE",
  "blocker":"NO_EXECUTABLE_END_TO_END_A105_GRAND_CHAIN_BINDING_ACROSS_CURRENT_COMPONENT_EVIDENCE",
  "rrp_d_required":True,"current_verdict":"INCONCLUSIVE",
  "historical_inconclusive_preserved":True,"production_runtime_modified":False,
  "criticality_changed":False,"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,
  "functional_only":True,"phenomenology_undetermined":True}
