from ontology.occ1h_a080_rrp9_12_final_disposition import evaluate
def test_a080_final_root_materiality():
 r=evaluate(); assert r["root_materiality"]["classification"]=="ROOT"; assert r["root_materiality"]["applicable_root_invariants"]==["DNA.L0.3"]; assert len(r["root_materiality"]["causal_chain"])==5
def test_a080_final_disposition():
 r=evaluate(); assert r["rrp10"].startswith("INCONCLUSIVE_ELIMINATED"); assert r["rrp11"]=="CLOSURE_ELIGIBLE_FOR_A080_ONLY"; assert r["rrp12"]=="ROOT + RESOLVED_EMPIRICALLY"; assert r["final_verdict"]=="RESISTED"
def test_a080_final_degradation(tmp_path):
 d=tmp_path/"ontology"; d.mkdir(); from pathlib import Path; home=Path.home()/"open-cognitive-ecology"/"ontology"; c=(home/"occ_compiled_normative_profile.py").read_text().replace('"REVOKED":set()','"REVOKED":{"ACTIVE"}'); (d/"occ_compiled_normative_profile.py").write_text(c); (d/"occ1h_a080_rrp22_independent_requalification.py").write_text((home/"occ1h_a080_rrp22_independent_requalification.py").read_text()); r=evaluate(tmp_path); assert r["rrp12"]=="ROOT_UNDETERMINED + BLOCKING"; assert r["final_verdict"]=="INCONCLUSIVE"
def test_a080_final_boundaries_and_history():
 r=evaluate(); assert r["historical_record_preserved"]; assert not r["runtime_activation_claimed"] and not r["p160_semantics_claimed"]; assert not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
