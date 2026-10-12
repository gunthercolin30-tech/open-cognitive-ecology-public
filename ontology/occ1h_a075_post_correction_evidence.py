from pathlib import Path
import hashlib,json
SCHEMA="oce.p159.occ1h.a075.post_correction_evidence.v1"
EXPECTED_PROBE_SHA256="b0685f3a25d8febab76a427d8c342ef0a2bf4355f296c09b16148d95ce76f23b"
EXPECTED_H7_SHA256="4ff4abf8af70c3f350e8574f6dad556536506c614928809b819fc8596925dbbc"
ART=Path("validation_artifacts/p159/occ1h/a075_post_correction_evidence_v1.json")
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _dig(d): return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def verify_document(d):
    if d.get("schema")!=SCHEMA or d.get("attack_id")!="A075": return False
    if (d.get("historical_verdict"),d.get("current_verdict"))!=("INCONCLUSIVE","RESISTED"): return False
    if d.get("current_reason")!="UNAUTHORIZED_VERIFIER_IDENTITY_DRIFT_CANNOT_REBIND_PRECLOSE_TRUST": return False
    if d.get("post_correction_probe_sha256")!=EXPECTED_PROBE_SHA256 or d.get("historical_h7_bundle_sha256")!=EXPECTED_H7_SHA256: return False
    if any(d.get(k) is not False for k in ("historical_evidence_rewritten","authorization_created","execution_performed","normative_auto_rewrite","occ1h_closed","occ1i_opened","p159_final_lock","p160_opened")): return False
    x=dict(d); claimed=x.pop("evidence_sha256",None)
    return isinstance(claimed,str) and claimed==_dig(x)
def verify_materialized(root):
    root=Path(root); p=root/ART
    if not p.is_file(): return False
    try:
        d=json.loads(p.read_text(encoding="utf-8"))
        if not verify_document(d): return False
        pp=root/"ontology/occ1h_h7_a075_post_correction_independent_revalidation.py"
        hp=root/"validation_artifacts/p159/occ1h/h7_execution_bundle_v1.json"
        if pp.is_file() and _sha(pp)!=d["post_correction_probe_sha256"]: return False
        if hp.is_file() and _sha(hp)!=d["historical_h7_bundle_sha256"]: return False
        return True
    except Exception: return False
