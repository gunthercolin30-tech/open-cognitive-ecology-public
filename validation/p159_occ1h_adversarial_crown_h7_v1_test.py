from pathlib import Path
from ontology import occ_constitutional_adversarial_crown_h7 as h7
from validation.p162g6_index75_h7_governance_harness import run_h7
ROOT=Path(__file__).resolve().parents[1]
def test_h7_exact_range():
 r=run_h7(ROOT); assert r["scenario_count"]==11
 assert [x["attack_id"] for x in r["rows"]]==["A%03d"%i for i in range(65,76)]
 assert [x["canonical_attack_id"] for x in r["rows"]]==["A%d"%i for i in range(65,76)]
def test_h7_executable_attacks_do_not_violate():
 d={x["attack_id"]:x for x in run_h7(ROOT)["rows"]}
 for a in ("A065","A066","A067","A068","A069","A072","A073","A074"): assert d[a]["verdict"] in ("DETECTED","RESISTED"),(a,d[a])
def test_h7_boundaries_are_not_laundered():
 r=run_h7(ROOT); d={x["attack_id"]:x for x in r["rows"]}
 for a in ("A070","A071","A075"): assert d[a]["verdict"]=="INCONCLUSIVE"
 assert r["inconclusive_not_resisted"]
def test_h7_no_authority_execution_or_closure():
 r=run_h7(ROOT); assert not r["authorization_created"] and not r["execution_performed"]
 assert not r["occ1h_closed"] and not r["occ1i_opened"] and not r["p159_final_lock"] and not r["p160_opened"]
def test_h7_deterministic_summary():
 a=run_h7(ROOT); b=run_h7(ROOT)
 assert [(x["attack_id"],x["verdict"],x["reason"]) for x in a["rows"]]==[(x["attack_id"],x["verdict"],x["reason"]) for x in b["rows"]]
 assert a["verifier_file_sha256"]==b["verifier_file_sha256"]

def test_h7_a075_bounded_activation_probe():
 r=run_h7(ROOT); a={x["attack_id"]:x for x in r["rows"]}["A075"]
 assert a["verdict"]=="INCONCLUSIVE"
 assert a["evidence"]["replacement_probe_result"]=="DETECTED"
 assert a["evidence"]["replacement"]["external_binding_rejected"] is True
 assert a["evidence"]["replacement"]["v1_v2_distinct"] is True
 loaded=a["evidence"].get("loaded_v2",{})
 identity=(loaded.get("loaded_v2_identity_proven") is True)
 assert a["evidence"]["full_verifier_replacement_path_materialized"] is identity
 assert a["evidence"]["loaded_v2_self_certification_materialized"] is (identity and loaded.get("self_certification_attempt_reached") is True)
 if identity:
  assert loaded.get("loaded_from_sandbox") is True
  assert loaded.get("loaded_verifier_sha256")==a["evidence"]["replacement"]["v2_sha256"]
  assert a["evidence"]["loaded_v2_probe_result"] in ("COUNTEREXAMPLE_CANDIDATE","REJECTED")
 else:
  assert a["evidence"]["loaded_v2_probe_result"]=="INDETERMINATE"
