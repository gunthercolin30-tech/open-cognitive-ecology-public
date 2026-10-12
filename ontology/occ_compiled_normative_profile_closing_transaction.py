from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from ontology.governed_evidence_effect_policy import EvidenceEffectDecision
from ontology.governed_evidence_filesystem_bridge import GovernedEvidenceFilesystemBridge

PRIMITIVE = "occ_compiled_normative_profile_closing_transaction"
SCHEMA = "oce.p159.occ1e.closing_transaction.v1"

EXPECTED_CONSUMERS = {
    "NormResolver", "CCAD", "AuthorizationEngine", "CapabilityGate",
    "RecoveryEngine", "AssuranceEngine",
}

def _bytes_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()

def _canonical_hash(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()

def _load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def _paths(root: Path) -> Dict[str, Path]:
    a = root / "validation_artifacts" / "p159"
    occ1e = a / "occ1e"
    static_candidates = (
        a / "occ1d" / "static_constitutional_check_report_v1_2.json",
        a / "occ1d" / "static_constitutional_check_report_v1.json",
    )
    static = next((p for p in static_candidates if p.exists()), static_candidates[0])
    return {
        "profile": occ1e / "compiled_normative_profile_v1.json",
        "manifest": occ1e / "compiled_normative_profile_manifest_v1.json",
        "runtime": occ1e / "runtime_interface_contract_v1.json",
        "explanation": occ1e / "compiled_normative_profile_explanation_v1.txt",
        "crown": occ1e / "occ1e_crown_report_v1.json",
        "schema": root / "schemas" / "p159_occ1e_compiled_normative_profile_v1.schema.json",
        "compiler": root / "ontology" / "occ_constitutional_compiler.py",
        "source": a / "occ1c" / "compiled_normative_profile_v1.json",
        "static": static,
        "output": occ1e / "occ1e_closing_transaction_v1.json",
    }

def evaluate(root: Path) -> Dict[str, Any]:
    root = Path(root)
    p = _paths(root)
    missing = sorted(k for k, path in p.items() if k != "output" and not path.is_file())
    checks: Dict[str, bool] = {}
    details: Dict[str, Any] = {}

    if missing:
        return {
            "schema": SCHEMA, "milestone": "P159/OCC-1E",
            "decision": "OCC1E_CLOSE_REJECTED",
            "missing_inputs": missing, "checks": checks,
            "occ1e_closed": False, "occ1f_opened": False, "p160_opened": False,
            "p159_final_lock": False, "authorization_created": False,
            "authority_activated": False, "execution_performed": False,
            "functional_conclusion_only": True, "phenomenology_undetermined": True,
        }

    profile = _load(p["profile"])
    manifest = _load(p["manifest"])
    runtime = _load(p["runtime"])
    crown = _load(p["crown"])
    schema = _load(p["schema"])

    semantic_payload = deepcopy(profile)
    semantic_hash = semantic_payload.pop("artifact_hash", None)

    checks["profile_file_hash_bound"] = crown.get("profile_artifact_sha256") == _bytes_hash(p["profile"])
    checks["profile_semantic_hash_valid"] = semantic_hash == _canonical_hash(semantic_payload)
    checks["profile_semantic_hash_bound"] = crown.get("profile_semantic_hash") == semantic_hash
    checks["manifest_hash_bound"] = crown.get("manifest_sha256") == _bytes_hash(p["manifest"])
    checks["runtime_hash_bound"] = crown.get("runtime_interface_contract_sha256") == _bytes_hash(p["runtime"])
    checks["explanation_hash_bound"] = crown.get("explanation_sha256") == _bytes_hash(p["explanation"])
    checks["schema_hash_bound"] = crown.get("schema_sha256") == _bytes_hash(p["schema"])
    checks["compiler_hash_bound"] = crown.get("compiler_sha256") == _bytes_hash(p["compiler"])
    checks["occ1c_source_hash_bound"] = crown.get("occ1c_source_profile_sha256") == _bytes_hash(p["source"])
    checks["occ1d_static_hash_bound"] = crown.get("occ1d_static_report_sha256") == _bytes_hash(p["static"])

    snap = profile.get("constitutional_snapshot", {})
    snap_payload = deepcopy(snap)
    snap_hash = snap_payload.pop("snapshot_hash", None)
    checks["snapshot_present_and_hash_valid"] = bool(snap_hash) and snap_hash == _canonical_hash(snap_payload)
    checks["snapshot_source_bound"] = snap.get("occ1c_profile_hash") == _canonical_hash(_load(p["source"]))
    checks["snapshot_compiler_bound"] = snap.get("compiler_hash") == _bytes_hash(p["compiler"])
    checks["snapshot_schema_bound"] = snap.get("schema_hash") == _bytes_hash(p["schema"])
    checks["snapshot_static_report_bound"] = snap.get("static_validation_report_hash") == _bytes_hash(p["static"])

    checks["schema_complete_core"] = all(x in schema.get("required", []) for x in (
        "profile_id", "profile_version", "profile_state", "rules",
        "authority_model", "scope_model", "temporal_model", "uncertainty_model",
        "conflict_hooks", "enforcement_map", "runtime_interfaces", "source_map",
        "validation_report_hash", "constitutional_snapshot", "artifact_hash",
    ))
    checks["rule_count_48"] = len(profile.get("rules", [])) == 48 and manifest.get("rule_count") == 48
    checks["all_rules_source_mapped"] = all(
        bool(r.get("source_norm_ids")) and bool(r.get("nir_node_ids")) and isinstance(r.get("provenance"), dict)
        for r in profile.get("rules", [])
    )
    checks["lifecycle_defined"] = set(profile.get("lifecycle_model", {}).get("states", [])) >= {
        "DRAFT","COMPILED","VERIFIED","SEALED","CERTIFIED","ACTIVE",
        "SUPERSEDED","REVOKED","NON_ACTIVATABLE",
    }
    checks["immutability_defined"] = profile.get("lifecycle_model", {}).get("sealed_mutation_allowed") is False
    checks["governed_transition_required"] = profile.get("lifecycle_model", {}).get("status_changes_require_governed_transition") is True
    checks["self_activation_forbidden"] = profile.get("lifecycle_model", {}).get("self_activation") is False
    checks["non_activatable_promotion_forbidden"] = profile.get("lifecycle_model", {}).get("ordinary_activation_from_non_activatable") is False

    contract = profile.get("compiler_contract", {})
    checks["no_execute_primitive_or_payload"] = (
        contract.get("compiler_is_execution") is False and
        contract.get("execution_performed") is False and
        contract.get("executable_payload") is False and
        runtime.get("execution_capability") is False
    )
    checks["no_authorization_manufactured"] = (
        contract.get("compiler_is_authority") is False and
        contract.get("compilation_manufactures_legitimacy") is False and
        contract.get("authorization_created") is False and
        runtime.get("authorization_capability") is False and
        runtime.get("allow_candidate_is_permission_to_execute") is False
    )
    checks["consumers_explicit"] = set(runtime.get("consumers", [])) == EXPECTED_CONSUMERS
    checks["manifest_consistent"] = (
        manifest.get("artifact_hash") == semantic_hash and
        manifest.get("constitutional_snapshot_hash") == snap_hash and
        manifest.get("profile_state") == profile.get("profile_state") and
        manifest.get("authorization_created") is False and
        manifest.get("execution_performed") is False and
        manifest.get("self_activation") is False
    )
    checks["crown_scope_preserved"] = (
        crown.get("milestone") == "P159/OCC-1E" and
        crown.get("occ1e_closed") is False and
        crown.get("occ1f_opened") is False and
        crown.get("p160_opened") is False and
        crown.get("p159_final_lock") is False
    )
    checks["unresolved_runtime_evidence_preserved"] = (
        profile.get("enforcement_map", {}).get("status") == "UNRESOLVED" and
        profile.get("enforcement_map", {}).get("runtime_consumer_graph_proven") is False and
        runtime.get("enforcement_status") == "UNRESOLVED" and
        runtime.get("runtime_consumer_graph_proven") is False
    )
    checks["epistemic_invariants"] = (
        profile.get("functional_conclusion_only") is True and
        profile.get("phenomenology_undetermined") is True and
        runtime.get("functional_conclusion_only") is True and
        runtime.get("phenomenology_undetermined") is True
    )

    all_ok = bool(checks) and all(checks.values())
    details["input_hashes"] = {k: _bytes_hash(path) for k, path in p.items() if k != "output"}
    transaction_basis = {
        "milestone": "P159/OCC-1E",
        "checks": checks,
        "input_hashes": details["input_hashes"],
        "profile_semantic_hash": semantic_hash,
        "snapshot_hash": snap_hash,
        "unresolved_runtime_evidence_preserved": True,
        "occ1f_opened": False,
        "p160_opened": False,
        "p159_final_lock": False,
    }
    transaction_id = _canonical_hash(transaction_basis)

    return {
        "schema": SCHEMA,
        "milestone": "P159/OCC-1E",
        "decision": "OCC1E_CLOSING_TRANSACTION_COMMITTED_VALID" if all_ok else "OCC1E_CLOSE_REJECTED",
        "transaction_id": transaction_id,
        "checks": checks,
        "input_hashes": details["input_hashes"],
        "profile_semantic_hash": semantic_hash,
        "constitutional_snapshot_hash": snap_hash,
        "occ1e_closed": all_ok,
        "closure_scope": "LOCAL_OCC1E_ONLY",
        "runtime_consumer_graph_proven": False,
        "enforcement_status": "UNRESOLVED",
        "authorization_created": False,
        "authority_activated": False,
        "execution_performed": False,
        "self_activation": False,
        "occ1f_opened": False,
        "p160_opened": False,
        "p159_final_lock": False,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
    }

def _missing_parent_chain(parent: Path) -> list[Path]:
    missing = []
    cursor = parent
    while not cursor.exists():
        missing.append(cursor)
        if cursor.parent == cursor:
            break
        cursor = cursor.parent
    missing.reverse()
    return missing


def commit(
    root: Path,
    evidence_bridge: Optional[GovernedEvidenceFilesystemBridge] = None,
    evidence_decisions: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    root = Path(root)
    result = evaluate(root)
    if not result.get("occ1e_closed"):
        raise RuntimeError("OCC1E_CLOSE_REJECTED: " + json.dumps(
            {k:v for k,v in result.get("checks", {}).items() if not v}, sort_keys=True
        ))
    out = _paths(root)["output"]
    content = json.dumps(result, indent=2, sort_keys=True) + "\n"

    # Preserve the historical divergence guard before requesting mutation authority.
    if out.exists() and out.read_text(encoding="utf-8") != content:
        raise RuntimeError("OCC1E_EXISTING_CLOSURE_ARTIFACT_DIVERGES")

    if evidence_bridge is None or evidence_decisions is None:
        raise PermissionError("OCC1E persistent closing artifact requires preissued governed evidence-effect authority")
    parent_decisions = evidence_decisions.get("parent_create", [])
    write_decision = evidence_decisions.get("write")
    if not isinstance(parent_decisions, list):
        raise TypeError("OCC1E parent_create decisions must be a list")
    if not isinstance(write_decision, EvidenceEffectDecision):
        raise TypeError("OCC1E write EvidenceEffectDecision required")

    missing_parents = _missing_parent_chain(out.parent)
    if len(parent_decisions) != len(missing_parents):
        raise RuntimeError(
            "OCC1E_PARENT_CREATE_DECISION_CARDINALITY_MISMATCH:%d!=%d"
            % (len(parent_decisions), len(missing_parents))
        )
    if any(not isinstance(d, EvidenceEffectDecision) for d in parent_decisions):
        raise TypeError("OCC1E parent EvidenceEffectDecision required")

    root_path = getattr(getattr(evidence_bridge, "filesystem_context", None), "root_path", None)
    if root_path is None:
        raise RuntimeError("OCC1E filesystem context root_path required")
    root_path = Path(root_path).resolve()

    for parent, decision in zip(missing_parents, parent_decisions):
        try:
            relative_parent = parent.resolve().relative_to(root_path)
        except (OSError, ValueError):
            raise RuntimeError("OCC1E parent outside governed root")
        effect = evidence_bridge.execute_path(
            decision=decision,
            evidence_role="occ1e_closing_artifact_parent",
            slot="occ1e_closing_parent_create",
            operation_id="FS_CREATE_DIR",
            path=relative_parent,
        )
        if effect.get("status") != "EVIDENCE_EFFECT_CONFIRMED":
            raise PermissionError("OCC1E parent creation denied")

    try:
        relative_out = out.resolve().relative_to(root_path)
    except (OSError, ValueError):
        raise RuntimeError("OCC1E closing artifact outside governed root")
    effect = evidence_bridge.execute_path(
        decision=write_decision,
        evidence_role="occ1e_closing_artifact",
        slot="occ1e_closing_write",
        operation_id="FS_WRITE_REPLACE_BYTES",
        path=relative_out,
        payload=content.encode("utf-8"),
    )
    if effect.get("status") != "EVIDENCE_EFFECT_CONFIRMED":
        raise PermissionError("OCC1E closing artifact write denied")

    print("OCC1E_CLOSING_TRANSACTION_COMMITTED_VALID")
    print("transaction_id=" + result["transaction_id"])
    print("OCC1E_CLOSED_LOCAL_ONLY")
    print("OCC1E_UNRESOLVED_RUNTIME_EVIDENCE_PRESERVED")
    print("OCC1F_NOT_OPENED")
    print("P160_NOT_OPENED")
    print("P159_FINAL_LOCK_FALSE")
    return result

if __name__ == "__main__":
    commit(Path.home() / "open-cognitive-ecology")
