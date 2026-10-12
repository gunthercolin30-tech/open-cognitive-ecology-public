from pathlib import Path
from ontology.occ1h_a105_rrpf_compositional_assurance_requalification import experiment
ROOT=Path.home()/"open-cognitive-ecology"
def test_rrp21():
 r=experiment(ROOT); assert r["rrp21"]=="BOUNDED_NON_PRODUCTION_A105_COMPOSITIONAL_ASSURANCE_EXPERIMENT_EXECUTED" and r["rrp21_discrimination_ok"] and r["non_compensatory_fail_closed"] and all(r["component_bindings"].values())
def test_rrp22_independent():
 r=experiment(ROOT); assert r["rrp22"]=="INDEPENDENT_REQUALIFICATION_SUPPORTS_RETURN_TO_RRP9_12" and r["rrp22_discrimination_ok"] and r["return_to_rrp9_12_required"] and r["candidate_verdict"]=="RESISTED"
def test_degradation():
 r=experiment(ROOT); assert all(v=="REJECTED_FAIL_CLOSED" for k,v in r["rrp21_results"].items() if k!="intact_control"); assert all(v=="REJECTED_FAIL_CLOSED" for k,v in r["rrp22_results"].items() if k!="intact_control")
def test_nonregression():
 r=experiment(ROOT); assert r["root_materiality_candidate"]=="ROOT" and r["historical_inconclusive_preserved"] and r["evidence_scope"]=="BOUNDED_NON_PRODUCTION_COMPOSITIONAL_SURROGATE_ONLY" and not r["production_grand_chain_materialized"] and not r["production_runtime_modified"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
