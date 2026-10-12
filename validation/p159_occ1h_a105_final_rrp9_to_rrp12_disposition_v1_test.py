from pathlib import Path
from ontology.occ1h_a105_final_rrp9_to_rrp12_disposition import final_disposition
ROOT=Path.home()/"open-cognitive-ecology"
def test_final_disposition():
 r=final_disposition(ROOT); assert r["rrp9"]=="ROOT_MATERIALITY_RESOLVED" and r["rrp10"]=="INCONCLUSIVE_ELIMINATED" and r["rrp11"]=="CLOSURE_ELIGIBLE_FOR_A105_ONLY" and r["rrp12"]=="ROOT + RESOLVED_EMPIRICALLY" and r["final_verdict"]=="RESISTED"
def test_scope():
 r=final_disposition(ROOT); assert r["root_materiality"]=="ROOT" and r["qualification_mode"]=="COMPOUND" and r["evidence_scope"]=="BOUNDED_NON_PRODUCTION_COMPOSITIONAL_SURROGATE_ONLY" and not r["production_grand_chain_materialized"]
def test_history_and_blocker():
 r=final_disposition(ROOT); assert r["historical_inconclusive_preserved"] and not r["criticality_changed"] and not r["a105_blocks_occ1h"] and r["occ1h_global_consolidation_required"]
def test_nonregression():
 r=final_disposition(ROOT); assert not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"] and not r["production_runtime_modified"] and r["functional_only"] and r["phenomenology_undetermined"]
