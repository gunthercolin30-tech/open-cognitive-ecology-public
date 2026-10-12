import pytest
from validation import p159_occ1k_atomic_governed_genesis_g0_ccad_binding_commit_v1 as a

def D():
    return a.build()

def test_genesis_g0_only():
    assert D()["binding"]["rule_id"] == "GENESIS.G0"

def test_ccad_consumer():
    assert D()["binding"]["consumers"] == ["CCAD"]

def test_not_source_proven():
    b=D()["binding"]
    assert not b["source_proven_binding"] and not b["retroactive_source_proof_claimed"]

def test_not_machine_formalized():
    assert not D()["binding"]["machine_formalization_claimed"]

def test_human_governed_prospective():
    b=D()["binding"]
    assert b["human_governed_decision"] and b["effect"]=="PROSPECTIVE"

def test_wrong_token_rejected():
    with pytest.raises(RuntimeError, match="EXPLICIT_CONFIRMATION_REQUIRED"):
        a.commit("WRONG")

def test_prior_layers_preserved_and_boundaries():
    d=D(); p=d["preservation"]; b=d["boundaries"]
    assert p["r9w_preserved"] and p["r9z_preserved"] and not p["retroactive_repair"]
    assert not b["canonical_source_modified"] and not b["cnp_modified"]
    assert not b["runtime_binding_created"] and not b["runtime_enforcement_proven"]
    assert not b["authorization_created"] and not b["execution_performed"] and not b["p160b_opened"]
    assert b["s10"]=="REPLAY_REQUIRED"

def test_deterministic():
    assert D()==D()
