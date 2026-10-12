from pathlib import Path
from ontology.occ1h_a105_rrpd_blocker_resolution import blocker_resolution
ROOT=Path.home()/"open-cognitive-ecology"
def test_functional():
 r=blocker_resolution(ROOT); assert r["rrp13"]=="BLOCKER_RESOLUTION_SPACE_EXHAUSTED" and r["rrp14"]=="NO_ADMISSIBLE_EXISTING_RESOLUTION_CANDIDATE_PROVEN" and r["rrp15"]=="BLOCKER_RESOLUTION_EXPERIMENT_NOT_ADMISSIBLE_WITH_CURRENT_EVIDENCE" and r["rrp16"]=="BLOCKER_IRREDUCIBLE_WITH_CURRENT_EVIDENCE"
def test_causal_boundary():
 r=blocker_resolution(ROOT); assert r["component_evidence_sufficient_individually"] and not r["component_evidence_sufficient_compositionally"] and r["synthetic_composition_forbidden"]
def test_degradation():
 r=blocker_resolution(ROOT); assert r["current_verdict"]=="INCONCLUSIVE" and r["rrp_e_required"] and r["root_materiality"]=="ROOT"
def test_nonregression():
 r=blocker_resolution(ROOT); assert r["historical_inconclusive_preserved"] and not r["production_runtime_modified"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
