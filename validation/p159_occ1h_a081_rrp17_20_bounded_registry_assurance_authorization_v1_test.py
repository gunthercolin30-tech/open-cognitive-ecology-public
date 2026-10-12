from ontology.occ1h_a081_rrp17_20_bounded_registry_assurance_authorization import evaluate
def test_a081_authority_basis(): r=evaluate(); assert all(r["facts"].values()); assert r["RRP20"]=="EXISTING_NORMATIVE_AUTHORITY_SUFFICIENT"
def test_a081_zero_normative_dof(): r=evaluate(); assert r["RRP19"]["new_normative_degrees_of_freedom"]==0; assert all(r["RRP19"]["minimality"].values())
def test_a081_bounded_only(): r=evaluate(); assert r["technical_remediation_authorized"]; assert not r["RRP19"]["real_runtime_binding_claimed"]; assert not r["real_runtime_consumer_graph_materialized"] and not r["p160_semantics_invented"]
def test_a081_barriers(): r=evaluate(); assert r["rrp21"]=="OPEN_FOR_BOUNDED_P159_ASSURANCE_EXPERIMENT"; assert r["rrp22"]=="REQUIRED_INDEPENDENTLY_AFTER_RRP21"; assert not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
