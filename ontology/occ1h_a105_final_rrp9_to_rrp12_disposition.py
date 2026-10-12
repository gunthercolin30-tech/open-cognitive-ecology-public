from pathlib import Path
from ontology.occ1h_a105_rrpf_compositional_assurance_requalification import experiment

def final_disposition(root):
    f=experiment(root)
    assert f["rrp21_discrimination_ok"] is True
    assert f["rrp22_discrimination_ok"] is True
    assert f["candidate_verdict"]=="RESISTED"
    assert f["return_to_rrp9_12_required"] is True
    assert f["production_grand_chain_materialized"] is False
    return {
      "scenario":"A105",
      "rrp9":"ROOT_MATERIALITY_RESOLVED",
      "root_materiality":"ROOT",
      "qualification_mode":"COMPOUND",
      "rrp10":"INCONCLUSIVE_ELIMINATED",
      "rrp11":"CLOSURE_ELIGIBLE_FOR_A105_ONLY",
      "rrp12":"ROOT + RESOLVED_EMPIRICALLY",
      "final_verdict":"RESISTED",
      "resolution_basis":"INDEPENDENT_RRP21_RRP22_BOUNDED_COMPOSITIONAL_ASSURANCE",
      "evidence_scope":"BOUNDED_NON_PRODUCTION_COMPOSITIONAL_SURROGATE_ONLY",
      "production_grand_chain_materialized":False,
      "historical_inconclusive_preserved":True,
      "criticality_changed":False,
      "a105_blocks_occ1h":False,
      "all_known_root_scenarios_candidate_resolved":True,
      "occ1h_global_consolidation_required":True,
      "occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,
      "production_runtime_modified":False,
      "functional_only":True,"phenomenology_undetermined":True}
