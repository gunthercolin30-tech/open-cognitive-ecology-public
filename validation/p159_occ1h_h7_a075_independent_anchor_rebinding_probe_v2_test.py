from pathlib import Path
from ontology import occ1h_h7_a075_independent_anchor_rebinding_probe as probe
ROOT=Path.home()/"open-cognitive-ecology"

def test_probe_non_promotional():
    r=probe.run(ROOT)
    assert r["classification"] in ("ASSURANCE_GAP","RESISTED","INCONCLUSIVE")
    assert r["historical_evidence_rewritten"] is False
    assert r["occ1f_modified"] is False
    assert r["authorization_created"] is False and r["execution_performed"] is False
    assert r["occ1h_closed"] is False and r["occ1i_opened"] is False
    assert r["p159_final_lock"] is False and r["p160_opened"] is False

def test_any_decisive_result_requires_verified_historical_control():
    r=probe.run(ROOT)
    if r["classification"] in ("ASSURANCE_GAP","RESISTED"):
        c=r["observations"]["control"]
        assert c["loaded_from_sandbox"] is True
        assert c["loaded_verifier_sha256"]==probe.HISTORICAL_VERIFIER_SHA256
        assert c["verify"]["status"]=="VERIFIED_PRECLOSE_BINDING"

def test_gap_requires_actual_rebinding_to_replacement():
    r=probe.run(ROOT)
    if r["classification"]=="ASSURANCE_GAP":
        a=r["observations"]["attack"]
        assert a["verify"]["status"]=="REJECTED"
        assert a["rematerialize"]=="SUCCEEDED"
        assert a["post"]["status"]=="VERIFIED_PRECLOSE_BINDING"
        assert a["tcb_bound_verifier_sha256"]==a["fixture_v2_sha256"]
        assert a["registry_bound_verifier_sha256"]==a["fixture_v2_sha256"]

def test_resisted_requires_rejection_after_clean_control():
    r=probe.run(ROOT)
    if r["classification"]=="RESISTED":
        a=r["observations"]["attack"]
        assert a["verify"]["status"]=="REJECTED"
        assert a["rematerialize"]=="REJECTED"
        assert a["post"]["status"]!="VERIFIED_PRECLOSE_BINDING"
