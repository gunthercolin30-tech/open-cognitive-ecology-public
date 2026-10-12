from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict

def _p162g6_execute_evidence_write(bridge, decision, slot, path, payload, evidence_role):
    # Exact evidence write; never an authority source.
    if bridge is None or decision is None:
        raise RuntimeError("governed_evidence_bridge_and_decision_required")
    ctx = getattr(bridge, "filesystem_context", None)
    root_path = getattr(ctx, "root_path", None)
    if root_path is None:
        raise RuntimeError("filesystem_context_root_path_required")
    root = Path(root_path).expanduser().resolve()
    target = Path(path).expanduser()
    if not target.is_absolute():
        target = root / target
    try:
        relative = target.resolve(strict=False).relative_to(root).as_posix()
    except ValueError as exc:
        raise RuntimeError("evidence_target_outside_governed_root") from exc
    result = bridge.execute_path(
        decision=decision,
        evidence_role=evidence_role,
        slot=slot,
        operation_id="FS_WRITE_REPLACE_BYTES",
        path=relative,
        payload=payload,
    )
    if not isinstance(result, dict) or result.get("status") != "EVIDENCE_EFFECT_CONFIRMED":
        raise RuntimeError("evidence_effect_not_confirmed")
    return result

SCHEMA = "oce.p159.occ1e.postclose_verification.v1"

def _hash_bytes(p: Path) -> str:
    return sha256(p.read_bytes()).hexdigest()

def _hash_obj(x: Any) -> str:
    return sha256(json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def _load(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))

def paths(root: Path) -> Dict[str, Path]:
    a = root / "validation_artifacts" / "p159"
    e = a / "occ1e"
    static = a / "occ1d" / "static_constitutional_check_report_v1_2.json"
    if not static.exists():
        static = a / "occ1d" / "static_constitutional_check_report_v1.json"
    return {
        "profile": e / "compiled_normative_profile_v1.json",
        "manifest": e / "compiled_normative_profile_manifest_v1.json",
        "runtime": e / "runtime_interface_contract_v1.json",
        "explanation": e / "compiled_normative_profile_explanation_v1.txt",
        "crown": e / "occ1e_crown_report_v1.json",
        "closure": e / "occ1e_closing_transaction_v1.json",
        "schema": root / "schemas" / "p159_occ1e_compiled_normative_profile_v1.schema.json",
        "compiler": root / "ontology" / "occ_constitutional_compiler.py",
        "source": a / "occ1c" / "compiled_normative_profile_v1.json",
        "static": static,
        "output": e / "occ1e_postclose_verification_v1.json",
    }

def verify(root: Path) -> Dict[str, Any]:
    root = Path(root)
    p = paths(root)
    missing = [k for k,v in p.items() if k != "output" and not v.is_file()]
    if missing:
        return {"schema":SCHEMA,"decision":"OCC1E_POSTCLOSE_REJECTED","missing":sorted(missing),
                "occ1e_closed":False,"postclose_verified":False,"occ1f_opened":False,
                "p160_opened":False,"p159_final_lock":False,
                "functional_conclusion_only":True,"phenomenology_undetermined":True}

    closure = _load(p["closure"])
    profile = _load(p["profile"])
    checks = {}

    # Independent reconstruction: do not import or call the closing transaction.
    current_hashes = {k:_hash_bytes(v) for k,v in p.items() if k not in ("output","closure")}
    recorded = closure.get("input_hashes", {})
    checks["closure_decision_valid"] = closure.get("decision") == "OCC1E_CLOSING_TRANSACTION_COMMITTED_VALID"
    checks["closure_scope_local"] = closure.get("closure_scope") == "LOCAL_OCC1E_ONLY"
    checks["closure_claim_true"] = closure.get("occ1e_closed") is True
    checks["exact_inputs_unchanged"] = all(recorded.get(k) == h for k,h in current_hashes.items())
    checks["no_unexpected_recorded_input_loss"] = set(current_hashes).issubset(set(recorded))

    payload = deepcopy(profile)
    semantic = payload.pop("artifact_hash", None)
    checks["profile_semantic_hash_valid"] = semantic == _hash_obj(payload)
    checks["profile_semantic_hash_matches_closure"] = semantic == closure.get("profile_semantic_hash")

    snap = deepcopy(profile.get("constitutional_snapshot", {}))
    snap_hash = snap.pop("snapshot_hash", None)
    checks["snapshot_hash_valid"] = bool(snap_hash) and snap_hash == _hash_obj(snap)
    checks["snapshot_matches_closure"] = snap_hash == closure.get("constitutional_snapshot_hash")

    checks["epistemic_limits_preserved"] = (
        closure.get("runtime_consumer_graph_proven") is False and
        closure.get("enforcement_status") == "UNRESOLVED" and
        closure.get("functional_conclusion_only") is True and
        closure.get("phenomenology_undetermined") is True
    )
    checks["no_authority_or_execution"] = (
        closure.get("authorization_created") is False and
        closure.get("authority_activated") is False and
        closure.get("execution_performed") is False and
        closure.get("self_activation") is False
    )
    checks["downstream_unopened"] = (
        closure.get("occ1f_opened") is False and
        closure.get("p160_opened") is False and
        closure.get("p159_final_lock") is False
    )

    ok = all(checks.values())
    basis = {
        "milestone":"P159/OCC-1E",
        "closure_artifact_sha256":_hash_bytes(p["closure"]),
        "closure_transaction_id":closure.get("transaction_id"),
        "checks":checks,
        "current_input_hashes":current_hashes,
    }
    proof_sha = _hash_obj(basis)
    return {
        "schema":SCHEMA,
        "milestone":"P159/OCC-1E",
        "decision":"OCC1E_CLOSED_POSTCLOSE_VERIFIED" if ok else "OCC1E_POSTCLOSE_REJECTED",
        "postclose_proof_sha256":proof_sha,
        "closure_artifact_sha256":_hash_bytes(p["closure"]),
        "closure_transaction_id":closure.get("transaction_id"),
        "checks":checks,
        "occ1e_closed":ok,
        "postclose_verified":ok,
        "source_drift_detected":not checks.get("exact_inputs_unchanged", False),
        "runtime_consumer_graph_proven":False,
        "enforcement_status":"UNRESOLVED",
        "authorization_created":False,
        "authority_activated":False,
        "execution_performed":False,
        "occ1f_opened":False,
        "p160_opened":False,
        "p159_final_lock":False,
        "functional_conclusion_only":True,
        "phenomenology_undetermined":True,
    }

def commit(root: Path, evidence_bridge=None, evidence_decision=None) -> Dict[str, Any]:
    r = verify(root)
    if not r.get("postclose_verified"):
        raise RuntimeError("OCC1E_POSTCLOSE_REJECTED")
    out = paths(Path(root))["output"]
    content = json.dumps(r, indent=2, sort_keys=True) + "\n"
    if out.exists() and out.read_text(encoding="utf-8") != content:
        raise RuntimeError("OCC1E_POSTCLOSE_ARTIFACT_DIVERGES")
    _p162g6_execute_evidence_write(evidence_bridge, evidence_decision, "postclose_commit_write", out, content.encode("utf-8"), "VALIDATION_EVIDENCE_OR_AUDIT")
    print("OCC1E_CLOSED_POSTCLOSE_VERIFIED")
    print("postclose_proof_sha256=" + r["postclose_proof_sha256"])
    print("source_drift_detected=false")
    print("OCC1F_NOT_OPENED")
    print("P160_NOT_OPENED")
    print("P159_FINAL_LOCK_FALSE")
    return r

if __name__ == "__main__":
    commit(Path.home() / "open-cognitive-ecology")
