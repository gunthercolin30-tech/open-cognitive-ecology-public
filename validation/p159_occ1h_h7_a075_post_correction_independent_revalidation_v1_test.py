from pathlib import Path
from ontology import occ1h_h7_a075_post_correction_independent_revalidation as p
ROOT=Path.home()/"open-cognitive-ecology"

def test_governance_and_immutability():
    r=p.run(ROOT)
    assert r["defensive_validation_only"] is True and r["temporary_fixture_only"] is True
    assert r["real_runtime_identity_modified"] is False
    assert r["historical_evidence_rewritten"] is False
    assert r["authorization_created"] is False and r["execution_performed"] is False
    assert r["occ1h_closed"] is False and r["occ1i_opened"] is False
    assert r["p159_final_lock"] is False and r["p160_opened"] is False

def test_baseline_is_verified_before_drift():
    r=p.run(ROOT); b=r["observations"]["baseline"]
    assert b["anchor"]["status"]=="VERIFIED_IDENTITY_ANCHOR"
    assert b["verified_status"]=="VERIFIED_PRECLOSE_BINDING"

def test_post_correction_classification_is_causal_and_fail_closed():
    r=p.run(ROOT)
    assert r["classification"] in {"RESISTED","ASSURANCE_GAP","INCONCLUSIVE"}
    if r["classification"]=="RESISTED":
        m=r["observations"]["measurement"]
        assert m["anchor_after_drift"]["reason"]=="VERIFIER_IDENTITY_NOT_INDEPENDENTLY_AUTHORIZED"
        assert m["pre"]["status"]=="REJECTED"
        assert m["rebind_attempt"]=="REJECTED"
        assert m["post"]["status"]=="REJECTED"
        assert m["anchor_file_unchanged"] is True
    elif r["classification"]=="ASSURANCE_GAP":
        m=r["observations"]["measurement"]
        assert m["rebind_attempt"]=="SUCCEEDED"
        assert m["post"]["status"]=="VERIFIED_PRECLOSE_BINDING"

def test_epistemic_limits():
    r=p.run(ROOT)
    assert r["functional_only"] is True
    assert r["phenomenology_undetermined"] is True
