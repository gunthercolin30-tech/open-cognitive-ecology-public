from __future__ import annotations
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from copy import deepcopy
from hashlib import sha256
import json, os, tempfile
from pathlib import Path
from typing import Any, Dict

from ontology import occ_constitutional_compiler as compiler
from ontology import occ_normative_ir as nir

PRIMITIVE="occ_constitutional_compilation_transaction"
VERSION="P159-OCC1C-compilation-transaction-v1"
SCHEMA="oce.p159.occ1c.compilation_transaction.v1"
PASS,FAIL="PASS","FAIL"

def _sha(p:Path)->str: return sha256(p.read_bytes()).hexdigest()

def _source_identity(root:Path)->Dict[str,str]:
    return {str(p.relative_to(root)):_sha(p)
            for p in sorted(Path(root).rglob("*"))
            if p.is_file() and not p.name.endswith(".bak")}

def _atomic_json(path:Path,obj:Dict[str,Any],filesystem_effect_context=None,slot:str="constitutional_compile_write")->None:
    if filesystem_effect_context is None: raise RuntimeError("governed_filesystem_effect_context_required")
    parent_slot=(slot[:-len("_write_replace")] if slot.endswith("_write_replace") else slot[:-len("_write")] if slot.endswith("_write") else slot)+"_parent_create"
    filesystem_effect_context.execute_path(parent_slot,"FS_CREATE_DIRS",path.parent)
    data=(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode("utf-8")
    filesystem_effect_context.execute_path(slot,"FS_WRITE_REPLACE_BYTES",path,data)

def verify_transaction(obj:Dict[str,Any])->Dict[str,Any]:
    if not isinstance(obj,dict): return {"status":FAIL,"reason":"TRANSACTION_NOT_MAPPING"}
    payload=obj.get("payload")
    if not isinstance(payload,dict): return {"status":FAIL,"reason":"TRANSACTION_PAYLOAD_MISSING"}
    calc=nir.canonical_sha256(payload)
    if obj.get("payload_sha256")!=calc or obj.get("transaction_id")!=calc:
        return {"status":FAIL,"reason":"TRANSACTION_HASH_MISMATCH"}
    required={
      "schema":SCHEMA,"milestone":"P159/OCC-1C","transition":"COMPILE_AND_PERSIST",
      "decision":"COMMITTED_VALID","profile_state":"UNVERIFIED_COMPILED_PROFILE",
      "compiled_rules":48,"silent_loss":0,"invented_norms":0,
      "authorization_created":False,"authority_activated":False,"execution_performed":False,
      "generated_python":False,"executable_payload":False,
      "conflict_arbitrated":False,"source_modified":False,
      "occ1d_opened":False,"p160_opened":False,"p159_final_lock_performed":False,
      "functional_conclusion_only":True,"phenomenology_undetermined":True,
    }
    bad=[k for k,v in required.items() if payload.get(k)!=v]
    if bad: return {"status":FAIL,"reason":"TRANSACTION_SEMANTICS_INVALID","failed_checks":bad}
    return {"status":PASS,"reason":"OCC1C_COMPILATION_TRANSACTION_INTEGRITY_OK"}

def commit(source_root:Path, proof_path:Path, profile_path:Path, tx_path:Path, filesystem_effect_context=None)->Dict[str,Any]:
    source_root=Path(source_root); proof_path=Path(proof_path)
    profile_path=Path(profile_path); tx_path=Path(tx_path)
    before=_source_identity(source_root)

    result=compiler.compile_profile(source_root,proof_path)
    if result.get("status")!=PASS:
        return {"status":FAIL,"reason":"COMPILATION_FAILED","detail":result.get("reason")}
    profile=result["profile"]
    if compiler.verify_profile(profile).get("status")!=PASS:
        return {"status":FAIL,"reason":"COMPILED_PROFILE_SELF_INTEGRITY_FAILED"}
    if _source_identity(source_root)!=before:
        return {"status":FAIL,"reason":"SOURCE_MUTATION_DURING_COMPILATION"}

    profile_data=json.dumps(profile,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n"
    if profile_path.exists():
        if profile_path.read_text(encoding="utf-8")!=profile_data:
            return {"status":FAIL,"reason":"DIVERGENT_PROFILE_REPLAY_REJECTED"}
    else:
        _atomic_json(profile_path,profile,filesystem_effect_context,'constitutional_profile_write_replace')

    # Re-read persisted profile before committing transaction.
    persisted=json.loads(profile_path.read_text(encoding="utf-8"))
    if persisted!=profile or compiler.verify_profile(persisted).get("status")!=PASS:
        return {"status":FAIL,"reason":"PERSISTED_PROFILE_VERIFICATION_FAILED"}

    payload={
      "schema":SCHEMA,
      "milestone":"P159/OCC-1C",
      "transition":"COMPILE_AND_PERSIST",
      "decision":"COMMITTED_VALID",
      "compiler_version":compiler.VERSION,
      "profile_schema":compiler.SCHEMA,
      "profile_state":"UNVERIFIED_COMPILED_PROFILE",
      "profile_sha256":profile["profile_sha256"],
      "profile_artifact_sha256":_sha(profile_path),
      "occ1b_postclose_proof_sha256":_sha(proof_path),
      "source_nir_sha256":profile["source_nir_sha256"],
      "source_identity":before,
      "compiled_rules":48,
      "silent_loss":0,
      "invented_norms":0,
      "authorization_created":False,
      "authority_activated":False,
      "execution_performed":False,
      "generated_python":False,
      "executable_payload":False,
      "conflict_arbitrated":False,
      "source_modified":False,
      "independent_semantic_verification_performed":False,
      "occ1d_opened":False,
      "p160_opened":False,
      "p159_final_lock_performed":False,
      "functional_conclusion_only":True,
      "phenomenology_undetermined":True,
    }
    tid=nir.canonical_sha256(payload)
    tx={"payload":payload,"payload_sha256":tid,"transaction_id":tid}

    if tx_path.exists():
        try: existing=json.loads(tx_path.read_text(encoding="utf-8"))
        except Exception: return {"status":FAIL,"reason":"EXISTING_TRANSACTION_UNREADABLE"}
        if existing!=tx: return {"status":FAIL,"reason":"DIVERGENT_TRANSACTION_REPLAY_REJECTED"}
    else:
        _atomic_json(tx_path,tx,filesystem_effect_context,'constitutional_tx_write_replace')

    persisted_tx=json.loads(tx_path.read_text(encoding="utf-8"))
    vr=verify_transaction(persisted_tx)
    if vr.get("status")!=PASS: return vr
    if _source_identity(source_root)!=before:
        return {"status":FAIL,"reason":"SOURCE_MUTATION_POST_COMMIT"}
    return {"status":PASS,"reason":"P159_OCC1C_COMPILATION_TRANSACTION_COMMITTED",
            "transaction_id":tid,"profile_sha256":profile["profile_sha256"],
            "profile_artifact_sha256":_sha(profile_path),
            "transaction_artifact_sha256":_sha(tx_path),
            "compiled_rules":48,"profile_state":"UNVERIFIED_COMPILED_PROFILE",
            "independent_semantic_verification_performed":False,
            "occ1d_opened":False,"p160_opened":False,"final_lock_performed":False}
