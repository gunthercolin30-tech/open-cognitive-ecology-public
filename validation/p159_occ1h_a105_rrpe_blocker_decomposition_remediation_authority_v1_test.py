from pathlib import Path
from ontology.occ1h_a105_rrpe_blocker_decomposition_remediation_authority import authority_gate
ROOT=Path.home()/"open-cognitive-ecology"
def test_rrp17_20():
 r=authority_gate(ROOT); assert r["rrp17"]=="BLOCKER_CAUSALLY_DECOMPOSED" and r["rrp18"]=="MISSING_ASSURANCE_CAPABILITY_CLASSIFIED" and r["rrp19"]=="LEGITIMATE_REMEDIATION_DESIGNED" and r["rrp20"]=="TECHNICAL_REMEDIATION_AUTHORIZED"
def test_normative_minimality():
 r=authority_gate(ROOT); assert r["gap_class"]=="TECHNICAL_COMPOSITIONAL_ASSURANCE_GAP_NOT_NORMATIVE_RULE_GAP" and not r["normative_gap_detected"] and r["normative_degrees_of_freedom"]==0 and not r["new_normative_decision_required"]
def test_authority_boundary():
 r=authority_gate(ROOT); assert r["rrp21_authorized"] and r["rrp21_authorized_scope"]=="BOUNDED_NON_PRODUCTION_A105_COMPOSITIONAL_ASSURANCE_EXPERIMENT_ONLY" and not r["production_path_authorized"] and r["production_capability_required"] is False and r["rrp_f_required"]
def test_nonregression():
 r=authority_gate(ROOT); assert r["current_verdict"]=="INCONCLUSIVE" and not r["production_runtime_modified"] and not r["criticality_changed"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
