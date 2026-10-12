from pathlib import Path
from ontology import occ_constitutional_adversarial_crown_h7 as h7
from validation.p162g6_index75_h7_governance_harness import run_h7,_make_lease
from ontology import occ_independent_constitutional_verifier as verifier
ROOT=Path(__file__).resolve().parents[1]
def test_a075_probe_is_executable_but_bounded():
 a={x["attack_id"]:x for x in run_h7(ROOT)["rows"]}["A075"]
 assert a["verdict"]=="INCONCLUSIVE"
 e=a["evidence"]
 if "probe_result" in e:
  assert e["probe_result"]=="DETECTED"
 else:
  assert e.get("replacement_probe_result") in ("REJECTED","DETECTED","DETECTED_BY_IDENTITY_BINDING")
  x=e.get("loaded_v2",{})
  identity=(x.get("loaded_v2_identity_proven") is True)
  assert e.get("full_verifier_replacement_path_materialized") is identity
  assert e.get("loaded_v2_self_certification_materialized") is (identity and x.get("self_certification_attempt_reached") is True)
  if identity:
   assert x.get("loaded_from_sandbox") is True
   assert x.get("loaded_verifier_sha256")==e["replacement"]["v2_sha256"]
   assert e.get("loaded_v2_probe_result") in ("COUNTEREXAMPLE_CANDIDATE","REJECTED")
  else:
   assert e.get("loaded_v2_probe_result")=="INDETERMINATE"
 if "failed" in e:
  assert "IVI-11" in e["failed"]
def test_a075_causal_degradation_without_self_activation():
 lease=_make_lease(ROOT,0); sb_ctx,sb=h7._sandbox(ROOT,lease)
 try:
  r=verifier.verify(sb); assert "IVI-11" not in r.get("failed_check_ids",[])
  def attack(x): x.setdefault("lifecycle_model",{})["self_activation"]=True
  h7._mut(sb,attack,True); r2=verifier.verify(sb)
  assert "IVI-11" in r2.get("failed_check_ids",[])
  assert r2.get("verdict")==verifier.REJECTED
 finally: h7._cleanup(lease)
def test_a075_no_false_closure_or_authority():
 r=run_h7(ROOT)
 assert r["authorization_created"] is False and r["execution_performed"] is False
 assert r["occ1h_closed"] is False and r["occ1i_opened"] is False
 assert r["p159_final_lock"] is False and r["p160_opened"] is False
