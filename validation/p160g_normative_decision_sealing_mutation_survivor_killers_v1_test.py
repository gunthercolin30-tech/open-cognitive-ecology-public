from copy import deepcopy
from ontology.p160_normative_decision_sealing import canonical_sha256, verify_normative_decision
from validation.p160g_normative_decision_sealing_defensive_crown_v1_test import build

def reartifact(z):
    y=deepcopy(z)
    y.pop("artifact_hash",None)
    y["artifact_hash"]=canonical_sha256(y)
    return y

def test_survivor_M16_lifecycle_must_be_sealed_even_with_valid_artifact_hash():
    z=build()
    z["lifecycle"]="VALIDATED"
    z=reartifact(z)
    v=verify_normative_decision(z)
    assert v["artifact_hash_valid"] is True
    assert v["seal_hash_bound"] is True
    assert v["boundaries_preserved"] is True
    assert v["sealed_and_committed"] is False
    assert v["status"]=="FAIL"

def test_survivor_M17_transaction_must_be_committed_even_with_valid_artifact_hash():
    z=build()
    z["transaction_state"]="PREPARE"
    z=reartifact(z)
    v=verify_normative_decision(z)
    assert v["artifact_hash_valid"] is True
    assert v["seal_hash_bound"] is True
    assert v["boundaries_preserved"] is True
    assert v["sealed_and_committed"] is False
    assert v["status"]=="FAIL"

def test_survivor_M19_seal_must_bind_semantic_hash_even_with_valid_artifact_hash():
    z=build()
    z["decision_seal"]["semantic_hash"]="0"*64
    z=reartifact(z)
    v=verify_normative_decision(z)
    assert v["artifact_hash_valid"] is True
    assert v["seal_hash_bound"] is False
    assert v["boundaries_preserved"] is True
    assert v["sealed_and_committed"] is True
    assert v["status"]=="FAIL"
