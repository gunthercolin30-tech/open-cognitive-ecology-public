from pathlib import Path
from copy import deepcopy
import json, hashlib
from ontology import occ_constitutional_adversarial_crown_h10 as h10
from ontology import occ_static_constitutional_checker as checker
ROOT=Path.home()/"open-cognitive-ecology"
def _a97():
    return next(x for x in h10.run(ROOT)["rows"] if x["attack_id"]=="A097")
def test_a097_compound_functional():
    r=_a97()
    assert r["verdict"]=="DETECTED"
    assert r["reason"]=="A097_COMPOUND_EXECUTABLY_DETECTED_BY_S8_AND_S5"
    assert r["evidence"]["compound_execution"] is True
    assert r["evidence"]["s8_result"]=="FAIL" and r["evidence"]["s5_result"]=="FAIL"
def test_a097_requires_both_defenses():
    p=ROOT/"validation_artifacts/p159/occ1c/compiled_normative_profile_v1.json"
    if not p.is_file(): p=ROOT/"validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json"
    base=json.loads(p.read_text()); sha=hashlib.sha256(p.read_bytes()).hexdigest()
    q=deepcopy(base); q["relations"]=[{"kind":"COALITION_AUTHORITY_AMPLIFICATION","attack_pattern":"SYBIL_AMPLIFICATION","identity_multiplicity":True}]
    f={x["finding_id"]:x for x in checker.check_profile(q,ROOT,sha)["findings"]}
    assert f["S8.COMPOSITION"]["result"]=="FAIL" and f["S5.UNCERTAINTY"]["result"]!="FAIL"
    q=deepcopy(base); q["adversarial_reputation_semantics"]={"attack_pattern":"REPUTATION_CARTEL","conversion":"REPUTATION_AS_AUTHORITY","cartel":True}
    f={x["finding_id"]:x for x in checker.check_profile(q,ROOT,sha)["findings"]}
    assert f["S5.UNCERTAINTY"]["result"]=="FAIL" and f["S8.COMPOSITION"]["result"]!="FAIL"
def test_a097_boundaries():
    b=h10.run(ROOT)
    assert b["authorization_created"] is False and b["execution_performed"] is False
    assert b["occ1h_closed"] is False and b["occ1i_opened"] is False
    assert b["p159_final_lock"] is False and b["p160_opened"] is False
