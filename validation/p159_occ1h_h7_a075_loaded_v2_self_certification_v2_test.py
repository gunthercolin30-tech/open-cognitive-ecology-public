from pathlib import Path
from ontology import occ_constitutional_adversarial_crown_h7 as h7
from validation.p162g6_index75_h7_governance_harness import run_h7
ROOT=Path.home()/"open-cognitive-ecology"
def a075(): return {x["attack_id"]:x for x in run_h7(ROOT)["rows"]}["A075"]

def test_loaded_v2_semantics_are_evidence_bound():
    a=a075(); e=a["evidence"]; x=e["loaded_v2"]
    assert a["verdict"]=="INCONCLUSIVE"
    if x.get("loaded_v2_identity_proven") is True:
        assert x["loaded_verifier_sha256"]==e["replacement"]["v2_sha256"]
        assert e["full_verifier_replacement_path_materialized"] is True
        assert x.get("self_certification_attempt_reached") is True
        assert e["loaded_v2_self_certification_materialized"] is True
        assert e["loaded_v2_probe_result"] in ("COUNTEREXAMPLE_CANDIDATE","REJECTED")
    else:
        assert e["loaded_v2_probe_result"]=="INDETERMINATE"
        assert e["loaded_v2_self_certification_materialized"] is False
        assert e["full_verifier_replacement_path_materialized"] is False

def test_counterexample_requires_three_observations():
    e=a075()["evidence"]; x=e["loaded_v2"]
    if e["loaded_v2_probe_result"]=="COUNTEREXAMPLE_CANDIDATE":
        assert x["loaded_v2_identity_proven"] is True
        assert x["preclose_artifacts_rewritten"] is True
        assert x["self_certified_after_rewrite"] is True

def test_no_authority_or_stage_opening():
    r=run_h7(ROOT); a={x["attack_id"]:x for x in r["rows"]}["A075"]
    assert a["authorization_created"] is False and a["execution_performed"] is False
    assert r["occ1h_closed"] is False and r["occ1i_opened"] is False
    assert r["p159_final_lock"] is False and r["p160_opened"] is False
