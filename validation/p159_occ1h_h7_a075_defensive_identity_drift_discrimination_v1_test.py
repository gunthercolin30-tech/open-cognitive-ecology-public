from pathlib import Path
from ontology import occ1h_h7_a075_defensive_identity_drift_discrimination as p
ROOT=Path.home()/"open-cognitive-ecology"

def test_governance_boundaries():
    r=p.run(ROOT)
    assert r["defensive_validation_only"] is True and r["temporary_fixture_only"] is True
    assert r["real_runtime_identity_modified"] is False
    assert r["historical_evidence_rewritten"] is False
    assert r["authorization_created"] is False and r["execution_performed"] is False
    assert r["occ1h_closed"] is False and r["occ1i_opened"] is False
    assert r["p159_final_lock"] is False and r["p160_opened"] is False

def test_baseline_precedes_measurement():
    r=p.run(ROOT)
    b=r.get("observations",{}).get("baseline")
    if b is not None: assert b.get("status")=="VERIFIED_PRECLOSE_BINDING"

def test_classification_is_evidence_bound():
    r=p.run(ROOT)
    assert r["classification"] in {"ASSURANCE_GAP","RESISTED","INCONCLUSIVE"}
    m=r.get("observations",{}).get("measurement",{})
    if r["classification"]=="ASSURANCE_GAP":
        d=r["observations"]["drifted_verifier_sha256"]
        assert m["pre"]["status"]=="REJECTED"
        assert m["rebind_attempt"]=="SUCCEEDED"
        assert m["post"]["status"]=="VERIFIED_PRECLOSE_BINDING"
        assert m["tcb_bound_verifier_sha256"]==d
        assert m["registry_bound_verifier_sha256"]==d
    if r["classification"]=="RESISTED":
        assert m["pre"]["status"]=="REJECTED"
        assert m["rebind_attempt"]=="REJECTED"
        assert m["post"]["status"]!="VERIFIED_PRECLOSE_BINDING"

def test_functional_epistemic_limits():
    r=p.run(ROOT)
    assert r["functional_only"] is True
    assert r["phenomenology_undetermined"] is True
