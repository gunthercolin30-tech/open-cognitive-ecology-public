from pathlib import Path
from ontology.occ1h_a105_rrpa_baseline_contract import baseline
ROOT=Path.home()/"open-cognitive-ecology"
def test_functional():
 r=baseline(ROOT); assert r["rrp0"]=="BASELINE_FROZEN" and r["rrp1"]=="DEPENDENCY_CLOSURE_ESTABLISHED" and r["rrp2"]=="GAP_CAUSALLY_QUALIFIED" and r["rrp3"]=="BASELINE_REPRODUCED" and r["rrp4"]=="RESOLUTION_CONTRACT_FROZEN"
def test_identity_and_dependencies():
 r=baseline(ROOT); assert r["scenario"]=="A105" and r["root_materiality"]=="ROOT" and r["qualification_mode"]=="COMPOUND"; assert r["historical_prerequisites"]==["A095","A100","A101"]; assert r["dependency_current_states"]=={"A095":"RESISTED","A097":"DETECTED","A100":"RESISTED","A101":"RESISTED"}
def test_degradation_contract():
 r=baseline(ROOT); c=r["resolution_contract"]; assert c["success_must_be_non_compensatory"] and c["no_root_reclassification_for_closure"] and c["historical_inconclusive_preserved"] and c["candidate_positive_verdict_requires_empirical_evidence"]
def test_nonregression():
 r=baseline(ROOT); assert r["historical_current_verdict"]=="INCONCLUSIVE" and not r["production_runtime_modified"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
