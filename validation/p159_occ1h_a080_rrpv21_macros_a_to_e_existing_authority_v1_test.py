from ontology.occ1h_a080_rrpv21_macros_a_to_e_existing_authority import evaluate
def test_a080_identity_and_history():
 r=evaluate(); assert r["source_identity_ok"]; assert r["historical_verdict"]=="INCONCLUSIVE"
def test_a080_existing_authority_no_new_norm():
 r=evaluate(); assert r["RRP_E"]["rrp20"]=="EXISTING_NORMATIVE_AUTHORITY_SUFFICIENT"; assert r["RRP_E"]["rrp19"]["normative_degrees_of_freedom"]==0
def test_a080_stays_blocking_before_experiment():
 r=evaluate(); assert r["RRP_C"]["rrp12"]=="ROOT_UNDETERMINED + BLOCKING"; assert r["rrp_f"]=="OPEN_FOR_BOUNDED_P159_ASSURANCE_EXPERIMENT"
def test_a080_boundaries():
 r=evaluate(); assert not r["authorization_created"] and not r["execution_performed"] and not r["runtime_created"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
