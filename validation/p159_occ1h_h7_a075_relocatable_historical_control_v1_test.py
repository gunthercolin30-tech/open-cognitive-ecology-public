from pathlib import Path
from ontology import occ1h_h7_a075_relocatable_historical_control as p
ROOT=Path.home()/"open-cognitive-ecology"
def test_non_promotional():
    r=p.run(ROOT)
    assert r["classification"]=="INCONCLUSIVE" and r["diagnostic_only"] is True
    assert r["attack_phase_executed"] is False and r["a075_verdict_changed"] is False
    assert r["historical_evidence_rewritten"] is False and r["occ1f_modified"] is False
    assert r["authorization_created"] is False and r["execution_performed"] is False
    assert r["occ1h_closed"] is False and r["occ1i_opened"] is False and r["p159_final_lock"] is False and r["p160_opened"] is False
def test_verified_control_requires_only_path_differences():
    r=p.run(ROOT)
    if r["relocatable_historical_control_verified"]:
        c=r["observations"]["comparison"]
        assert c["persisted_self_hash_valid"] is True
        assert c["persisted_verifier_identity"]==c["rebuilt_verifier_identity"]
        assert c["component_ids_match"] is True
        assert c["component_nonpath_differences"]==[]
        assert c["normalized_top_level_differences"]==[]
        assert c["normalized_persisted_hash"]==c["normalized_rebuilt_hash"]
        assert c["strict_equal"] is False and len(c["path_differences"])>0
def test_historical_disk_identities():
    r=p.run(ROOT)
    d=r.get("observations",{}).get("sandbox_disk",{})
    if d:
        assert d["verifier"]==p.HISTORICAL_VERIFIER_SHA256
        assert d["builder"]==p.HISTORICAL_BUILDER_SHA256
        assert d["nir"]==p.HISTORICAL_NIR_SHA256
def test_no_decisive_a075_verdict():
    r=p.run(ROOT)
    assert r["classification"]=="INCONCLUSIVE"
    assert r["reason"] not in ("RESISTED","ASSURANCE_GAP","DETECTED")
