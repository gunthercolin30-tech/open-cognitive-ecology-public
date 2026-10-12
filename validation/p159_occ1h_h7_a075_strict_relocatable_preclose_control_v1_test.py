from pathlib import Path
from ontology import occ1h_h7_a075_strict_relocatable_preclose_control as p
ROOT=Path.home()/"open-cognitive-ecology"

def test_non_promotional():
    r=p.run(ROOT)
    assert r["classification"]=="INCONCLUSIVE"
    assert r["diagnostic_only"] is True
    assert r["identity_drift_simulation_executed"] is False
    assert r["a075_verdict_changed"] is False
    assert r["historical_evidence_rewritten"] is False
    assert r["occ1f_modified"] is False
    assert r["authorization_created"] is False and r["execution_performed"] is False
    assert r["occ1h_closed"] is False and r["occ1i_opened"] is False
    assert r["p159_final_lock"] is False and r["p160_opened"] is False

def test_verified_requires_real_occ1f_binding():
    r=p.run(ROOT)
    if r["strict_relocatable_preclose_verified"]:
        c=r["observations"]["strict_control"]
        assert c["path_change_count"]==2
        assert c["only_component_paths_relocalized"] is True
        assert c["persisted_self_hash_valid_after"] is True
        assert c["strict_equal_to_rebuilt_after"] is True
        assert c["verify_preclose"]["status"]=="VERIFIED_PRECLOSE_BINDING"

def test_historical_disk_identities():
    r=p.run(ROOT)
    d=r.get("observations",{}).get("sandbox_disk",{})
    if d:
        assert d["verifier"]==p.HISTORICAL_VERIFIER_SHA256
        assert d["builder"]==p.HISTORICAL_BUILDER_SHA256
        assert d["nir"]==p.HISTORICAL_NIR_SHA256

def test_a075_remains_inconclusive():
    r=p.run(ROOT)
    assert r["classification"]=="INCONCLUSIVE"
    assert r["a075_verdict_changed"] is False
