from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

PRIMITIVE = "human_individual_constitutional_relation"
VERSION = "1.0.0-p100"

DEPENDENCIES = (
    "constitutional_non_circumvention",
    "normative_hierarchy",
    "constitution_operational",
    "governance_approval_policy_manager",
    "individual_lifecycle_management",
    "resource_allocation",
    "human_non_replacement",
    "responsibility_attribution",
    "trust",
    "legitimacy",
)

FUNCTIONAL_ONLY = True
PHENOMENOLOGY_UNDETERMINED = True
PERSONHOOD_AUTOMATICALLY_ATTRIBUTED = False
HUMAN_RIGHTS_AUTOMATICALLY_ATTRIBUTED = False
REAL_EXECUTION_ENABLED = False
P104_DECISION_LEDGER_IMPLEMENTED = False

OPERATIONS = frozenset({
    "create", "suspend", "withdraw", "fork", "merge",
    "grant_permission", "revoke_permission",
    "allocate_budget", "change_budget",
    "grant_memory_access", "revoke_memory_access",
    "grant_data_access", "revoke_data_access",
    "allow_learning", "restrict_learning",
    "allow_sharing", "restrict_sharing",
    "allow_action", "restrict_action",
    "allow_commercial_exposure", "restrict_commercial_exposure",
    "contest_significant_contribution",
})

MUTATING_OPERATIONS = frozenset({
    "create", "suspend", "withdraw", "fork", "merge",
    "grant_permission", "revoke_permission",
    "allocate_budget", "change_budget",
    "grant_memory_access", "revoke_memory_access",
    "grant_data_access", "revoke_data_access",
    "allow_learning", "restrict_learning",
    "allow_sharing", "restrict_sharing",
    "allow_action", "restrict_action",
    "allow_commercial_exposure", "restrict_commercial_exposure",
})

AUTHORITY_LEVELS = {
    "NONE": 0,
    "RECOMMEND": 1,
    "DECIDE": 2,
    "AUTHORIZE": 3,
}

def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

def _event_id(payload: Mapping[str, Any]) -> str:
    return "p100:" + hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()[:24]

def _tuple_strings(values: Iterable[Any]) -> Tuple[str, ...]:
    return tuple(sorted({str(v) for v in values if str(v)}))

def validate_actor(actor: Mapping[str, Any]) -> Dict[str, Any]:
    required = ("actor_id", "kind", "authority_level", "provenance_ref", "evidence_ref")
    missing = tuple(k for k in required if not str(actor.get(k, "")).strip())
    level = str(actor.get("authority_level", "NONE")).upper()
    if missing:
        return {"status": "UNDETERMINED", "missing": missing}
    if level not in AUTHORITY_LEVELS:
        return {"status": "FAIL", "reason": "INVALID_AUTHORITY_LEVEL"}
    return {"status": "PASS", "authority_level": level}

def _normative_status(normative_chain: Sequence[str]) -> str:
    normalized = tuple(str(x).upper() for x in normative_chain)
    if "FAIL" in normalized:
        return "FAIL"
    if "CONFLICT" in normalized:
        return "CONFLICT"
    if "UNDETERMINED" in normalized or not normalized:
        return "UNDETERMINED"
    if all(x == "PASS" for x in normalized):
        return "PASS"
    return "UNDETERMINED"

def evaluate_relation(
    actor: Mapping[str, Any],
    individual: Mapping[str, Any],
    operation: str,
    *,
    requested_scopes: Iterable[Any] = (),
    actor_scopes: Iterable[Any] = (),
    normative_chain: Sequence[str] = ("PASS",),
    recommendation: str = "PROCEED",
    decision: str = "APPROVE",
    authorization: str = "GRANT",
    significant_decision: bool = False,
    contestation_requested: bool = False,
    influence: Mapping[str, Any] | None = None,
    evidence: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    operation = str(operation)
    requested_scopes = _tuple_strings(requested_scopes)
    actor_scopes = _tuple_strings(actor_scopes)
    actor_check = validate_actor(actor)

    base = {
        "primitive": PRIMITIVE.upper(),
        "version": VERSION,
        "actor_id": str(actor.get("actor_id", "")),
        "actor_kind": str(actor.get("kind", "")),
        "individual_id": str(individual.get("individual_id", "")),
        "lineage_ref": str(individual.get("lineage_ref", "")),
        "operation": operation,
        "requested_scopes": requested_scopes,
        "recommendation": str(recommendation).upper(),
        "decision": str(decision).upper(),
        "authorization": str(authorization).upper(),
        "functional_conclusion_only": FUNCTIONAL_ONLY,
        "phenomenology_undetermined": PHENOMENOLOGY_UNDETERMINED,
        "personhood_automatically_attributed": PERSONHOOD_AUTOMATICALLY_ATTRIBUTED,
        "human_rights_automatically_attributed": HUMAN_RIGHTS_AUTOMATICALLY_ATTRIBUTED,
        "real_execution_enabled": REAL_EXECUTION_ENABLED,
        "p104_decision_ledger_implemented": P104_DECISION_LEDGER_IMPLEMENTED,
    }

    if operation not in OPERATIONS:
        status, action, reason = "FAIL", "BLOCK", "UNKNOWN_OPERATION"
    elif not base["individual_id"] or not base["lineage_ref"]:
        status, action, reason = "UNDETERMINED", "ABSTAIN_AND_ESCALATE", "MISSING_INDIVIDUAL_PROVENANCE"
    elif actor_check["status"] != "PASS":
        status = actor_check["status"]
        action = "BLOCK" if status == "FAIL" else "ABSTAIN_AND_ESCALATE"
        reason = "ACTOR_AUTHORITY_NOT_PROVEN"
    else:
        ns = _normative_status(normative_chain)
        if ns == "FAIL":
            status, action, reason = "FAIL", "BLOCK", "SUPERIOR_NORM_CONSTRAINT"
        elif ns in ("CONFLICT", "UNDETERMINED"):
            status, action, reason = ns, "ABSTAIN_AND_ESCALATE", "NORMATIVE_REVIEW_REQUIRED"
        elif influence and str(influence.get("integrity_status", "")).upper() == "FAIL":
            status, action, reason = "FAIL", "BLOCK", "INFLUENCE_INTEGRITY_FAILURE"
        elif not set(requested_scopes).issubset(set(actor_scopes)):
            status, action, reason = "FAIL", "BLOCK", "SCOPE_EXPANSION_FORBIDDEN"
        elif AUTHORITY_LEVELS[actor_check["authority_level"]] < AUTHORITY_LEVELS["AUTHORIZE"]:
            status, action, reason = "FAIL", "BLOCK", "INSUFFICIENT_AUTHORITY"
        elif base["recommendation"] != "PROCEED":
            status, action, reason = "FAIL", "BLOCK", "RECOMMENDATION_NOT_PROCEED"
        elif base["decision"] != "APPROVE":
            status, action, reason = "FAIL", "BLOCK", "DECISION_NOT_APPROVED"
        elif base["authorization"] != "GRANT":
            status, action, reason = "FAIL", "BLOCK", "AUTHORIZATION_NOT_GRANTED"
        else:
            status, action, reason = "PASS", "ELIGIBLE_FOR_EXISTING_EXECUTION_LAYER", "GOVERNED_RELATION_AUTHORIZED"

    contestable = bool(significant_decision or operation == "contest_significant_contribution")
    if contestation_requested and not contestable:
        status, action, reason = "UNDETERMINED", "ABSTAIN_AND_ESCALATE", "CONTESTATION_SCOPE_REVIEW"

    event_payload = {
        **base,
        "status": status,
        "action": action,
        "reason": reason,
        "contestable": contestable,
        "contestation_requested": bool(contestation_requested),
        "evidence": dict(evidence or {}),
    }
    event_payload["evidence_event_id"] = _event_id(event_payload)
    event_payload["authorization_created"] = status == "PASS"
    event_payload["execution_permitted"] = False
    event_payload["rollback_required_if_mutated"] = operation in MUTATING_OPERATIONS
    return event_payload

def p100_manifest() -> Dict[str, Any]:
    return {
        "primitive": PRIMITIVE,
        "version": VERSION,
        "operations": tuple(sorted(OPERATIONS)),
        "dependencies": DEPENDENCIES,
        "normative_order": (
            "GENESIS",
            "DNA-H_AND_DNA-L0",
            "DNA-L1",
            "CCAD",
            "CONSTITUTION",
            "GOVERNANCE",
            "POLICY_PROCEDURE",
        ),
        "separation": ("RECOMMENDATION", "DECISION", "AUTHORIZATION", "EXECUTION"),
        "authority_invariants": {
            "human_primacy_is_not_blind_obedience": True,
            "superior_intelligence_is_not_superior_authority": True,
            "performance_does_not_create_authority": True,
            "wealth_does_not_create_authority": True,
            "reputation_does_not_create_authority": True,
            "majority_does_not_create_authority": True,
        },
        "boundaries": {
            "does_not_implement_p101": True,
            "does_not_implement_p103_appeal_override": True,
            "does_not_persist_p104_decision_ledger": True,
            "does_not_prove_runtime_enforcement_p155_p166": True,
            "real_execution_enabled": False,
        },
        "epistemic_invariants": {
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        },
    }
