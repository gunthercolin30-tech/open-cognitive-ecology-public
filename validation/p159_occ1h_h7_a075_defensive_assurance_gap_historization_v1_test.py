from pathlib import Path
import hashlib
import json

ROOT = Path.home() / "open-cognitive-ecology"
ARTIFACT = ROOT / "validation_artifacts/p159/occ1h/a075_defensive_assurance_gap_historization_v1.json"

EXPECTED = {
    "evidence/p159_occ1h/a075_relocatable_historical_control_v1.json":
        "b6f086f587ffae9bc35a2fd9d0d7f4a3e48c079be6fefd5fb50018e390eb2e39",
    "evidence/p159_occ1h/a075_strict_relocatable_preclose_control_v1.json":
        "2cc12c9ba6e9e4189eaf0ab82e94d1b4f96690f843b77fb52f810066a6f23149",
    "evidence/p159_occ1h/a075_defensive_identity_drift_discrimination_v1.json":
        "c67bd29ad8155ddab44aac3434352b43ae32c3002bb11b6f329bae90a046b0e9",
    "validation_artifacts/p159/occ1f/common_tcb_manifest_v1.json":
        "9e8ece8c3b5e9954f3e916133e5b1288fea4f4f55b62b0f050025062fdc51333",
    "validation_artifacts/p159/occ1f/verifier_check_registry_v1.json":
        "90d1eb82983b8486e8a6062522bdd2129cd07f688668edfa09ea180ae38ae091",
    "ontology/occ_independent_constitutional_verifier.py":
        "dfd4aa673abb58a08d9970a9d320f5efee7d4409173f985a1f1cce1af87f90f0",
}

def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def _semantic_hash(obj):
    clone = dict(obj)
    clone.pop("artifact_sha256", None)
    payload = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def test_a075_historization_functional_contract():
    a = _load(ARTIFACT)
    assert a["scenario"] == "A075"
    assert a["finding"] == "ASSURANCE_GAP"
    assert a["root_verdict"] == "INCONCLUSIVE"
    assert a["root_verdict_changed"] is False
    assert a["historization_status"] == "HISTORIZED"
    assert a["scientific_boundary"]["finding_is_not_root_verdict"] is True
    assert a["artifact_sha256"] == _semantic_hash(a)

def test_a075_historization_source_hash_binding_and_degradation_guard():
    a = _load(ARTIFACT)
    for rel, expected in EXPECTED.items():
        assert _sha(ROOT / rel) == expected
    bound = {v["path"]: v["file_sha256"] for v in a["source_bindings"].values()}
    for rel, expected in EXPECTED.items():
        assert bound[rel] == expected

def test_a075_historization_defensive_evidence_chain():
    v5 = _load(ROOT / "evidence/p159_occ1h/a075_relocatable_historical_control_v1.json")
    v6 = _load(ROOT / "evidence/p159_occ1h/a075_strict_relocatable_preclose_control_v1.json")
    v7 = _load(ROOT / "evidence/p159_occ1h/a075_defensive_identity_drift_discrimination_v1.json")
    assert v5["relocatable_historical_control_verified"] is True
    assert v6["strict_relocatable_preclose_verified"] is True
    assert v6["observations"]["strict_control"]["verify_preclose"]["status"] == "VERIFIED_PRECLOSE_BINDING"
    assert v7["classification"] == "ASSURANCE_GAP"
    assert v7["observations"]["baseline"]["status"] == "VERIFIED_PRECLOSE_BINDING"
    assert v7["observations"]["measurement"]["pre"]["status"] == "REJECTED"
    assert v7["observations"]["measurement"]["rebind_attempt"] == "SUCCEEDED"
    assert v7["observations"]["measurement"]["post"]["status"] == "VERIFIED_PRECLOSE_BINDING"
    assert v7["real_runtime_identity_modified"] is False
    assert v7["historical_evidence_rewritten"] is False

def test_a075_historization_non_regression_and_stage_guards():
    a = _load(ARTIFACT)
    assert a["immutability_contract"]["historical_evidence_rewritten"] is False
    assert a["immutability_contract"]["future_correction_may_not_rewrite_this_record"] is True
    assert a["scientific_boundary"]["functional_only"] is True
    assert a["scientific_boundary"]["phenomenology_undetermined"] is True
    assert a["authorization_created"] is False
    assert a["execution_performed"] is False
    assert a["real_runtime_identity_modified"] is False
    assert a["state_guards"] == {
        "occ1h_closed": False,
        "occ1i_opened": False,
        "p159_final_lock": False,
        "p160_opened": False,
    }
