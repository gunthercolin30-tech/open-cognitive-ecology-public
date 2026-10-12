from ontology.occ1h_a046_governed_geographic_scope_decision import decision
def test_decision(): r=decision(); assert r["decision_status"]=="HUMAN_CONFIRMED" and r["normative_degrees_of_freedom"]==2
def test_d1_fail_closed(): r=decision(); assert "fail-closed" in r["D1"]["rule"] and "GLOBAL" in r["D1"]["rule"]
def test_d2_new_governance(): r=decision(); assert "requires a new governed decision" in r["D2"]["rule"] and "wildcard" in r["D2"]["rule"]
def test_boundaries(): r=decision(); assert not r["retroactive_legitimation"] and not r["checker_modified"] and not r["runtime_modified"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
