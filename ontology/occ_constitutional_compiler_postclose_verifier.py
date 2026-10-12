from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import hashlib,json
from ontology import occ_normative_ir as nir
PASS="PASS"
EVIDENCE=("compiled_normative_profile_v1.json","compilation_transaction_v1.json",
"independent_semantic_verification_v1.json","compile_report_v1.json","transformation_ledger_v1.json",
"compiler_manifest_v1.json","bounded_gaps_evidence_v1.json","canonical_readiness_audit_v1_1.json")
CLOSURE="occ1c_closure_transaction_v1.json"
def raw_sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def ch(x): return nir.canonical_sha256(x)
def verify(artifact_dir:Path):
    d=Path(artifact_dir); paths={n:d/n for n in EVIDENCE+(CLOSURE,)}
    if not all(p.is_file() for p in paths.values()):
        return {"status":"FAIL","reason":"POSTCLOSE_REQUIRED_ARTIFACT_MISSING"}
    r=load(paths["canonical_readiness_audit_v1_1.json"]); rp=r.get("payload",{})
    if not (r.get("status")==PASS and rp.get("decision")=="OCC1C_READY_TO_CLOSE"
      and rp.get("counts")=={"SATISFIED":25,"BOUNDED":0,"MISSING":0}
      and r.get("audit_sha256")==ch(rp)):
        return {"status":"FAIL","reason":"POSTCLOSE_READINESS_INVALID"}
    clo=load(paths[CLOSURE]); cp=clo.get("payload",{})
    if clo.get("status")!=PASS: return {"status":"FAIL","reason":"CLOSURE_STATUS_INVALID"}
    q=deepcopy(cp); tid=q.pop("transaction_id",None)
    if tid!=ch(q): return {"status":"FAIL","reason":"CLOSURE_TRANSACTION_ID_INVALID"}
    if cp.get("decision")!="OCC1C_CLOSING_TRANSACTION_COMMITTED_VALID":
        return {"status":"FAIL","reason":"CLOSURE_DECISION_INVALID"}
    if cp.get("readiness_decision")!="OCC1C_READY_TO_CLOSE" or cp.get("readiness_counts")!={"SATISFIED":25,"BOUNDED":0,"MISSING":0}:
        return {"status":"FAIL","reason":"CLOSURE_READINESS_BINDING_INVALID"}
    if cp.get("readiness_audit_sha256")!=r.get("audit_sha256"):
        return {"status":"FAIL","reason":"CLOSURE_READINESS_HASH_INVALID"}
    expected={n:raw_sha(paths[n]) for n in EVIDENCE}
    if cp.get("evidence_file_sha256")!=expected:
        return {"status":"FAIL","reason":"UPSTREAM_EVIDENCE_DRIFT"}
    if cp.get("profile_artifact_sha256")!=expected["compiled_normative_profile_v1.json"]:
        return {"status":"FAIL","reason":"PROFILE_BINDING_INVALID"}
    if cp.get("compilation_transaction_artifact_sha256")!=expected["compilation_transaction_v1.json"]:
        return {"status":"FAIL","reason":"COMPILATION_TRANSACTION_BINDING_INVALID"}
    if cp.get("independent_semantic_proof_artifact_sha256")!=expected["independent_semantic_verification_v1.json"]:
        return {"status":"FAIL","reason":"SEMANTIC_PROOF_BINDING_INVALID"}
    if cp.get("authorization_created") is not False or cp.get("authority_activated") is not False or cp.get("execution_performed") is not False:
        return {"status":"FAIL","reason":"POSTCLOSE_POWER_INFLATION"}
    if cp.get("occ1c_closed") is not True or cp.get("occ1d_opened") is not False or cp.get("p160_opened") is not False or cp.get("p159_final_lock") is not False:
        return {"status":"FAIL","reason":"POSTCLOSE_STAGE_BOUNDARY_INVALID"}
    payload={"schema":"oce.p159.occ1c.postclose_verification.v1","milestone":"P159/OCC-1C",
      "decision":"OCC1C_CLOSED_POSTCLOSE_VERIFIED","closure_transaction_id":tid,
      "closure_artifact_sha256":raw_sha(paths[CLOSURE]),"readiness_audit_sha256":r["audit_sha256"],
      "evidence_file_sha256":expected,"readiness":{"SATISFIED":25,"BOUNDED":0,"MISSING":0},
      "closure_identity_verified":True,"upstream_evidence_verified":True,"source_drift_detected":False,
      "authorization_created":False,"authority_activated":False,"execution_performed":False,
      "occ1c_closed":True,"postclose_verified":True,"occ1d_opened":False,"p160_opened":False,
      "p159_final_lock":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    payload["proof_sha256"]=ch(payload)
    return {"status":PASS,"reason":"P159_OCC1C_POSTCLOSE_VERIFICATION_VERIFIED","payload":payload}
def verify_proof(obj,artifact_dir:Path):
    if obj.get("status")!=PASS:return False
    p=obj.get("payload",{}); supplied=p.get("proof_sha256")
    q=deepcopy(p); q.pop("proof_sha256",None)
    if supplied!=ch(q): return False
    fresh=verify(Path(artifact_dir))
    return fresh.get("status")==PASS and fresh.get("payload")==p
