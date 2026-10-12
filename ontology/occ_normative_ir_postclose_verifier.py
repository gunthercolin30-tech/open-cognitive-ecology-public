from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict

from ontology import occ_normative_ir as nir

PRIMITIVE="occ_normative_ir_postclose_verifier"
VERSION="P159-OCC1B-postclose-verifier-v1"
PASS,FAIL="PASS","FAIL"
TX_SCHEMA="oce.p159.occ1b.closing_transaction.v1"
PROOF_SCHEMA="oce.p159.occ1b.postclose_verification.v1"

def _sha_file(p:Path)->str:
    return sha256(p.read_bytes()).hexdigest()

def _source_identity(root:Path)->Dict[str,str]:
    out={}
    for p in sorted(x for x in Path(root).rglob("*") if x.is_file() and not x.name.endswith(".bak")):
        out[str(p.relative_to(root))]=_sha_file(p)
    return out

def _load(path:Path)->Dict[str,Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def verify(package_root:Path, closure_artifact:Path)->Dict[str,Any]:
    root=Path(package_root); artifact=Path(closure_artifact)
    if not root.is_dir():
        return {"status":FAIL,"reason":"SOURCE_PACKAGE_MISSING"}
    if not artifact.is_file():
        return {"status":FAIL,"reason":"CLOSURE_ARTIFACT_MISSING"}
    try:
        obj=_load(artifact)
        payload=obj["payload"]
    except Exception:
        return {"status":FAIL,"reason":"CLOSURE_ARTIFACT_STRUCTURE_INVALID"}

    # Independent cryptographic reconstruction: do not call writer verify_artifact/close.
    actual_payload_sha=nir.canonical_sha256(payload)
    if obj.get("payload_sha256")!=actual_payload_sha:
        return {"status":FAIL,"reason":"PAYLOAD_SHA_MISMATCH"}
    if obj.get("transaction_id")!=actual_payload_sha:
        return {"status":FAIL,"reason":"TRANSACTION_ID_MISMATCH"}

    checks={
      "schema":payload.get("schema")==TX_SCHEMA,
      "milestone":payload.get("milestone")=="P159/OCC-1B",
      "transition":payload.get("transition")=="OPEN_TO_CLOSED",
      "decision":payload.get("decision")=="COMMITTED_VALID",
      "closure_basis":payload.get("closure_basis")=="OCC1B_CLOSURE_AUDIT_READY",
      "requirements":payload.get("requirements_total")==27,
      "satisfied":payload.get("satisfied_count")==25,
      "bounded":payload.get("bounded_count")==2,
      "missing":payload.get("missing_count")==0,
      "bounded_ids":payload.get("bounded_requirements")==["C08","C09"],
      "closed":payload.get("occ1b_closed") is True,
      "writer_not_self_verified":payload.get("post_close_verified") is False,
      "no_authority":payload.get("authority_activated") is False,
      "no_execution":payload.get("execution_performed") is False,
      "occ1c_closed":payload.get("occ1c_opened") is False,
      "p160_closed":payload.get("p160_opened") is False,
      "no_final_lock":payload.get("p159_final_lock_performed") is False,
      "functional_only":payload.get("functional_conclusion_only") is True,
      "phenomenology_undetermined":payload.get("phenomenology_undetermined") is True,
    }
    bad=[k for k,v in checks.items() if not v]
    if bad:
        return {"status":FAIL,"reason":"CLOSURE_SEMANTICS_INVALID","failed_checks":bad}

    recorded=payload.get("source_identity")
    if not isinstance(recorded,dict) or not recorded:
        return {"status":FAIL,"reason":"RECORDED_SOURCE_IDENTITY_INVALID"}
    current=_source_identity(root)
    if current!=recorded:
        missing=sorted(set(recorded)-set(current))
        added=sorted(set(current)-set(recorded))
        changed=sorted(k for k in set(current)&set(recorded) if current[k]!=recorded[k])
        return {"status":FAIL,"reason":"POSTCLOSE_SOURCE_DRIFT_DETECTED",
                "missing_files":missing,"added_files":added,"changed_files":changed}

    proof={
      "schema":PROOF_SCHEMA,
      "milestone":"P159/OCC-1B",
      "verification":"INDEPENDENT_POST_CLOSE",
      "closure_transaction_id":obj["transaction_id"],
      "closure_artifact_sha256":_sha_file(artifact),
      "closure_payload_sha256":actual_payload_sha,
      "source_identity_sha256":nir.canonical_sha256(recorded),
      "requirements_total":27,
      "satisfied_count":25,
      "bounded_count":2,
      "missing_count":0,
      "bounded_requirements":["C08","C09"],
      "occ1b_closed":True,
      "post_close_verified":True,
      "authority_activated":False,
      "execution_performed":False,
      "occ1c_opened":False,
      "p160_opened":False,
      "p159_final_lock_performed":False,
      "writer_verify_function_used":False,
      "writer_close_function_used":False,
      "source_package_mutated":False,
      "functional_conclusion_only":True,
      "phenomenology_undetermined":True,
    }
    proof["proof_sha256"]=nir.canonical_sha256(proof)
    return {"status":PASS,"reason":"P159_OCC1B_POSTCLOSE_VERIFICATION_OK",
            "proof":proof,"proof_sha256":proof["proof_sha256"]}

def verify_proof(proof:Dict[str,Any])->Dict[str,str]:
    p=deepcopy(proof)
    supplied=p.pop("proof_sha256",None)
    actual=nir.canonical_sha256(p)
    return {"status":PASS if supplied==actual else FAIL,
            "reason":"POSTCLOSE_PROOF_INTEGRITY_OK" if supplied==actual else "POSTCLOSE_PROOF_TAMPER_DETECTED"}
