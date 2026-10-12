from ontology.occ1h_a021_final_rrp9_to_rrp12_disposition import evaluate
def test_final_disposition(): r=evaluate(); assert r["rrp9"]=="ROOT_MATERIALITY_RESOLVED" and r["rrp10"]=="INCONCLUSIVE_ELIMINATED" and r["rrp11"]=="CLOSURE_ELIGIBLE_FOR_A021_ONLY" and r["rrp12"]=="ROOT + RESOLVED_EMPIRICALLY" and r["final_verdict"]=="RESISTED"
def test_root_non_compensatory(): r=evaluate(); assert r["root_criticality"]=="ROOT" and not r["criticality_changed"] and not r["a021_blocks_occ1h"]
def test_history_and_scope(): r=evaluate(); assert r["historical_inconclusive_preserved"] and r["evidence_scope"]=="BOUNDED_P159_ASSURANCE_MODEL" and r["governed_semantic_identity"]=="MAY -> PERMITS"
def test_boundaries(): r=evaluate(); assert not r["real_builder_modified"] and not r["runtime_execution"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"] and r["functional_only"] and r["phenomenology_undetermined"]
