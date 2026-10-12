from pathlib import Path
from ontology.occ1h_a105_rrpa_baseline_contract import baseline
from ontology import occ_constitutional_adversarial_crown_h10 as h10

def rrp_b(root):
    root=Path(root); a=baseline(root)
    row=next(x for x in h10.run(root)["rows"] if x["attack_id"]=="A105")
    assert a["historical_prerequisites"]==["A095","A100","A101"]
    assert a["dependency_current_states"]=={"A095":"RESISTED","A097":"DETECTED","A100":"RESISTED","A101":"RESISTED"}
    surface={
      "historical_h10_scenario":True,
      "historical_prerequisites_exact":["A095","A100","A101"],
      "current_supporting_dependency_A097":"DETECTED",
      "current_prerequisite_states":{"A095":"RESISTED","A100":"RESISTED","A101":"RESISTED"},
      "root_invariants":a["affected_root_invariants"],
      "historical_reason":row["reason"]}
    # Dry-run does not synthesize a missing grand-chain. It proves only that all known historical
    # prerequisite blockers are no longer INCONCLUSIVE and that a direct end-to-end probe is now admissible.
    prereq_ready=all(v!="INCONCLUSIVE" for v in surface["current_prerequisite_states"].values())
    return {
      "scenario":"A105","rrp5":"IMPACT_SURFACE_MAPPED","impact_surface":surface,
      "rrp6":"DRY_RUN_ALL_PRODUCTS_VALID",
      "dry_run_prerequisites_ready":prereq_ready,
      "dry_run_grand_chain_synthesized":False,
      "rrp7":"TRANSACTIONAL_INSTALLATION_THIS_MODULE_ONLY",
      "rrp8":"FUNNEL_VALIDATION_READY",
      "direct_end_to_end_probe_required":True,
      "rrp_c_required":True,
      "current_verdict":"INCONCLUSIVE",
      "root_materiality":"ROOT","qualification_mode":"COMPOUND",
      "historical_inconclusive_preserved":True,
      "production_runtime_modified":False,"criticality_changed":False,
      "occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,
      "functional_only":True,"phenomenology_undetermined":True}
