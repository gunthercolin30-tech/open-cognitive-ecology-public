from ontology.occ1h_a084_rrpf_clock_rollback_surrogate_requalification import temporal_gate,rrpf
def test_nominal(): assert temporal_gate(100,101)
def test_degradation(): assert not temporal_gate(100,100) and not temporal_gate(100,99) and not temporal_gate(100,99,True) and not temporal_gate(100,101,provenance_ok=False)
def test_independent_requalification(): r=rrpf(); assert r["rrp21"]=="BOUNDED_NON_PRODUCTION_CLOCK_ROLLBACK_SURROGATE_EXPERIMENT_EXECUTED" and r["discrimination"] and r["rrp22"]=="INDEPENDENT_REQUALIFICATION_PASSED_BOUNDED" and r["candidate_verdict"]=="RESISTED"
def test_nonregression(): r=rrpf(); assert r["evidence_scope"]=="BOUNDED_NON_PRODUCTION_SURROGATE_ONLY" and r["historical_inconclusive_preserved"] and r["final_disposition_required"] and not r["production_runtime_modified"] and not r["production_clock_path_materialized"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
