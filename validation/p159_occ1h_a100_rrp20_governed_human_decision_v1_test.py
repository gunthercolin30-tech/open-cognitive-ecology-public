from ontology.occ1h_a100_rrp20_governed_human_decision import governed_decision
def test_decision():
 r=governed_decision()
 assert r["human_confirmation"]=="D1_AND_D2_CONFIRMED_AS_FORMULATED"
 assert r["rrp20_post_decision"]=="GOVERNED_NORMATIVE_DECISION_RECORDED"
 assert r["rrp21_authorized"]
def test_minimality():
 r=governed_decision()
 assert r["normative_dof_count"]==2 and not r["additional_implicit_normative_dof"]
 assert "explicitement autorisée" in r["decision_D1"]
 assert "préexistante et indépendante" in r["decision_D2"]
def test_degradation():
 r=governed_decision()
 assert r["self_certification_forbidden"] and r["rrp22_independent_requalification_required"]
 assert r["current_verdict"]=="INCONCLUSIVE" and not r["transition_materialized"]
def test_nonregression():
 r=governed_decision()
 assert not r["production_runtime_modified"] and not r["criticality_changed"]
 assert not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
