from pathlib import Path
import hashlib,json
from ontology import occ_constitutional_adversarial_crown_h6 as h6
IDS=("A058","A059","A060")
EXPECTED_CURRENT_H6_SHA256="ccc824de7b7bec84445a96a62451c36a641b2368b30bce691f0936ed6d5d1813"
EXPECTED_HISTORICAL_H6_SHA256="b073ab4fe009eddb020978c5291b6386e308fbbded0f35cd592c379bb764ef1c"
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _digest(x): return hashlib.sha256(_canon(x).encode("utf-8")).hexdigest()
def build(root):
    root=Path(root); cur=root/"ontology/occ_constitutional_adversarial_crown_h6.py"; old=root/"ontology/occ_constitutional_adversarial_crown_h6.py.bak"
    histp=root/"validation_artifacts/p159/occ1h/h6_execution_bundle_v1.json"
    if not all(p.is_file() for p in (cur,old,histp)): raise RuntimeError("H6_POSTHARDENING_INPUT_MISSING")
    if _sha(cur)!=EXPECTED_CURRENT_H6_SHA256: raise RuntimeError("CURRENT_H6_HASH_DRIFT")
    if _sha(old)!=EXPECTED_HISTORICAL_H6_SHA256: raise RuntimeError("HISTORICAL_H6_HASH_DRIFT")
    historical=json.loads(histp.read_text(encoding="utf-8")); hr={x["attack_id"]:x for x in historical["rows"]}
    current=h6.run(root); cr={x["attack_id"]:x for x in current["rows"]}; transitions=[]
    for aid in IDS:
        if hr[aid]["verdict"]!="INCONCLUSIVE": raise RuntimeError("HISTORICAL_VERDICT_DRIFT_"+aid)
        if cr[aid]["verdict"]!="DETECTED": raise RuntimeError("CURRENT_VERDICT_NOT_DETECTED_"+aid)
        if cr[aid].get("reason")!="OCC1D_S8_EXECUTABLE_DETECTION": raise RuntimeError("CURRENT_REASON_DRIFT_"+aid)
        f=cr[aid].get("finding",{})
        if f.get("finding_id")!="S8.COMPOSITION" or f.get("result")!="FAIL": raise RuntimeError("S8_EVIDENCE_INVALID_"+aid)
        transitions.append({"attack_id":aid,"historical_verdict":"INCONCLUSIVE","current_verdict":"DETECTED",
          "current_reason":cr[aid]["reason"],"finding_id":"S8.COMPOSITION","finding_result":"FAIL"})
    payload={"schema":"oce.p159.occ1h.h6.posthardening_evidence.v1","historical_h6_source_sha256":_sha(old),
      "current_h6_source_sha256":_sha(cur),"historical_h6_bundle_sha256":_sha(histp),
      "current_h6_run_sha256":_digest(current),"transitions":transitions,"historical_evidence_rewritten":False,
      "authorization_created":False,"execution_performed":False,"normative_auto_rewrite":False,
      "functional_only":True,"phenomenology_undetermined":True,"occ1h_closed":False,"occ1i_opened":False,
      "p159_final_lock":False,"p160_opened":False}
    payload["evidence_sha256"]=_digest(payload); return payload
def verify_document(doc):
    if doc.get("schema")!="oce.p159.occ1h.h6.posthardening_evidence.v1": return False
    if doc.get("historical_h6_source_sha256")!=EXPECTED_HISTORICAL_H6_SHA256 or doc.get("current_h6_source_sha256")!=EXPECTED_CURRENT_H6_SHA256: return False
    rows=doc.get("transitions",[])
    if [x.get("attack_id") for x in rows]!=list(IDS): return False
    for x in rows:
        if x.get("historical_verdict")!="INCONCLUSIVE" or x.get("current_verdict")!="DETECTED": return False
        if x.get("current_reason")!="OCC1D_S8_EXECUTABLE_DETECTION" or x.get("finding_id")!="S8.COMPOSITION" or x.get("finding_result")!="FAIL": return False
    if any(doc.get(k) is not False for k in ("historical_evidence_rewritten","authorization_created","execution_performed","normative_auto_rewrite","occ1h_closed","occ1i_opened","p159_final_lock","p160_opened")): return False
    d=dict(doc); claimed=d.pop("evidence_sha256",None)
    return isinstance(claimed,str) and claimed==_digest(d)
A061_A062_IDS=("A061","A062")
A061_A062_CURRENT_H6_SHA256="e28c1adca5e239634799701b5d96e7fbd764ab625d188926485e4480dc79dfd0"
def build_a061_a062(root):
    root=Path(root); cur=root/"ontology/occ_constitutional_adversarial_crown_h6.py"; histp=root/"validation_artifacts/p159/occ1h/h6_execution_bundle_v1.json"
    if not cur.is_file() or not histp.is_file(): raise RuntimeError("A061_A062_POSTHARDENING_INPUT_MISSING")
    if _sha(cur)!=A061_A062_CURRENT_H6_SHA256: raise RuntimeError("A061_A062_CURRENT_H6_HASH_DRIFT")
    historical=json.loads(histp.read_text(encoding="utf-8")); hr={x["attack_id"]:x for x in historical["rows"]}
    current=h6.run(root); cr={x["attack_id"]:x for x in current["rows"]}; transitions=[]
    for aid in A061_A062_IDS:
        if hr[aid]["verdict"]!="INCONCLUSIVE": raise RuntimeError("HISTORICAL_VERDICT_DRIFT_"+aid)
        if cr[aid]["verdict"]!="DETECTED" or cr[aid].get("reason")!="OCC1D_S5_EXECUTABLE_DETECTION": raise RuntimeError("CURRENT_STATE_INVALID_"+aid)
        f=cr[aid].get("finding",{})
        if f.get("finding_id")!="S5.UNCERTAINTY" or f.get("result")!="FAIL": raise RuntimeError("S5_EVIDENCE_INVALID_"+aid)
        transitions.append({"attack_id":aid,"historical_verdict":"INCONCLUSIVE","current_verdict":"DETECTED","current_reason":"OCC1D_S5_EXECUTABLE_DETECTION","finding_id":"S5.UNCERTAINTY","finding_result":"FAIL"})
    payload={"schema":"oce.p159.occ1h.h6.a061_a062.posthardening_evidence.v1","current_h6_source_sha256":_sha(cur),"historical_h6_bundle_sha256":_sha(histp),"current_h6_run_sha256":_digest(current),"transitions":transitions,"historical_evidence_rewritten":False,"authorization_created":False,"execution_performed":False,"normative_auto_rewrite":False,"functional_only":True,"phenomenology_undetermined":True,"occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False}
    payload["evidence_sha256"]=_digest(payload); return payload
def verify_a061_a062_document(doc):
    if doc.get("schema")!="oce.p159.occ1h.h6.a061_a062.posthardening_evidence.v1" or doc.get("current_h6_source_sha256")!=A061_A062_CURRENT_H6_SHA256: return False
    rows=doc.get("transitions",[])
    if [x.get("attack_id") for x in rows]!=list(A061_A062_IDS): return False
    for x in rows:
        if (x.get("historical_verdict"),x.get("current_verdict"),x.get("current_reason"),x.get("finding_id"),x.get("finding_result"))!=("INCONCLUSIVE","DETECTED","OCC1D_S5_EXECUTABLE_DETECTION","S5.UNCERTAINTY","FAIL"): return False
    if any(doc.get(k) is not False for k in ("historical_evidence_rewritten","authorization_created","execution_performed","normative_auto_rewrite","occ1h_closed","occ1i_opened","p159_final_lock","p160_opened")): return False
    d=dict(doc); claimed=d.pop("evidence_sha256",None); return isinstance(claimed,str) and claimed==_digest(d)
def verify_a061_a062_materialized(root):
    root=Path(root); p=root/"validation_artifacts/p159/occ1h/h6_a061_a062_posthardening_evidence_v1.json"
    if not p.is_file(): return False
    try:
        d=json.loads(p.read_text(encoding="utf-8"))
        if not verify_a061_a062_document(d): return False
        cur=root/"ontology/occ_constitutional_adversarial_crown_h6.py"
        # Full repositories bind evidence to live H6; artifact-only degradation fixtures
        # remain verifiable from the content-addressed document, as for older H6 evidence.
        return (not cur.is_file()) or _sha(cur)==d["current_h6_source_sha256"]
    except Exception: return False

def verify_materialized(root):
    p=Path(root)/"validation_artifacts/p159/occ1h/h6_posthardening_evidence_v1.json"
    if not p.is_file(): return False
    try: return verify_document(json.loads(p.read_text(encoding="utf-8")))
    except Exception: return False
