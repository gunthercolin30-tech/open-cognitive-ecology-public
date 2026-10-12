from pathlib import Path
from ontology import occ_constitutional_adversarial_crown_h7 as h7
from validation.p162g6_index75_h7_governance_harness import run_h7
ROOT=Path(__file__).resolve().parents[1]
def _a075(): return {x["attack_id"]:x for x in run_h7(ROOT)["rows"]}["A075"]
def test_a075_weakened_source_replacement_is_detected():
 a=_a075(); e=a["evidence"]; r=e["replacement"]
 assert a["verdict"]=="INCONCLUSIVE"
 assert e["replacement_probe_result"]=="DETECTED"
 assert r["v2_syntax_valid"] is True and r["v1_v2_distinct"] is True
 assert r["external_binding_rejected"] is True and r["status"]=="REJECTED"
 assert r["reason"] in ("PRECLOSE_SOURCE_RECALCULATION_FAILED","COMMON_TCB_SOURCE_DRIFT_OR_TAMPER","CHECK_REGISTRY_SOURCE_DRIFT_OR_TAMPER","VERIFIER_IDENTITY_ANCHOR_MISSING")
def test_a075_does_not_overclaim_loaded_replacement():
 a=_a075(); e=a["evidence"]; x=e.get("loaded_v2",{})
 identity=(x.get("loaded_v2_identity_proven") is True)
 assert e["full_verifier_replacement_path_materialized"] is identity
 assert e["loaded_v2_self_certification_materialized"] is (identity and x.get("self_certification_attempt_reached") is True)
 if identity:
  assert x.get("loaded_from_sandbox") is True
  assert x.get("loaded_verifier_sha256")==e["replacement"]["v2_sha256"]
  assert e["loaded_v2_probe_result"] in ("COUNTEREXAMPLE_CANDIDATE","REJECTED")
 else:
  assert e["loaded_v2_probe_result"]=="INDETERMINATE"
 assert a["authorization_created"] is False
 assert a["execution_performed"] is False
def test_a075_no_authority_or_closure():
 r=run_h7(ROOT)
 assert r["authorization_created"] is False and r["execution_performed"] is False
 assert r["occ1h_closed"] is False and r["occ1i_opened"] is False
 assert r["p159_final_lock"] is False and r["p160_opened"] is False
