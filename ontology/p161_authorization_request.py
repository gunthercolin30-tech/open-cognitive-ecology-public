"""P161-A — Authorization Request Contract. Functional-only, non-sovereign."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Mapping

from ontology.p160_normative_decision_sealing import verify_normative_decision

PRIMITIVE = "p161_authorization_request"
VERSION = "P161-A-v1"
SCHEMA = "oce.p161a.authorization_request.v1"
USE_POLICIES = ("SINGLE_USE", "BOUNDED_MULTI_USE", "REVALIDATE_EACH_USE")
BOUNDARIES = {
    "authority_created": False,
    "authorization_created": False,
    "authorization_token_created": False,
    "capability_created": False,
    "execution_performed": False,
    "p162_opened": False,
}
FUNCTIONAL_ONLY = {
    "functional_only": True,
    "phenomenology_undetermined": True,
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
}
UNKNOWN = (None, "", "UNKNOWN", "UNRESOLVED", "INCONCLUSIVE")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_sha256(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _known(value: Any) -> bool:
    return value not in UNKNOWN


def _iso(value: Any):
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        s = value[:-1] + "+00:00" if value.endswith("Z") else value
        d = datetime.fromisoformat(s)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)
    except Exception:
        return None


def _subset(requested: Any, eligible: Any) -> bool:
    """Conservative structural subset: request may narrow, never add/widen."""
    if requested == eligible:
        return True
    if isinstance(requested, Mapping) and isinstance(eligible, Mapping):
        return all(k in eligible and _subset(v, eligible[k]) for k, v in requested.items())
    if isinstance(requested, (list, tuple, set)) and isinstance(eligible, (list, tuple, set)):
        e = list(eligible)
        return all(any(_subset(v, x) for x in e) for v in requested)
    return False


def _action(decision: Mapping[str, Any]) -> Mapping[str, Any]:
    a = decision.get("action_digest", {})
    return a if isinstance(a, Mapping) else {}


def manifest() -> dict:
    return {
        "primitive": PRIMITIVE,
        "version": VERSION,
        "schema": SCHEMA,
        "scope": "P161-A_ONLY",
        "doctrines": [
            "REQUEST!=AUTHORIZATION",
            "REQUEST!=AUTHORITY",
            "REQUEST!=CAPABILITY",
            "REQUEST!=EXECUTION",
            "REQUESTED_SCOPE_SUBSET_OF_P160_ELIGIBLE_SCOPE",
            "NO_IMPLICIT_WILDCARD",
            "NO_SILENT_EXPANSION",
            "UNKNOWN_DOES_NOT_SATISFY_POSITIVE_PRECONDITION",
        ],
        "reuses": [
            "P160-G sealed NormativeDecision identity/hash/action/bindings",
            "P160-A/P160-G runtime context fingerprint",
            "P160-F/P160-G authority context binding",
        ],
        **deepcopy(BOUNDARIES),
        **deepcopy(FUNCTIONAL_ONLY),
    }


def build_authorization_request(*, normative_decision: Mapping[str, Any], requester: str,
                                proposed_executor: str, target: Any, purpose: Any,
                                requested_scope: Any, requested_capabilities: Any,
                                requested_validity: Mapping[str, Any], requested_use_policy: str,
                                approval_evidence_refs=None, authority_context_ref=None,
                                created_at: str) -> dict:
    d = deepcopy(dict(normative_decision or {}))
    errors = []
    verification = verify_normative_decision(d)
    if verification.get("status") != "PASS":
        errors.append("P160_NORMATIVE_DECISION_VERIFICATION_FAILED")
    if d.get("lifecycle") != "SEALED" or d.get("transaction_state") != "COMMITTED":
        errors.append("P160_DECISION_NOT_SEALED_COMMITTED")
    if d.get("normative_eligibility") != "ELIGIBLE_CANDIDATE" or d.get("usable_by_p161") is not True:
        errors.append("P160_DECISION_NOT_ELIGIBLE_FOR_P161")

    action = _action(d)
    if not _known(requester): errors.append("REQUESTER_REQUIRED")
    if not _known(proposed_executor): errors.append("PROPOSED_EXECUTOR_REQUIRED")
    if target != action.get("target"): errors.append("TARGET_MUST_MATCH_P160_ACTION")
    if purpose != action.get("purpose"): errors.append("PURPOSE_MUST_MATCH_P160_ACTION")
    if not _known(target): errors.append("TARGET_UNRESOLVED")
    if not _known(purpose): errors.append("PURPOSE_UNRESOLVED")

    eligible_scope = action.get("scope")
    if not _known(requested_scope): errors.append("REQUESTED_SCOPE_REQUIRED")
    elif not _subset(requested_scope, eligible_scope): errors.append("REQUESTED_SCOPE_WIDENS_P160")
    if "*" in canonical_json(requested_scope): errors.append("WILDCARD_SCOPE_FORBIDDEN")

    eligible_caps = action.get("capabilities")
    if not isinstance(requested_capabilities, (list, tuple)):
        errors.append("REQUESTED_CAPABILITIES_MUST_BE_LIST")
    elif not _subset(list(requested_capabilities), eligible_caps):
        errors.append("REQUESTED_CAPABILITIES_WIDEN_P160")

    validity = deepcopy(dict(requested_validity or {}))
    start = _iso(validity.get("not_before"))
    end = _iso(validity.get("expires_at"))
    if start is None or end is None or end <= start:
        errors.append("REQUESTED_VALIDITY_MUST_BE_BOUNDED")
    if requested_use_policy not in USE_POLICIES:
        errors.append("INVALID_REQUESTED_USE_POLICY")
    if requested_use_policy == "BOUNDED_MULTI_USE":
        uses = validity.get("max_uses")
        if not isinstance(uses, int) or isinstance(uses, bool) or uses < 1:
            errors.append("BOUNDED_MULTI_USE_REQUIRES_POSITIVE_MAX_USES")

    created = _iso(created_at)
    if created is None:
        errors.append("CREATED_AT_INVALID")

    bindings = d.get("bindings", {}) if isinstance(d.get("bindings"), Mapping) else {}
    freshness = d.get("decision_freshness_policy", {}) if isinstance(d.get("decision_freshness_policy"), Mapping) else {}
    state_hashes = freshness.get("required_state_hashes", {}) if isinstance(freshness.get("required_state_hashes"), Mapping) else {}
    authority_ref = authority_context_ref or state_hashes.get("authority_context_fingerprint")
    required_bindings = {
        "normative_decision_id": d.get("decision_id"),
        "normative_decision_hash": d.get("artifact_hash"),
        "action_digest": action.get("semantic_hash"),
        "runtime_context_fingerprint": bindings.get("runtime_context_fingerprint"),
        "constitutional_snapshot_hash": bindings.get("constitutional_snapshot_hash"),
        "compiled_profile_hash": bindings.get("compiled_profile_hash"),
        "authority_context_ref": authority_ref,
    }
    for k, v in required_bindings.items():
        if not _known(v): errors.append("REQUIRED_BINDING_UNRESOLVED:" + k)

    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "requester": requester,
        "proposed_executor": proposed_executor,
        **required_bindings,
        "target": deepcopy(target),
        "purpose": deepcopy(purpose),
        "requested_scope": deepcopy(requested_scope),
        "requested_capabilities": deepcopy(list(requested_capabilities) if isinstance(requested_capabilities, (list, tuple)) else requested_capabilities),
        "requested_validity": validity,
        "requested_use_policy": requested_use_policy,
        "approval_evidence_refs": deepcopy(list(approval_evidence_refs or [])),
        "created_at": created_at,
        "validation_errors": sorted(set(errors)),
        "request_state": "REQUESTED" if not errors else "INVALID_REQUEST",
        "narrowing_rule": "INTERSECTION_NEVER_UNION",
        **deepcopy(BOUNDARIES),
        **deepcopy(FUNCTIONAL_ONLY),
    }
    identity = {k: v for k, v in payload.items() if k not in ("validation_errors", "request_state")}
    request_hash = canonical_sha256(identity)
    payload["request_hash"] = request_hash
    payload["authorization_request_id"] = "AR-" + request_hash[:24]
    return payload


def verify_authorization_request(request: Mapping[str, Any], normative_decision: Mapping[str, Any]) -> dict:
    r = deepcopy(dict(request or {})); d = deepcopy(dict(normative_decision or {}))
    issues = []
    if r.get("schema") != SCHEMA: issues.append("SCHEMA_MISMATCH")
    if r.get("request_state") != "REQUESTED" or r.get("validation_errors"):
        issues.append("REQUEST_NOT_VALID")
    if verify_normative_decision(d).get("status") != "PASS": issues.append("P160_DECISION_INVALID")
    expected = {
        "normative_decision_id": d.get("decision_id"),
        "normative_decision_hash": d.get("artifact_hash"),
        "action_digest": _action(d).get("semantic_hash"),
        "runtime_context_fingerprint": d.get("bindings", {}).get("runtime_context_fingerprint"),
        "constitutional_snapshot_hash": d.get("bindings", {}).get("constitutional_snapshot_hash"),
        "compiled_profile_hash": d.get("bindings", {}).get("compiled_profile_hash"),
    }
    for k, v in expected.items():
        if r.get(k) != v: issues.append("BINDING_MISMATCH:" + k)
    identity = {k: v for k, v in r.items() if k not in ("request_hash", "authorization_request_id", "validation_errors", "request_state")}
    h = canonical_sha256(identity)
    if r.get("request_hash") != h: issues.append("REQUEST_HASH_MISMATCH")
    if r.get("authorization_request_id") != "AR-" + h[:24]: issues.append("REQUEST_ID_MISMATCH")
    if not _subset(r.get("requested_scope"), _action(d).get("scope")): issues.append("SCOPE_NOT_NARROWING")
    if not _subset(r.get("requested_capabilities"), _action(d).get("capabilities")): issues.append("CAPABILITIES_NOT_NARROWING")
    if r.get("target") != _action(d).get("target"): issues.append("TARGET_DRIFT")
    if r.get("purpose") != _action(d).get("purpose"): issues.append("PURPOSE_DRIFT")
    if any(r.get(k) is not False for k in BOUNDARIES): issues.append("SOVEREIGNTY_BOUNDARY_VIOLATION")
    return {"status": "PASS" if not issues else "FAIL", "issues": issues, **deepcopy(BOUNDARIES), **deepcopy(FUNCTIONAL_ONLY)}

# P161_CANONICAL_COMPLETION_AFGH_V1
CANONICAL_REQUEST_CONSTRAINT_FIELDS=("environment","related_requests","break_glass","max_uses","max_resource","max_targets","max_duration","max_concurrent_uses")
def validate_canonical_request_constraints(request):
    c=request.get("constraints",request)
    missing=[k for k in ("environment","related_requests","break_glass") if k not in c]
    if missing:return {"status":"UNKNOWN","reason":"CANONICAL_REQUEST_CONTEXT_MISSING","missing":missing}
    budgets={k:c.get(k) for k in ("max_uses","max_resource","max_targets","max_duration","max_concurrent_uses")}
    for k,v in budgets.items():
        if v is not None and (not isinstance(v,(int,float)) or isinstance(v,bool) or v<0):
            return {"status":"UNSATISFIED","reason":"INVALID_BUDGET","field":k}
    if not isinstance(c["related_requests"],list) or not isinstance(c["break_glass"],bool):
        return {"status":"UNSATISFIED","reason":"REQUEST_CONTEXT_INVALID"}
    return {"status":"SATISFIED","budgets":budgets,"environment":c["environment"],"related_requests":list(c["related_requests"]),"break_glass":c["break_glass"]}
