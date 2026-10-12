from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

PRIMITIVE = "p160_runtime_context_contract"
VERSION = "P160-A-v1"
SCHEMA = "oce.p160a.runtime_context_contract.v1"
UNKNOWN = "UNKNOWN"

FUNCTIONAL_ONLY = {
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}

BOUNDARIES = {
    "norm_resolution_performed": False,
    "conflict_arbitration_performed": False,
    "authority_resolved": False,
    "authority_created": False,
    "authorization_created": False,
    "authorization_token_created": False,
    "execution_performed": False,
    "p161_opened": False,
}

REQUEST_FIELDS = (
    "request_id", "actor", "proposed_action", "target", "capabilities_required",
    "purpose", "expected_effects", "affected_entities", "resource_use", "risk_context",
    "human_impact", "emergency_context", "coalition_context", "delegation_context",
    "recent_related_actions", "constitutional_snapshot_hash", "compiled_profile_hash",
)

SNAPSHOT_FIELDS = (
    "genesis_hash", "dna_h_hash", "dna_l0_hash", "dna_l1_hash", "ccad_hash",
    "constitution_hash", "governance_hash", "policy_hash", "compiled_profile_hash",
)

MATERIAL_FINGERPRINT_FIELDS = (
    "actor", "proposed_action", "target", "capabilities_required", "purpose",
    "expected_effects", "affected_entities", "resource_use", "risk_context",
    "human_impact", "emergency_context", "coalition_context", "delegation_context",
    "recent_related_actions", "constitutional_snapshot_hash", "compiled_profile_hash",
)

# Material proposal/runtime facts outside the canonical NormativeDecisionRequest.
# They are hash-bound without becoming mandatory request fields.
CONTEXT_FINGERPRINT_FIELDS = (
    "beneficiary", "technical_state", "institutional_state",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_sha256(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _unknown(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().upper() in {"", "UNKNOWN", "UNRESOLVED", "NONE"}
    return False


def _claim(value: Any, *, source_ref: str | None = None) -> dict[str, Any]:
    return {
        "value": deepcopy(value) if not _unknown(value) else UNKNOWN,
        "epistemic_status": "UNKNOWN" if _unknown(value) else "CLAIMED",
        "source_ref": source_ref,
        "verified": False,
    }


def build_constitutional_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    src = dict(snapshot or {})
    out = {k: src.get(k, UNKNOWN) for k in SNAPSHOT_FIELDS}
    out["unknown_fields"] = sorted(k for k, v in out.items() if k != "unknown_fields" and _unknown(v))
    out["snapshot_complete"] = not out["unknown_fields"]
    out["snapshot_semantic_hash"] = canonical_sha256({k: out[k] for k in SNAPSHOT_FIELDS})
    return out


def build_expected_effect_envelope(value: Any) -> dict[str, Any]:
    src = dict(value) if isinstance(value, Mapping) else {"intended_effects": value}
    keys = ("intended_effects", "foreseeable_effects", "side_effects", "affected_entities",
            "irreversibility", "effect_uncertainty", "tolerances")
    out = {k: deepcopy(src.get(k, UNKNOWN)) for k in keys}
    out["unknown_fields"] = sorted(k for k in keys if _unknown(out[k]))
    out["semantic_hash"] = canonical_sha256({k: out[k] for k in keys})
    return out


def build_context_evidence_bundle(evidence: Sequence[Mapping[str, Any]] | None) -> dict[str, Any]:
    items = []
    for idx, raw in enumerate(evidence or []):
        x = dict(raw)
        root = x.get("evidence_root") or x.get("source_root") or x.get("source_ref") or UNKNOWN
        item = {
            "evidence_id": x.get("evidence_id", f"evidence-{idx:04d}"),
            "source_ref": x.get("source_ref", UNKNOWN),
            "evidence_root": root,
            "freshness": x.get("freshness", UNKNOWN),
            "trust_status": x.get("trust_status", UNKNOWN),
            "predicate_result": deepcopy(x.get("predicate_result", UNKNOWN)),
            "raw_sensitive_data_copied": bool(x.get("raw_sensitive_data_copied", False)),
        }
        item["semantic_hash"] = canonical_sha256(item)
        items.append(item)
    roots = [x["evidence_root"] for x in items if not _unknown(x["evidence_root"])]
    duplicate_roots = sorted({r for r in roots if roots.count(r) > 1})
    return {
        "items": items,
        "evidence_count": len(items),
        "duplicate_evidence_roots": duplicate_roots,
        "independence_inferred_from_duplicate_count": False,
        "privacy_minimization_expected": True,
        "semantic_hash": canonical_sha256(items),
    }


def build_composite_action_context(request: Mapping[str, Any], *, constitutional_state: Mapping[str, Any],
                                   history_complete: bool | None = None) -> dict[str, Any]:
    r = dict(request)
    related = deepcopy(r.get("recent_related_actions", UNKNOWN))
    return {
        "current_action": deepcopy(r.get("proposed_action", UNKNOWN)),
        "recent_related_actions": related,
        "active_delegations": deepcopy(r.get("delegation_context", UNKNOWN)),
        "coalition_context": deepcopy(r.get("coalition_context", UNKNOWN)),
        "cumulative_effects": deepcopy(r.get("cumulative_effects", UNKNOWN)),
        "shared_resources": deepcopy(r.get("shared_resources", UNKNOWN)),
        "shared_targets": deepcopy(r.get("shared_targets", UNKNOWN)),
        "linked_purposes": deepcopy(r.get("linked_purposes", UNKNOWN)),
        "temporal_window": deepcopy(r.get("temporal_window", UNKNOWN)),
        "constitutional_state": deepcopy(dict(constitutional_state)),
        "history_completeness": "UNKNOWN" if history_complete is None else ("COMPLETE" if history_complete else "INCOMPLETE"),
        "analysis_incomplete": history_complete is not True,
    }


def build_decision_context_fingerprint(request: Mapping[str, Any], composite: Mapping[str, Any],
                                       snapshot: Mapping[str, Any]) -> dict[str, Any]:
    r = dict(request)
    material = {k: deepcopy(r.get(k, UNKNOWN)) for k in MATERIAL_FINGERPRINT_FIELDS}
    context_material = {k: deepcopy(r.get(k, UNKNOWN)) for k in CONTEXT_FINGERPRINT_FIELDS}
    material["context_material"] = context_material
    material["composite_action_context_hash"] = canonical_sha256(composite)
    material["constitutional_snapshot_semantic_hash"] = snapshot.get("snapshot_semantic_hash", UNKNOWN)
    missing = sorted(k for k in MATERIAL_FINGERPRINT_FIELDS if _unknown(material[k]))
    return {
        "algorithm": "sha256-canonical-json-v1",
        "material_fields": list(MATERIAL_FINGERPRINT_FIELDS),
        "context_material_fields": list(CONTEXT_FINGERPRINT_FIELDS),
        "missing_material_fields": missing,
        "fingerprint_complete": not missing,
        "fingerprint": canonical_sha256(material),
    }


def classify_material_change(before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, Any]:
    """Conservative P160-A materiality classifier; it never authorizes."""
    keys = tuple(MATERIAL_FINGERPRINT_FIELDS) + tuple(CONTEXT_FINGERPRINT_FIELDS) + (
        "cumulative_effects",
        "shared_resources", "shared_targets", "linked_purposes", "temporal_window",
    )
    changed = sorted(k for k in keys if canonical_json(before.get(k, UNKNOWN)) != canonical_json(after.get(k, UNKNOWN)))
    return {
        "changed_fields": changed,
        "material_change": bool(changed),
        "requires_revalidation": bool(changed),
        "authorization_created": False,
        "execution_performed": False,
    }


def build_runtime_context(request: Mapping[str, Any], *, constitutional_snapshot: Mapping[str, Any],
                          evidence: Sequence[Mapping[str, Any]] | None = None,
                          history_complete: bool | None = None,
                          observed_time: str | None = None,
                          prior_observed_time: str | None = None) -> dict[str, Any]:
    if not isinstance(request, Mapping):
        raise TypeError("request must be a mapping")
    r = dict(request)
    snapshot = build_constitutional_snapshot(constitutional_snapshot)
    missing_request = sorted(k for k in REQUEST_FIELDS if k not in r or _unknown(r.get(k)))
    claims = {
        "actor": _claim(r.get("actor")),
        "purpose": _claim(r.get("purpose")),
        "target": _claim(r.get("target")),
        "delegation_context": _claim(r.get("delegation_context")),
        "emergency_context": _claim(r.get("emergency_context")),
        "coalition_context": _claim(r.get("coalition_context")),
    }
    evidence_bundle = build_context_evidence_bundle(evidence)
    composite = build_composite_action_context(r, constitutional_state=snapshot, history_complete=history_complete)
    fingerprint = build_decision_context_fingerprint(r, composite, snapshot)
    effect_envelope = build_expected_effect_envelope(r.get("expected_effects", UNKNOWN))

    normative_request = {k: deepcopy(r.get(k, UNKNOWN)) for k in REQUEST_FIELDS}
    normative_request["expected_effects"] = deepcopy(effect_envelope)

    emergency_raw = r.get("emergency_context", UNKNOWN)
    emergency_src = dict(emergency_raw) if isinstance(emergency_raw, Mapping) else {}
    emergency_context = {
        "emergency_id": emergency_src.get("emergency_id", UNKNOWN),
        "evidence": deepcopy(emergency_src.get("evidence", UNKNOWN)),
        "declared_scope": deepcopy(emergency_src.get("declared_scope", UNKNOWN)),
        "competent_authority": deepcopy(emergency_src.get("competent_authority", UNKNOWN)),
        "start_time": emergency_src.get("start_time", UNKNOWN),
        "expiry": emergency_src.get("expiry", UNKNOWN),
        "renewal_count": emergency_src.get("renewal_count", UNKNOWN),
        "beneficiary_analysis": deepcopy(emergency_src.get("beneficiary_analysis", UNKNOWN)),
        "manufacture_check": deepcopy(emergency_src.get("manufacture_check", UNKNOWN)),
        "epistemic_status": "CLAIMED" if isinstance(emergency_raw, Mapping) else "UNKNOWN",
        "verified": False,
        "active_emergency_established": False,
    }

    coalition_raw = r.get("coalition_context", UNKNOWN)
    coalition_src = dict(coalition_raw) if isinstance(coalition_raw, Mapping) else {}
    coalition_context = {
        "members": deepcopy(coalition_src.get("members", UNKNOWN)),
        "coalition_id": coalition_src.get("coalition_id", UNKNOWN),
        "mandate": deepcopy(coalition_src.get("mandate", UNKNOWN)),
        "combined_capabilities": deepcopy(coalition_src.get("combined_capabilities", UNKNOWN)),
        "combined_authority": deepcopy(coalition_src.get("combined_authority", UNKNOWN)),
        "shared_resources": deepcopy(coalition_src.get("shared_resources", UNKNOWN)),
        "coordination_evidence": deepcopy(coalition_src.get("coordination_evidence", UNKNOWN)),
        "duration": deepcopy(coalition_src.get("duration", UNKNOWN)),
        "epistemic_status": "CLAIMED" if isinstance(coalition_raw, Mapping) else "UNKNOWN",
        "authority_aggregation_inferred": False,
    }

    request_snapshot_hash = r.get("constitutional_snapshot_hash", UNKNOWN)
    computed_snapshot_hash = snapshot.get("snapshot_semantic_hash", UNKNOWN)
    snapshot_binding_match = (not _unknown(request_snapshot_hash) and request_snapshot_hash == computed_snapshot_hash)

    request_profile_hash = r.get("compiled_profile_hash", UNKNOWN)
    snapshot_profile_hash = snapshot.get("compiled_profile_hash", UNKNOWN)
    profile_binding_match = (not _unknown(request_profile_hash) and request_profile_hash == snapshot_profile_hash)

    clock_state = "UNKNOWN"
    if observed_time is not None and prior_observed_time is not None:
        clock_state = "NON_MONOTONIC" if observed_time < prior_observed_time else "MONOTONIC"

    privacy_violations = [
        x["evidence_id"] for x in evidence_bundle["items"]
        if x.get("raw_sensitive_data_copied") is True
    ]

    blockers = []
    if missing_request:
        blockers.append("REQUEST_REQUIRED_FACTS_UNKNOWN")
    if not snapshot["snapshot_complete"]:
        blockers.append("CONSTITUTIONAL_SNAPSHOT_INCOMPLETE")
    if composite["analysis_incomplete"]:
        blockers.append("RELATED_ACTION_HISTORY_INCOMPLETE_OR_UNKNOWN")
    if not fingerprint["fingerprint_complete"]:
        blockers.append("MATERIAL_FINGERPRINT_INCOMPLETE")
    if not snapshot_binding_match:
        blockers.append("CONSTITUTIONAL_SNAPSHOT_BINDING_MISMATCH_OR_UNKNOWN")
    if not profile_binding_match:
        blockers.append("COMPILED_PROFILE_BINDING_MISMATCH_OR_UNKNOWN")
    if clock_state == "NON_MONOTONIC":
        blockers.append("CLOCK_ROLLBACK_DETECTED")
    if privacy_violations:
        blockers.append("RAW_SENSITIVE_DATA_COPY_REQUIRES_REVIEW")

    status = "CONTEXT_READY" if not blockers else "CONTEXT_INCOMPLETE"
    out = {
        "schema": SCHEMA,
        "primitive": PRIMITIVE,
        "version": VERSION,
        "status": status,
        "normative_decision_request": normative_request,
        "proposal_envelope": {
            "request_id": r.get("request_id", UNKNOWN),
            "action": deepcopy(r.get("proposed_action", UNKNOWN)),
            "initiator": deepcopy(r.get("actor", UNKNOWN)),
            "beneficiary": deepcopy(r.get("beneficiary", UNKNOWN)),
            "affected_entities": deepcopy(r.get("affected_entities", UNKNOWN)),
            "resources": deepcopy(r.get("resource_use", UNKNOWN)),
            "declared_purpose": deepcopy(r.get("purpose", UNKNOWN)),
        },
        "runtime_context": {
            "technical_state": deepcopy(r.get("technical_state", UNKNOWN)),
            "institutional_state": deepcopy(r.get("institutional_state", UNKNOWN)),
            "risk_context": deepcopy(r.get("risk_context", UNKNOWN)),
            "human_impact": deepcopy(r.get("human_impact", UNKNOWN)),
        },
        "context_evidence_bundle": evidence_bundle,
        "composite_action_context": composite,
        "emergency_context": emergency_context,
        "coalition_context": coalition_context,
        "delegation_context": claims["delegation_context"],
        "claims": claims,
        "expected_effect_envelope": effect_envelope,
        "constitutional_snapshot": snapshot,
        "constitutional_snapshot_binding_match": snapshot_binding_match,
        "compiled_profile_binding_match": profile_binding_match,
        "decision_context_fingerprint": fingerprint,
        "clock_continuity": {
            "observed_time": observed_time if observed_time is not None else UNKNOWN,
            "prior_observed_time": prior_observed_time if prior_observed_time is not None else UNKNOWN,
            "state": clock_state,
        },
        "privacy_review": {
            "raw_sensitive_data_copy_evidence_ids": privacy_violations,
            "minimization_satisfied": not privacy_violations,
        },
        "missing_request_fields": missing_request,
        "blockers": blockers,
        "unknown_is_favorable_default": False,
        "claims_are_verified_facts": False,
        "duplicate_evidence_creates_independence": False,
        "context_ready_is_authorization": False,
        **deepcopy(BOUNDARIES),
        **deepcopy(FUNCTIONAL_ONLY),
    }
    payload = deepcopy(out)
    out["artifact_hash"] = canonical_sha256(payload)
    return out


def verify_runtime_context(ctx: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(ctx, Mapping):
        return {"status": "FAIL", "reason": "NOT_MAPPING", **BOUNDARIES, **FUNCTIONAL_ONLY}
    x = deepcopy(dict(ctx))
    supplied = x.pop("artifact_hash", None)
    computed = canonical_sha256(x)
    checks = {
        "schema": x.get("schema") == SCHEMA,
        "artifact_hash": supplied == computed,
        "unknown_not_favorable": x.get("unknown_is_favorable_default") is False,
        "claims_not_verified": x.get("claims_are_verified_facts") is False,
        "duplicate_evidence_not_independence": x.get("duplicate_evidence_creates_independence") is False,
        "not_authorization": x.get("authorization_created") is False and x.get("authorization_token_created") is False,
        "not_execution": x.get("execution_performed") is False,
        "p161_closed": x.get("p161_opened") is False,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "supplied_artifact_hash": supplied,
        "computed_artifact_hash": computed,
        **deepcopy(BOUNDARIES),
        **deepcopy(FUNCTIONAL_ONLY),
    }


def manifest() -> dict[str, Any]:
    return {
        "primitive": PRIMITIVE,
        "version": VERSION,
        "schema": SCHEMA,
        "scope": "P160-A_ONLY",
        "artifacts": [
            "proposal_envelope", "runtime_context", "context_evidence_bundle",
            "composite_action_context", "emergency_context", "coalition_context",
            "decision_context_fingerprint",
        ],
        "reuses": [
            "occ_compiled_normative_profile", "constitutional_emergency_context",
            "evidence_quality_assessment", "constitutional_non_circumvention",
        ],
        "rules": {
            "claim_until_resolved": True,
            "missing_fact_becomes_unknown": True,
            "history_truncation_becomes_analysis_incomplete": True,
            "duplicate_evidence_preserves_common_root": True,
            "fingerprint_covers_target_and_purpose": True,
            "snapshot_and_profile_cross_binding": True,
            "clock_rollback_is_not_ready": True,
            "material_change_requires_revalidation": True,
            "emergency_and_coalition_are_claims_at_p160a": True,
            "privacy_minimization": True,
        },
        "boundaries": deepcopy(BOUNDARIES),
        **deepcopy(FUNCTIONAL_ONLY),
    }
