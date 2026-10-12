from ontology.occ1h_a100_final_rrp9_to_rrp12_disposition import final_disposition
def test_final_rrp9_12():
 r=final_disposition(); assert r["rrp9"]=="ROOT_MATERIALITY_RESOLVED" and r["rrp10"]=="INCONCLUSIVE_ELIMINATED" and r["rrp11"]=="CLOSURE_ELIGIBLE_FOR_A100_ONLY" and r["rrp12"]=="ROOT + RESOLVED_EMPIRICALLY"
def test_final_verdict():
 r=final_disposition(); assert r["root_materiality"]=="ROOT" and r["root_invariant"]=="DNA-L0.1_SELF_LEGITIMACY" and r["final_verdict"]=="RESISTED" and not r["a100_blocks_occ1h"]
def test_evidence_scope():
 r=final_disposition(); assert r["evidence_scope"]=="BOUNDED_NON_PRODUCTION_GOVERNED_TRANSITION_ASSURANCE_ONLY" and not r["production_transition_materialized"] and r["historical_inconclusive_preserved"] and not r["criticality_changed"]
def test_boundaries():
 r=final_disposition(); assert not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"] and r["functional_only"] and r["phenomenology_undetermined"]
