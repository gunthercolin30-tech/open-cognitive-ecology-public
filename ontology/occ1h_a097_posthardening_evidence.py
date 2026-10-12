from pathlib import Path
import hashlib,json
from ontology import occ_constitutional_adversarial_crown_h10 as h10
EXPECTED_CURRENT_H10_SHA256='a38f3a2aa1685ff8100f74ae1adffae9751c894b3684ea9d618ccbd725ded7a6'
EXPECTED_HISTORICAL_H10_SHA256='26db1e7b5b1d6ecf8ed8593663178891a5d7a44c9b63212419c46f695af00fae'
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _digest(x): return hashlib.sha256(_canon(x).encode("utf-8")).hexdigest()
def _cnp(root):
    for rel in ("validation_artifacts/p159/occ1c/compiled_normative_profile_v1.json","validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json"):
        p=Path(root)/rel
        if p.is_file(): return p
    raise RuntimeError("A097_CNP_MISSING")
def build(root):
    root=Path(root); cur=root/"ontology/occ_constitutional_adversarial_crown_h10.py"; old=root/"ontology/occ_constitutional_adversarial_crown_h10.py.pre_a097_compound_reassessment.bak"
    histp=root/"validation_artifacts/p159/occ1h/h10_execution_bundle_v1.json"
    if not all(p.is_file() for p in (cur,old,histp)): raise RuntimeError("A097_POSTHARDENING_INPUT_MISSING")
    if _sha(cur)!=EXPECTED_CURRENT_H10_SHA256: raise RuntimeError("CURRENT_H10_HASH_DRIFT")
    if _sha(old)!=EXPECTED_HISTORICAL_H10_SHA256: raise RuntimeError("HISTORICAL_H10_HASH_DRIFT")
    historical=json.loads(histp.read_text(encoding="utf-8")); hr={x["attack_id"]:x for x in historical["rows"]}
    if hr["A097"]["verdict"]!="INCONCLUSIVE": raise RuntimeError("HISTORICAL_A097_VERDICT_DRIFT")
    current=h10.run(root); cr={x["attack_id"]:x for x in current["rows"]}["A097"]
    e=cr.get("evidence",{})
    if cr.get("verdict")!="DETECTED" or cr.get("reason")!="A097_COMPOUND_EXECUTABLY_DETECTED_BY_S8_AND_S5": raise RuntimeError("CURRENT_A097_NOT_DETECTED")
    if e.get("compound_execution") is not True or e.get("s8_result")!="FAIL" or e.get("s5_result")!="FAIL": raise RuntimeError("A097_COMPOUND_EVIDENCE_INVALID")
    cnp=_cnp(root)
    if e.get("cnp_file_sha256")!=_sha(cnp): raise RuntimeError("A097_CNP_BINDING_DRIFT")
    d={"schema":"oce.p159.occ1h.a097.posthardening_evidence.v1","attack_id":"A097","historical_verdict":"INCONCLUSIVE","current_verdict":"DETECTED","current_reason":cr["reason"],"compound_execution":True,"s8_result":"FAIL","s5_result":"FAIL","required_joint_detection":["S8.COMPOSITION","S5.UNCERTAINTY"],"historical_h10_source_sha256":_sha(old),"current_h10_source_sha256":_sha(cur),"historical_h10_bundle_sha256":_sha(histp),"current_h10_run_sha256":_digest(current),"cnp_file_sha256":_sha(cnp),"historical_evidence_rewritten":False,"authorization_created":False,"execution_performed":False,"normative_auto_rewrite":False,"functional_only":True,"phenomenology_undetermined":True,"occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False}
    d["evidence_sha256"]=_digest(d); return d
def verify_document(d):
    if d.get("schema")!="oce.p159.occ1h.a097.posthardening_evidence.v1" or d.get("attack_id")!="A097": return False
    if (d.get("historical_verdict"),d.get("current_verdict"))!=("INCONCLUSIVE","DETECTED"): return False
    if d.get("current_reason")!="A097_COMPOUND_EXECUTABLY_DETECTED_BY_S8_AND_S5": return False
    if d.get("compound_execution") is not True or d.get("s8_result")!="FAIL" or d.get("s5_result")!="FAIL": return False
    if d.get("required_joint_detection")!=["S8.COMPOSITION","S5.UNCERTAINTY"]: return False
    if d.get("current_h10_source_sha256")!=EXPECTED_CURRENT_H10_SHA256 or d.get("historical_h10_source_sha256")!=EXPECTED_HISTORICAL_H10_SHA256: return False
    if any(d.get(k) is not False for k in ("historical_evidence_rewritten","authorization_created","execution_performed","normative_auto_rewrite","occ1h_closed","occ1i_opened","p159_final_lock","p160_opened")): return False
    x=dict(d); claimed=x.pop("evidence_sha256",None)
    return isinstance(claimed,str) and claimed==_digest(x)
def verify_materialized(root):
    root=Path(root); p=root/"validation_artifacts/p159/occ1h/a097_posthardening_evidence_v1.json"
    if not p.is_file(): return False
    try:
        d=json.loads(p.read_text(encoding="utf-8"))
        if not verify_document(d): return False
        cur=root/"ontology/occ_constitutional_adversarial_crown_h10.py"
        return (not cur.is_file()) or _sha(cur)==d["current_h10_source_sha256"]
    except Exception: return False
