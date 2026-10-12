from ontology.occ1h_a081_rrpv21_macros_a_to_e_registry_binding_gap import evaluate
def test_a081_identity_and_gap():
 r=evaluate(); assert r["canonical_label"]=="registry substitution"; assert all(r["facts"].values())
def test_a081_no_false_resistance():
 r=evaluate(); assert r["RRP_C"]["rrp12"]=="ROOT_UNDETERMINED + BLOCKING"; assert r["final_state"]=="ROOT_UNDETERMINED + BLOCKING"
def test_a081_no_p159_manufactured_binding():
 r=evaluate(); assert r["RRP_D"]["rrp16"]=="BLOCKER_IRREDUCIBLE_WITH_CURRENT_P159_EVIDENCE"; assert r["RRP_E"]["rrp20"]=="TECHNICAL_REMEDIATION_NOT_AUTHORIZED_WITHIN_P159"; assert r["rrp_f"]=="NOT_OPENED"
def test_a081_boundaries():
 r=evaluate(); assert not r["authorization_created"] and not r["execution_performed"] and not r["runtime_binding_created"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
