from pathlib import Path
from ontology.occ1h_a105_rrpb_impact_dryrun import rrp_b
ROOT=Path.home()/"open-cognitive-ecology"
def test_functional():
 r=rrp_b(ROOT); assert r["rrp5"]=="IMPACT_SURFACE_MAPPED" and r["rrp6"]=="DRY_RUN_ALL_PRODUCTS_VALID" and r["rrp7"]=="TRANSACTIONAL_INSTALLATION_THIS_MODULE_ONLY" and r["rrp8"]=="FUNNEL_VALIDATION_READY"
def test_dependency_semantics():
 r=rrp_b(ROOT); s=r["impact_surface"]; assert s["historical_prerequisites_exact"]==["A095","A100","A101"]; assert s["current_supporting_dependency_A097"]=="DETECTED"; assert s["current_prerequisite_states"]=={"A095":"RESISTED","A100":"RESISTED","A101":"RESISTED"}; assert r["dry_run_prerequisites_ready"]
def test_degradation():
 r=rrp_b(ROOT); assert not r["dry_run_grand_chain_synthesized"] and r["direct_end_to_end_probe_required"] and r["current_verdict"]=="INCONCLUSIVE" and r["rrp_c_required"]
def test_nonregression():
 r=rrp_b(ROOT); assert r["root_materiality"]=="ROOT" and r["historical_inconclusive_preserved"] and not r["production_runtime_modified"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
