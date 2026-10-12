from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import hashlib,json,os,tempfile
from ontology import occ_normative_ir as nir
PASS="PASS"
REQUIRED_FILES=("compiled_normative_profile_v1.json","compilation_transaction_v1.json",
"independent_semantic_verification_v1.json","compile_report_v1.json","transformation_ledger_v1.json",
"compiler_manifest_v1.json","bounded_gaps_evidence_v1.json","canonical_readiness_audit_v1_1.json")
def raw_sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def canonical_hash(x): return nir.canonical_sha256(x)
def verify_readiness(r):
    p=r.get("payload",{})
    return (r.get("status")==PASS and p.get("decision")=="OCC1C_READY_TO_CLOSE"
      and p.get("counts")=={"SATISFIED":25,"BOUNDED":0,"MISSING":0}
      and p.get("occ1c_closed") is False and p.get("occ1d_opened") is False
      and p.get("p160_opened") is False and p.get("p159_final_lock_performed") is False
      and r.get("audit_sha256")==canonical_hash(p))
def build(artifact_dir:Path):
    artifact_dir=Path(artifact_dir)
    paths={n:artifact_dir/n for n in REQUIRED_FILES}
    if not all(p.is_file() for p in paths.values()):
        return {"status":"FAIL","reason":"REQUIRED_CLOSURE_EVIDENCE_MISSING"}
    readiness=load(paths["canonical_readiness_audit_v1_1.json"])
    if not verify_readiness(readiness):
        return {"status":"FAIL","reason":"READINESS_NOT_VERIFIED"}
    profile=load(paths["compiled_normative_profile_v1.json"])
    tx=load(paths["compilation_transaction_v1.json"])
    sem=load(paths["independent_semantic_verification_v1.json"])
    # Bind the already validated profile/transaction/proof identities without manufacturing new semantics.
    bindings={n:raw_sha(p) for n,p in paths.items()}
    payload={"schema":"oce.p159.occ1c.closure_transaction.v1","milestone":"P159/OCC-1C",
      "transition":"OPEN_READY_TO_CLOSE->CLOSED","decision":"OCC1C_CLOSING_TRANSACTION_COMMITTED_VALID",
      "readiness_decision":"OCC1C_READY_TO_CLOSE","readiness_counts":{"SATISFIED":25,"BOUNDED":0,"MISSING":0},
      "readiness_audit_sha256":readiness["audit_sha256"],"evidence_file_sha256":bindings,
      "profile_artifact_sha256":bindings["compiled_normative_profile_v1.json"],
      "compilation_transaction_artifact_sha256":bindings["compilation_transaction_v1.json"],
      "independent_semantic_proof_artifact_sha256":bindings["independent_semantic_verification_v1.json"],
      "authorization_created":False,"authority_activated":False,"execution_performed":False,
      "occ1c_closed":True,"occ1d_opened":False,"p160_opened":False,"p159_final_lock":False,
      "functional_conclusion_only":True,"phenomenology_undetermined":True}
    payload["transaction_id"]=canonical_hash(payload)
    return {"status":PASS,"reason":"P159_OCC1C_CLOSING_TRANSACTION_READY","payload":payload}
def verify(obj,artifact_dir:Path):
    if obj.get("status")!=PASS: return False
    p=obj.get("payload",{}); tid=p.get("transaction_id")
    q=deepcopy(p); q.pop("transaction_id",None)
    if tid!=canonical_hash(q): return False
    if p.get("decision")!="OCC1C_CLOSING_TRANSACTION_COMMITTED_VALID": return False
    if p.get("readiness_counts")!={"SATISFIED":25,"BOUNDED":0,"MISSING":0}: return False
    if p.get("authorization_created") is not False or p.get("authority_activated") is not False or p.get("execution_performed") is not False: return False
    if p.get("occ1c_closed") is not True or p.get("occ1d_opened") is not False or p.get("p160_opened") is not False or p.get("p159_final_lock") is not False: return False
    expected=build(Path(artifact_dir))
    return expected.get("status")==PASS and expected.get("payload")==p
