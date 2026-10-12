from ontology.occ1h_a080_rrp21_revoked_activation_bounded_experiment import evaluate
def test_a080_rrp21_functional():
 r=evaluate(); assert r["rrp21"]=="COMPLETE_BOUNDED"; assert r["observed_outcome"]=="REJECT_REACTIVATION"; assert r["candidate_verdict"]=="RESISTED_BOUNDED"
def test_a080_rrp21_degradation(tmp_path):
 p=tmp_path/"ontology"; p.mkdir(); src=__import__("pathlib").Path.home()/"open-cognitive-ecology"/"ontology"/"occ_compiled_normative_profile.py"; t=src.read_text(); t=t.replace('"REVOKED":set()','"REVOKED":{"ACTIVE"}'); (p/"occ_compiled_normative_profile.py").write_text(t); r=evaluate(tmp_path); assert r["rrp21"]=="INCOMPLETE"; assert r["candidate_verdict"]=="INCONCLUSIVE"
def test_a080_rrp21_no_runtime_or_authority():
 r=evaluate(); assert not r["runtime_activation_executed"] and not r["authority_created"] and not r["p160_semantics_created"]
def test_a080_rrp21_boundaries():
 r=evaluate(); assert not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]; assert r["rrp22"]=="INDEPENDENT_REQUALIFICATION_REQUIRED"
