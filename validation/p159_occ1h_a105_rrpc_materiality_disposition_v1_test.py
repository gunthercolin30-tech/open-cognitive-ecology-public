from pathlib import Path
from ontology.occ1h_a105_rrpc_materiality_disposition import materiality
ROOT=Path.home()/"open-cognitive-ecology"
def test_materiality():
 r=materiality(ROOT); assert r["rrp9"]=="ROOT_MATERIALITY_RESOLVED" and r["root_materiality"]=="ROOT" and r["qualification_mode"]=="COMPOUND"
def test_component_evidence():
 r=materiality(ROOT); assert r["components_all_supported"] and all(r["component_evidence"].values())
def test_degradation_noncomposition():
 r=materiality(ROOT); assert not r["end_to_end_grand_chain_materialized"] and r["composition_inference_forbidden"] and r["rrp10"]=="INCONCLUSIVE_ELIMINATION_EXHAUSTED_WITH_CURRENT_EVIDENCE" and r["rrp11"]=="NOT_CLOSURE_ELIGIBLE" and r["rrp12"]=="ROOT + BLOCKING_INCONCLUSIVE" and r["rrp_d_required"]
def test_nonregression():
 r=materiality(ROOT); assert r["current_verdict"]=="INCONCLUSIVE" and r["historical_inconclusive_preserved"] and not r["production_runtime_modified"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
