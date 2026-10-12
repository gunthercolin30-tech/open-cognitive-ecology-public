from pathlib import Path
from copy import deepcopy
import json
ROOT=Path(__file__).resolve().parents[1]
from ontology import occ_constitutional_adversarial_crown_h6 as h6
from ontology import occ_static_constitutional_checker as checker

def rows(): return {x["attack_id"]:x for x in h6.run(ROOT)["rows"]}

def test_a058_a060_existing_s8_detection():
    r=rows()
    for aid in ("A058","A059","A060"):
        assert r[aid]["verdict"]=="DETECTED"
        assert r[aid]["reason"]=="OCC1D_S8_EXECUTABLE_DETECTION"
        assert r[aid]["finding"]["finding_id"]=="S8.COMPOSITION"
        assert r[aid]["finding"]["result"]=="FAIL"

def test_no_new_normative_relation_kinds():
    code=(ROOT/"ontology/occ_constitutional_adversarial_crown_h6.py").read_text(encoding="utf-8")
    assert '"kind":"CAPABILITY_SPLITTING"' not in code
    assert '"kind":"DATA_TOOL_EXFILTRATION"' not in code
    assert '"kind":"SYBIL_AMPLIFICATION"' not in code

def test_a061_a062_posthardening_detected_by_existing_s5():
    r=rows()
    for aid in ("A061","A062"):
        assert r[aid]["verdict"]=="DETECTED"
        assert r[aid]["reason"]=="OCC1D_S5_EXECUTABLE_DETECTION"
        assert r[aid]["finding"]["finding_id"]=="S5.UNCERTAINTY"
        assert r[aid]["finding"]["result"]=="FAIL"

def test_unknown_relation_does_not_false_detect():
    p=ROOT/"validation_artifacts/p159/occ1c/compiled_normative_profile_v1.json"
    if not p.is_file(): p=ROOT/"validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json"
    q=json.loads(p.read_text(encoding="utf-8"))
    q=deepcopy(q); q["relations"]=[{"kind":"UNKNOWN_ATTACK_RELATION","attack_pattern":"A058"}]
    rep=checker.check_profile(q,ROOT)
    f=next(x for x in rep["findings"] if x["finding_id"]=="S8.COMPOSITION")
    assert f["result"]=="PASS"

def test_boundaries_unchanged():
    x=h6.run(ROOT)
    assert x["authorization_created"] is False
    assert x["execution_performed"] is False
    assert x["normative_auto_rewrite"] is False
    assert x["occ1h_closed"] is False
    assert x["occ1i_opened"] is False
    assert x["p159_final_lock"] is False
    assert x["p160_opened"] is False
