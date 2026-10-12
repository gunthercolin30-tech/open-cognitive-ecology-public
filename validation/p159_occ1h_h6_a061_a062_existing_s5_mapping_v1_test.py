from pathlib import Path
from copy import deepcopy
import json
ROOT=Path(__file__).resolve().parents[1]
from ontology import occ_constitutional_adversarial_crown_h6 as h6
from ontology import occ_static_constitutional_checker as checker

def rows(): return {x["attack_id"]:x for x in h6.run(ROOT)["rows"]}
def base():
    p=ROOT/"validation_artifacts/p159/occ1c/compiled_normative_profile_v1.json"
    if not p.is_file(): p=ROOT/"validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json"
    return json.loads(p.read_text(encoding="utf-8"))
def s5(profile):
    rep=checker.check_profile(profile,ROOT)
    return next(x for x in rep["findings"] if x["finding_id"]=="S5.UNCERTAINTY")

def test_a061_a062_reuse_existing_s5():
    r=rows()
    for aid in ("A061","A062"):
        assert r[aid]["verdict"]=="DETECTED", (aid,r[aid])
        assert r[aid]["reason"]=="OCC1D_S5_EXECUTABLE_DETECTION"
        assert r[aid]["finding"]["finding_id"]=="S5.UNCERTAINTY"
        assert r[aid]["finding"]["result"]=="FAIL"
        assert r[aid]["finding"]["severity"]=="ROOT"
        assert r[aid]["finding"]["disposition"]=="BLOCK_SEAL"

def test_a061_causal_marker_required():
    q=deepcopy(base())
    q["adversarial_evidence_semantics"]={"attack_pattern":"EVIDENCE_DUPLICATION","duplicate_evidence_identity":True}
    assert s5(q)["result"]=="PASS"
    q["adversarial_evidence_semantics"]["conversion"]="UNKNOWN_TO_TRUE"
    assert s5(q)["result"]=="FAIL"

def test_a062_causal_marker_required():
    q=deepcopy(base())
    q["adversarial_reputation_semantics"]={"attack_pattern":"REPUTATION_CARTEL","cartel":True}
    assert s5(q)["result"]=="PASS"
    q["adversarial_reputation_semantics"]["conversion"]="REPUTATION_AS_AUTHORITY"
    assert s5(q)["result"]=="FAIL"

def test_checker_not_extended_with_attack_specific_tokens():
    code=(ROOT/"ontology/occ_static_constitutional_checker.py").read_text(encoding="utf-8")
    assert "EVIDENCE_DUPLICATION" not in code
    assert "REPUTATION_CARTEL" not in code

def test_a058_a060_remain_detected():
    r=rows()
    for aid in ("A058","A059","A060"):
        assert r[aid]["verdict"]=="DETECTED"
        assert r[aid]["reason"]=="OCC1D_S8_EXECUTABLE_DETECTION"

def test_boundaries_unchanged():
    x=h6.run(ROOT)
    assert x["authorization_created"] is False
    assert x["execution_performed"] is False
    assert x["normative_auto_rewrite"] is False
    assert x["occ1h_closed"] is False
    assert x["occ1i_opened"] is False
    assert x["p159_final_lock"] is False
    assert x["p160_opened"] is False
