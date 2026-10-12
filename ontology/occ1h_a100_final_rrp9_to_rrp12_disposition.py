from ontology.occ1h_a100_rrpf_governed_transition_requalification import experiment

def final_disposition():
    e=experiment()
    assert e["rrp21_discrimination_ok"] and e["rrp22_discrimination_ok"]
    assert e["return_to_rrp9_12_required"] and e["candidate_verdict"]=="RESISTED"
    return {
      "scenario":"A100",
      "rrp9":"ROOT_MATERIALITY_RESOLVED",
      "causal_chain":[
        "A100 CIS to permanent sovereignty transition",
        "an unauthorized, circular, ambiguous, self-ratified, non-independent, or provenance-unverifiable transition would permit permanent sovereignty without legitimate pre-existing constitutional authorization",
        "DNA-L0.1 self-legitimacy invariant is affected"
      ],
      "root_invariant":"DNA-L0.1_SELF_LEGITIMACY",
      "root_materiality":"ROOT",
      "rrp10":"INCONCLUSIVE_ELIMINATED",
      "evidence_basis":[
        "human-governed D1/D2 transition contract recorded",
        "RRP21 bounded governed control accepted",
        "RRP21 seven invalid authorization variants rejected fail-closed",
        "RRP22 independent recomputation reproduced the same discrimination"
      ],
      "rrp11":"CLOSURE_ELIGIBLE_FOR_A100_ONLY",
      "rrp12":"ROOT + RESOLVED_EMPIRICALLY",
      "final_verdict":"RESISTED",
      "evidence_scope":"BOUNDED_NON_PRODUCTION_GOVERNED_TRANSITION_ASSURANCE_ONLY",
      "production_transition_materialized":False,
      "historical_inconclusive_preserved":True,
      "criticality_changed":False,
      "a100_blocks_occ1h":False,
      "occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,
      "functional_only":True,"phenomenology_undetermined":True}
