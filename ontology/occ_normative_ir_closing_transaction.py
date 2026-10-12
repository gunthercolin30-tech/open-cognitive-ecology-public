from __future__ import annotations
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_evidence_effect_policy import EvidenceEffectDecision
from ontology.governed_evidence_filesystem_bridge import GovernedEvidenceFilesystemBridge
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json, os, tempfile
from pathlib import Path
from typing import Any, Dict

from ontology import occ_normative_ir as nir
from ontology import occ_normative_ir_closure_audit as auditmod

PRIMITIVE="occ_normative_ir_closing_transaction"
VERSION="P159-OCC1B-closing-transaction-v1"
PASS,FAIL="PASS","FAIL"
SCHEMA="oce.p159.occ1b.closing_transaction.v1"

def _canonical_bytes(obj:Dict[str,Any])->bytes:
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")

def _sha_file(p:Path)->str:
    return sha256(p.read_bytes()).hexdigest()

def _source_identity(package_root:Path)->Dict[str,str]:
    root=Path(package_root)
    out={}
    for p in sorted(x for x in root.rglob("*") if x.is_file() and not x.name.endswith(".bak")):
        out[str(p.relative_to(root))]=_sha_file(p)
    return out

def _artifact_payload(audit_result:Dict[str,Any], source_identity:Dict[str,str])->Dict[str,Any]:
    r=audit_result["report"]
    return {
        "schema":SCHEMA,
        "milestone":"P159/OCC-1B",
        "transition":"OPEN_TO_CLOSED",
        "decision":"COMMITTED_VALID",
        "closure_basis":"OCC1B_CLOSURE_AUDIT_READY",
        "closure_audit_report_sha256":audit_result["report_sha256"],
        "requirements_total":r["requirements_total"],
        "satisfied_count":r["satisfied_count"],
        "bounded_count":r["bounded_count"],
        "missing_count":r["missing_count"],
        "bounded_requirements":list(r["bounded_requirements"]),
        "source_identity":source_identity,
        "occ1b_closed":True,
        "post_close_verified":False,
        "authority_activated":False,
        "execution_performed":False,
        "occ1c_opened":False,
        "p160_opened":False,
        "p159_final_lock_performed":False,
        "functional_conclusion_only":True,
        "phenomenology_undetermined":True,
    }

def _envelope(payload:Dict[str,Any])->Dict[str,Any]:
    txid=nir.canonical_sha256(payload)
    return {"transaction_id":txid,"payload":payload,"payload_sha256":txid}

def verify_artifact(obj:Dict[str,Any])->Dict[str,str]:
    try:
        payload=obj["payload"]; supplied=obj["payload_sha256"]; txid=obj["transaction_id"]
    except Exception:
        return {"status":FAIL,"reason":"CLOSING_ARTIFACT_STRUCTURE_INVALID"}
    actual=nir.canonical_sha256(payload)
    if supplied!=actual or txid!=actual:
        return {"status":FAIL,"reason":"CLOSING_ARTIFACT_TAMPER_DETECTED"}
    if payload.get("schema")!=SCHEMA or payload.get("decision")!="COMMITTED_VALID":
        return {"status":FAIL,"reason":"CLOSING_ARTIFACT_SEMANTICS_INVALID"}
    return {"status":PASS,"reason":"CLOSING_ARTIFACT_INTEGRITY_OK"}

def _atomic_write(path:Path,obj:Dict[str,Any],filesystem_effect_context=None)->None:
    if filesystem_effect_context is None: raise RuntimeError("governed_filesystem_effect_context_required")
    filesystem_effect_context.execute_path("normative_ir_parent_create","FS_CREATE_DIRS",path.parent)
    data=_canonical_bytes(obj)+b"\n"
    filesystem_effect_context.execute_path("normative_ir_write_replace","FS_WRITE_REPLACE_BYTES",path,data)

def _rollback_remove(
    path:Path,
    filesystem_effect_bridge=None,
    rollback_evidence_decision=None,
)->bool:
    """Best-effort rollback without ambient filesystem authority."""
    if filesystem_effect_bridge is None or rollback_evidence_decision is None:
        return False
    root_path=getattr(getattr(filesystem_effect_bridge,"filesystem_context",None),"root_path",None)
    if root_path is None:
        return False
    try:
        relative=Path(path).resolve().relative_to(Path(root_path).resolve())
    except (OSError,ValueError):
        return False
    try:
        result=filesystem_effect_bridge.execute_path(
            decision=rollback_evidence_decision,
            evidence_role="normative_ir_closing_artifact_rollback",
            slot="normative_ir_rollback_remove",
            operation_id="FS_REMOVE_FILE",
            path=relative,
        )
    except Exception:
        return False
    return isinstance(result,dict) and result.get("status")=="EVIDENCE_EFFECT_CONFIRMED"

def close(
    package_root:Path,
    artifact_path:Path,
    filesystem_effect_context=None,
    filesystem_effect_bridge=None,
    rollback_evidence_decision=None,
)->Dict[str,Any]:
    root=Path(package_root); target=Path(artifact_path)
    before=_source_identity(root)

    ar=auditmod.audit(root)
    if ar.get("status")!=PASS or ar.get("decision")!="READY_TO_CLOSE":
        return {"status":FAIL,"reason":"OCC1B_NOT_READY_TO_CLOSE","occ1b_closed":False}

    rr=ar["report"]
    if rr.get("requirements_total")!=27 or rr.get("satisfied_count")!=25 or \
       rr.get("bounded_count")!=2 or rr.get("missing_count")!=0 or \
       rr.get("bounded_requirements")!=["C08","C09"]:
        return {"status":FAIL,"reason":"CLOSURE_BASIS_CONTRACT_INVALID","occ1b_closed":False}

    # Re-read source identity immediately before commit to detect drift during evaluation.
    precommit=_source_identity(root)
    if before!=precommit:
        return {"status":FAIL,"reason":"SOURCE_DRIFT_BEFORE_COMMIT","occ1b_closed":False}

    expected=_envelope(_artifact_payload(ar,precommit))

    if target.exists():
        try:
            existing=json.loads(target.read_text(encoding="utf-8"))
        except Exception:
            return {"status":FAIL,"reason":"EXISTING_CLOSURE_ARTIFACT_UNREADABLE","occ1b_closed":False}
        vr=verify_artifact(existing)
        if vr["status"]!=PASS:
            return {"status":FAIL,"reason":vr["reason"],"occ1b_closed":False}
        if existing!=expected:
            return {"status":FAIL,"reason":"DIVERGENT_REPLAY_REJECTED","occ1b_closed":False}
        return {"status":PASS,"reason":"P159_OCC1B_CLOSING_TRANSACTION_IDEMPOTENT",
                "transaction_id":existing["transaction_id"],"artifact_path":str(target),
                "occ1b_closed":True,"post_close_verified":False}

    _atomic_write(target,expected,filesystem_effect_context)

    # Verify persisted bytes and ensure normative source remained unchanged.
    try:
        persisted=json.loads(target.read_text(encoding="utf-8"))
    except Exception:
        _rollback_remove(target,filesystem_effect_bridge,rollback_evidence_decision)
        return {"status":FAIL,"reason":"PERSISTED_ARTIFACT_UNREADABLE_ROLLBACK","occ1b_closed":False}
    if verify_artifact(persisted)["status"]!=PASS or persisted!=expected:
        _rollback_remove(target,filesystem_effect_bridge,rollback_evidence_decision)
        return {"status":FAIL,"reason":"PERSISTED_ARTIFACT_VERIFY_FAILED_ROLLBACK","occ1b_closed":False}
    after=_source_identity(root)
    if after!=before:
        _rollback_remove(target,filesystem_effect_bridge,rollback_evidence_decision)
        return {"status":FAIL,"reason":"SOURCE_MUTATION_DETECTED_ROLLBACK","occ1b_closed":False}

    return {"status":PASS,"reason":"P159_OCC1B_CLOSING_TRANSACTION_COMMITTED",
            "transaction_id":expected["transaction_id"],"artifact_path":str(target),
            "occ1b_closed":True,"post_close_verified":False,
            "authority_activated":False,"execution_performed":False,
            "occ1c_opened":False,"p160_opened":False,"p159_final_lock_performed":False}
