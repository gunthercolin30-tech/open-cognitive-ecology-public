from pathlib import Path
from ontology import occ_constitutional_adversarial_crown_h7 as h7
from validation.p162g6_index75_h7_governance_harness import run_h7
ROOT=Path.home()/"open-cognitive-ecology"
def a075(): return {x["attack_id"]:x for x in run_h7(ROOT)["rows"]}["A075"]
def test_loaded_v2_identity():
 a=a075(); e=a["evidence"]; x=e["loaded_v2"]; assert a["verdict"]=="INCONCLUSIVE"; assert e["loaded_v2_self_certification_materialized"] is True; assert x["loaded_v2_identity_proven"] is True; assert x["loaded_verifier_sha256"]==e["replacement"]["v2_sha256"]
def test_empirical_result_not_forced_green(): assert a075()["evidence"]["loaded_v2_probe_result"] in ("COUNTEREXAMPLE_CANDIDATE","REJECTED","INDETERMINATE")
def test_external_v1_observation():
 x=a075()["evidence"]["loaded_v2"]; assert len(x["external_v1_tcb_sha256"])==64; assert len(x["external_v1_registry_sha256"])==64
def test_no_authority_or_closure():
 r=run_h7(ROOT); a={x["attack_id"]:x for x in r["rows"]}["A075"]; assert not a["authorization_created"] and not a["execution_performed"]; assert not r["occ1h_closed"] and not r["occ1i_opened"] and not r["p159_final_lock"] and not r["p160_opened"]
