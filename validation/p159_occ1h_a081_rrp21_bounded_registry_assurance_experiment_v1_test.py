from ontology.occ1h_a081_rrp21_bounded_registry_assurance_experiment import run,verify_binding,CONSUMERS
import hashlib
def test_a081_rrp21_functional():
 r=run(); assert r["all_required_discriminations_passed"]; assert r["experimental_verdict"]=="RESISTED_BOUNDED"
def test_a081_rrp21_degradation():
 h=hashlib.sha256(b"x").hexdigest(); assert not verify_binding({}, "UnknownConsumer",h)["accepted"]; assert not verify_binding(None,CONSUMERS[0],h)["accepted"]; assert not verify_binding({},CONSUMERS[0],"bad")["accepted"]
def test_a081_rrp21_substitution():
 r=run(); assert not r["cases"]["registry_substitution"]["accepted"]; assert not r["cases"]["cnp_substitution"]["accepted"]
def test_a081_rrp21_boundaries():
 r=run(); assert not r["real_runtime_consumer_graph_materialized"]; assert not r["real_runtime_binding_claimed"]; assert r["rrp22"]=="REQUIRED_INDEPENDENTLY"; assert not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
