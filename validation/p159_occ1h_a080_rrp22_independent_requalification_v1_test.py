from ontology.occ1h_a080_rrp22_independent_requalification import evaluate
def test_a080_rrp22_independent():
 r=evaluate(); assert r["rrp22"]=="PASSED_BOUNDED"; assert r["candidate_verdict"]=="RESISTED"; assert not r["imports_rrp21"] and not r["executes_rrp21"]
def test_a080_rrp22_degradation(tmp_path):
 d=tmp_path/"ontology"; d.mkdir(); from pathlib import Path; src=Path.home()/"open-cognitive-ecology"/"ontology"/"occ_compiled_normative_profile.py"; t=src.read_text().replace('"REVOKED":set()','"REVOKED":{"ACTIVE"}'); (d/"occ_compiled_normative_profile.py").write_text(t); r=evaluate(tmp_path); assert r["rrp22"]=="FAILED_FAIL_CLOSED"; assert r["candidate_verdict"]=="INCONCLUSIVE"
def test_a080_rrp22_return_gate():
 r=evaluate(); assert r["return_to_rrp9_12_required"]
def test_a080_rrp22_boundaries():
 r=evaluate(); assert not r["runtime_activation_executed"] and not r["authority_created"] and not r["p160_semantics_created"] and not r["occ1h_closed"] and not r["p159_final_lock"] and not r["p160_opened"]
