from ontology.occ1h_a046_rrpv21_macros_a_to_e_geographic_scope_minimality import evaluate
def test_a_to_e(): r=evaluate(); assert r["RRP_C"]["FINAL_DISPOSITION"]=="ROOT_UNDETERMINED + BLOCKING" and r["RRP_E"]["RRP20"]["gate"]=="NEW_NORMATIVE_DECISION_REQUIRED"
def test_minimality(): r=evaluate(); m=r["RRP_E"]["minimality"]; assert m["derived_decision_count"]==2 and m["necessary"] and m["independent"] and m["sufficiently_exhaustive_for_A046"]
def test_authority_barrier(): r=evaluate(); assert r["RRP_F"]["status"]=="NOT_OPENED_AUTHORITY_BARRIER" and not r["RRP_E"]["RRP19"]["values_selected_by_system"]
def test_boundaries(): r=evaluate(); assert not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"] and r["functional_only"] and r["phenomenology_undetermined"]
