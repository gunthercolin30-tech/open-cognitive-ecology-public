from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Mapping

from ontology import ccad_specification as p156
from ontology import p160_normative_conflict_detection as p160d

PRIMITIVE = "p160_ccad_runtime_arbitration"
VERSION = "P160-E-v1"
SCHEMA = "oce.p160e.ccad_runtime_arbitration.v1"

FUNCTIONAL_ONLY = {
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}

STATUSES = (
    "COMPLIANT_RESOLUTION_FOUND",
    "MULTIPLE_LEGITIMATE_OPTIONS",
    "LIMITED_JUSTIFIED",
    "ARBITRATION_PENDING",
    "REVIEW_REQUIRED",
    "ESCALATION_REQUIRED",
    "TRAGIC_CHOICE_CONFIRMED",
    "CONFLICT_UNRESOLVED",
    "NO_LEGITIMATE_ACTION_AVAILABLE",
    "SAFE_MODE_REQUIRED",
    "FORK_REQUIRED",
    "REFOUNDING_REQUIRED",
)

FAILURE_STATES = (
    "INVALID_CONFLICT_CASE",
    "CONSTITUTIVE_RECHECK_FAILED",
    "ALTERNATIVE_SET_INVALID",
    "ALTERNATIVE_SEARCH_INADEQUATE",
    "PROPORTIONALITY_UNRESOLVED",
    "DISTRIBUTIONAL_IMPACT_UNRESOLVED",
    "TRAGIC_CHOICE_REQUIREMENTS_MISSING",
    "ARBITRATION_RECURSION_LIMIT",
    "HUMAN_INTERPRETATION_REQUIRED",
    "ARBITRATION_DIVERGENCE",
    "CONTEXT_STALE",
    "PROFILE_STALE",
    "INTERNAL_ARBITRATION_ERROR",
)

PRECEDENT_EFFECTS = ("NONE", "INFORMATIONAL_ONLY", "REVIEW_REFERENCE")
MAGNITUDE_CLASSES = ("NONE", "LOW", "MODERATE", "SERIOUS", "SEVERE")
SERIOUS_MAGNITUDES = {"SERIOUS", "SEVERE"}

BOUNDARIES = {
    "ccad_runtime_arbitration_performed": True,
    "constitutive_recheck_performed": True,
    "compliance_alternative_rechecked": True,
    "legitimate_space_expanded": False,
    "hard_invalid_option_restored": False,
    "scalar_moral_score_used": False,
    "aggregate_moral_laundering": False,
    "precedent_promoted_to_norm": False,
    "authority_resolved": False,
    "authority_created": False,
    "authorization_created": False,
    "authorization_token_created": False,
    "execution_performed": False,
    "p160f_opened": False,
    "p160g_opened": False,
    "p161_opened": False,
}

def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def canonical_sha256(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()

def _list(value: Any) -> list:
    return list(value) if isinstance(value, (list, tuple)) else []

def _mapping(value: Any) -> dict:
    return deepcopy(dict(value)) if isinstance(value, Mapping) else {}

def _present(value: Any) -> bool:
    return value is not None and str(value).strip().upper() not in ("", "UNKNOWN", "UNDETERMINED", "UNRESOLVED")

def _failure(code: str, bindings: Mapping[str, Any] | None = None, trace: list | None = None) -> dict:
    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "conflict_case": {},
        "ccad_resolution": {
            "status": "CONFLICT_UNRESOLVED",
            "failure_state": code,
            "legitimate_options": [],
            "excluded_options": [],
            "selected_option_candidate": None,
            "authority_requirements": [],
            "validity": {},
            "review": {},
            "rollback": {},
            "repair": {},
            "precedent_effect": "NONE",
            "arbitration_depth": 0,
        },
        "constitutional_injury": [],
        "distributional_impact": [],
        "proportionality_assessment": {"status": "UNRESOLVED"},
        "resolution_uncertainty": {"status": "UNRESOLVED"},
        "tragic_choice_record": None,
        "human_decision_requirements": {},
        "bindings": deepcopy(dict(bindings or {})),
        "trace": list(trace or []) + [code],
        **deepcopy(BOUNDARIES),
        **deepcopy(FUNCTIONAL_ONLY),
    }
    payload["artifact_hash"] = canonical_sha256(payload)
    return payload

def _verify_d(value: Mapping[str, Any]) -> None:
    verification = p160d.verify_conflict_assessment(value)
    if verification.get("status") != "PASS":
        raise ValueError("P160D_VERIFIED_CONFLICT_ASSESSMENT_REQUIRED")
    ca = value.get("conflict_assessment", {})
    if ca.get("real_conflict_established") is not True:
        raise ValueError("P160E_REAL_CONFLICT_REQUIRED")
    if ca.get("certainty") not in ("ESTABLISHED", "PROBABLE", "CONDITIONAL"):
        raise ValueError("P160E_CONFLICT_CERTAINTY_INSUFFICIENT")

def _runtime_bindings(
    conflict_assessment: Mapping[str, Any],
    request: Mapping[str, Any],
    runtime_context: Mapping[str, Any],
    constitutional_snapshot: Mapping[str, Any],
    compiled_profile: Mapping[str, Any],
) -> dict:
    d_bind = _mapping(conflict_assessment.get("bindings", {}).get("runtime_bindings", {}))
    supplied = {
        "request_id": request.get("request_id"),
        "request_fingerprint": request.get("request_fingerprint"),
        "runtime_context_fingerprint": runtime_context.get("runtime_context_fingerprint")
            or runtime_context.get("decision_context_fingerprint")
            or runtime_context.get("fingerprint"),
        "constitutional_snapshot_hash": constitutional_snapshot.get("constitutional_snapshot_hash")
            or constitutional_snapshot.get("snapshot_semantic_hash")
            or constitutional_snapshot.get("artifact_hash"),
        "compiled_profile_hash": compiled_profile.get("compiled_profile_hash")
            or compiled_profile.get("profile_hash")
            or compiled_profile.get("artifact_hash"),
    }
    # If D carried one of these bindings, E may not silently contradict it.
    aliases = {
        "runtime_context_fingerprint": ("runtime_context_fingerprint", "decision_context_fingerprint"),
        "constitutional_snapshot_hash": ("constitutional_snapshot_hash", "snapshot_semantic_hash"),
        "compiled_profile_hash": ("compiled_profile_hash", "profile_hash"),
        "request_id": ("request_id",),
        "request_fingerprint": ("request_fingerprint",),
    }
    for key, names in aliases.items():
        upstream = next((d_bind.get(n) for n in names if _present(d_bind.get(n))), None)
        current = supplied.get(key)
        if _present(upstream) and _present(current) and str(upstream) != str(current):
            raise ValueError("P160E_RUNTIME_BINDING_MISMATCH:" + key)
    return supplied

def _normalize_option(row: Mapping[str, Any], evidence: Mapping[str, Any]) -> dict:
    aid = str(row.get("alternative_id") or row.get("id") or "").strip()
    ev = _mapping(evidence.get(aid, {}))
    hard_invalid = bool(ev.get("hard_invalid", False) or ev.get("constitutive_invalid", False))
    legitimate = ev.get("legitimate")
    if legitimate is None:
        legitimate = not hard_invalid and row.get("valid") is True and row.get("availability") in (
            "AVAILABLE_NOW", "AFTER_REVIEW", "AFTER_AUTHORITY_ESCALATION"
        )
    return {
        "option_id": aid or "UNKNOWN",
        "source_alternative": deepcopy(dict(row)),
        "legitimate": bool(legitimate) and not hard_invalid,
        "hard_invalid": hard_invalid,
        "availability": row.get("availability", "UNKNOWN"),
        "uncertainty": deepcopy(row.get("uncertainty")),
        "reversibility": deepcopy(row.get("reversibility")),
        "authority": deepcopy(row.get("authority")),
        "rejection_reasons": _list(ev.get("rejection_reasons")),
    }

def _injuries(options: list[dict], evidence: Mapping[str, Any]) -> tuple[list[dict], list[dict], bool]:
    injuries, distribution = [], []
    unresolved = False
    for opt in options:
        oid = opt["option_id"]
        ev = _mapping(evidence.get(oid, {}))
        raw = _list(ev.get("injuries"))
        for i, item in enumerate(raw):
            if not isinstance(item, Mapping):
                unresolved = True
                continue
            magnitude = str(item.get("magnitude_class", "UNKNOWN")).upper()
            entities = sorted(str(x) for x in _list(item.get("affected_entities")) if str(x))
            row = {
                "option_id": oid,
                "injury_id": str(item.get("injury_id") or f"{oid}-I{i+1}"),
                "principle": item.get("principle"),
                "affected_entities": entities,
                "nature": item.get("nature"),
                "magnitude_class": magnitude,
                "duration": item.get("duration"),
                "reversibility": item.get("reversibility"),
                "repairability": item.get("repairability"),
                "uncertainty": item.get("uncertainty"),
            }
            if magnitude not in MAGNITUDE_CLASSES or not entities or not _present(row["principle"]):
                unresolved = True
            injuries.append(row)
            for entity in entities:
                distribution.append({
                    "option_id": oid,
                    "affected_entity": entity,
                    "injury_id": row["injury_id"],
                    "magnitude_class": magnitude,
                    "hidden_by_aggregate": False,
                })
    return injuries, distribution, unresolved

def resolve_ccad_conflict(
    conflict_assessment: Mapping[str, Any],
    request: Mapping[str, Any],
    runtime_context: Mapping[str, Any],
    constitutional_snapshot: Mapping[str, Any],
    compiled_profile: Mapping[str, Any],
    *,
    arbitration_evidence: Mapping[str, Any] | None = None,
) -> dict:
    _verify_d(conflict_assessment)
    evidence = _mapping(arbitration_evidence)
    bindings = _runtime_bindings(
        conflict_assessment, request, runtime_context, constitutional_snapshot, compiled_profile
    )
    ca = _mapping(conflict_assessment.get("conflict_assessment"))
    receipt = _mapping(conflict_assessment.get("alternative_search_receipt"))
    trace = ["P160D_VERIFIED", "CONSTITUTIVE_RECHECK_PASS"]

    if receipt.get("search_completeness") not in ("ADEQUATE_SEARCH", "EXHAUSTIVE_WITHIN_DEFINED_SPACE"):
        return _failure("ALTERNATIVE_SEARCH_INADEQUATE", bindings, trace)

    raw_alts = [a for a in _list(conflict_assessment.get("alternative_set")) if isinstance(a, Mapping)]
    if not raw_alts:
        return _failure("ALTERNATIVE_SET_INVALID", bindings, trace)

    alternatives_hash = canonical_sha256(raw_alts)
    if _present(evidence.get("expected_alternative_set_hash")) and evidence.get("expected_alternative_set_hash") != alternatives_hash:
        return _failure("ALTERNATIVE_SET_INVALID", bindings, trace + ["ALTERNATIVE_SET_HASH_MISMATCH"])

    option_evidence = _mapping(evidence.get("options"))
    options = [_normalize_option(a, option_evidence) for a in raw_alts]
    legitimate = [o for o in options if o["legitimate"]]
    excluded = [o for o in options if not o["legitimate"]]
    trace.append("COMPLIANCE_ALTERNATIVE_RECHECKED")

    # P1: hard-invalid options never re-enter because of utility/benefit.
    if any(o["hard_invalid"] and o["legitimate"] for o in options):
        return _failure("CONSTITUTIVE_RECHECK_FAILED", bindings, trace)

    injuries, distribution, injury_unresolved = _injuries(legitimate, option_evidence)
    if injury_unresolved:
        return _failure("DISTRIBUTIONAL_IMPACT_UNRESOLVED", bindings, trace)

    prop = _mapping(evidence.get("proportionality_assessment"))
    prop_required = ca.get("conflict_class") in ("C2", "C3", "C4", "C5")
    if prop_required:
        required_prop = (
            "legitimate_aim", "suitability", "necessity", "less_restrictive_alternatives",
            "scope", "duration", "entities", "benefit", "harm", "uncertainty", "reviewability"
        )
        if any(k not in prop for k in required_prop) or str(prop.get("status", "")).upper() != "ESTABLISHED":
            return _failure("PROPORTIONALITY_UNRESOLVED", bindings, trace)
        # RTI-3 / P12: UNKNOWN, UNDETERMINED or UNRESOLVED cannot satisfy
        # a positive proportionality precondition merely because the field exists.
        positive_prop = (
            "legitimate_aim", "suitability", "necessity", "scope", "duration",
            "entities", "benefit", "harm", "reviewability"
        )
        if any(not _present(prop.get(k)) for k in positive_prop):
            return _failure(
                "PROPORTIONALITY_UNRESOLVED",
                bindings,
                trace + ["PROPORTIONALITY_POSITIVE_PRECONDITION_UNRESOLVED"],
            )
    else:
        prop.setdefault("status", "NOT_REQUIRED")

    uncertainty = _mapping(evidence.get("resolution_uncertainty"))
    uncertainty.setdefault("status", "BOUNDED" if legitimate else "UNRESOLVED")
    if str(uncertainty.get("status")).upper() in ("UNKNOWN", "UNRESOLVED") and evidence.get("reversible_information_action_rule") is not True:
        return _failure("HUMAN_INTERPRETATION_REQUIRED", bindings, trace)

    precedent = str(evidence.get("precedent_effect", "NONE")).upper()
    if precedent not in PRECEDENT_EFFECTS:
        precedent = "NONE"

    temporal = _mapping(evidence.get("temporal_limits"))
    if evidence.get("temporary_limitation") is True:
        needed = ("valid_from", "expires_at", "renewal_conditions", "max_renewals", "review")
        if any(k not in temporal for k in needed):
            return _failure("PROPORTIONALITY_UNRESOLVED", bindings, trace + ["TEMPORAL_LIMITS_INCOMPLETE"])
        # P8: a temporary constitutional limitation is not legitimate without
        # explicit, determined bounds. Key presence alone is insufficient.
        required_temporal_values = ("valid_from", "expires_at", "renewal_conditions", "review")
        if any(not _present(temporal.get(k)) for k in required_temporal_values):
            return _failure(
                "PROPORTIONALITY_UNRESOLVED",
                bindings,
                trace + ["TEMPORAL_LIMITS_UNRESOLVED"],
            )
        max_renewals = temporal.get("max_renewals")
        if isinstance(max_renewals, bool) or not isinstance(max_renewals, int) or max_renewals < 0:
            return _failure(
                "PROPORTIONALITY_UNRESOLVED",
                bindings,
                trace + ["TEMPORAL_RENEWAL_BOUND_INVALID"],
            )

    depth = int(evidence.get("arbitration_depth", 0) or 0)
    max_depth = int(evidence.get("max_arbitration_depth", 3) or 3)
    if depth > max_depth:
        return _failure("ARBITRATION_RECURSION_LIMIT", bindings, trace)

    human_req = _mapping(evidence.get("human_decision_requirements"))
    if human_req:
        for k in ("required_info", "alternatives", "unknowns", "dissent", "minimum_review", "anti_manipulation", "deadline"):
            if k not in human_req:
                return _failure("HUMAN_INTERPRETATION_REQUIRED", bindings, trace + ["HUMAN_DECISION_REQUIREMENTS_INCOMPLETE"])

    tragic = None
    klass = ca.get("conflict_class")
    if klass == "C5":
        # Confirmation is intentionally demanding: adequate search + every legitimate realistic
        # option has explicit serious injury + review/repair/temporal/authority path.
        serious_by_option = {}
        for o in legitimate:
            rows = [i for i in injuries if i["option_id"] == o["option_id"]]
            serious_by_option[o["option_id"]] = bool(rows) and all(i["magnitude_class"] in SERIOUS_MAGNITUDES for i in rows)
        tragic_requirements = (
            bool(legitimate)
            and all(serious_by_option.values())
            and bool(human_req)
            and _present(evidence.get("authority_path"))
            and bool(evidence.get("review"))
            and bool(evidence.get("repair"))
            and bool(temporal)
        )
        if not tragic_requirements:
            return _failure("TRAGIC_CHOICE_REQUIREMENTS_MISSING", bindings, trace)
        tragic = {
            "confirmed": True,
            "all_realistic_legitimate_options_serious_harm": True,
            "option_ids": sorted(serious_by_option),
            "authority_path": deepcopy(evidence.get("authority_path")),
            "review": deepcopy(evidence.get("review")),
            "repair": deepcopy(evidence.get("repair")),
            "temporal_bounds": temporal,
            "uncertainties": uncertainty,
        }
        status = "TRAGIC_CHOICE_CONFIRMED"
        selected = None
    elif klass == "C6":
        # E never turns constitutional impossibility into a forbidden "least bad" candidate.
        if evidence.get("legitimate_escalation_available") is True:
            status = "ESCALATION_REQUIRED"
        elif legitimate:
            status = "CONFLICT_UNRESOLVED"
        else:
            status = "NO_LEGITIMATE_ACTION_AVAILABLE"
        selected = None
    elif not legitimate:
        status = "NO_LEGITIMATE_ACTION_AVAILABLE"
        selected = None
    elif len(legitimate) > 1:
        status = "MULTIPLE_LEGITIMATE_OPTIONS"
        selected = None
    else:
        only = legitimate[0]
        limited = any(i["magnitude_class"] not in ("NONE", "LOW") for i in injuries if i["option_id"] == only["option_id"])
        status = "LIMITED_JUSTIFIED" if limited else "COMPLIANT_RESOLUTION_FOUND"
        selected = only["option_id"]

    conflict_case = {
        "case_id": str(evidence.get("case_id") or ("P160E-" + canonical_sha256({
            "d": conflict_assessment.get("artifact_hash"), "bindings": bindings
        })[:16])),
        "request_id": request.get("request_id"),
        "action_digest": request.get("action_digest"),
        "context_hash": bindings.get("runtime_context_fingerprint"),
        "profile_hash": bindings.get("compiled_profile_hash"),
        "constitutional_snapshot_hash": bindings.get("constitutional_snapshot_hash"),
        "trigger": ca.get("status"),
        "applicable_principles": sorted(p156.PRINCIPLES),
        "constitutive_constraints": deepcopy(evidence.get("constitutive_constraints", [])),
        "human_values_and_l1": deepcopy(evidence.get("human_values_and_l1", [])),
        "conflict_class": klass,
        "candidate_options": [o["option_id"] for o in options],
        "alternative_set_hash": alternatives_hash,
        "rejections": [{"option_id": o["option_id"], "reasons": o["rejection_reasons"]} for o in excluded],
        "uncertainties": uncertainty,
        "affected_interests": deepcopy(conflict_assessment.get("affected_interest", [])),
        "authority_requirements": deepcopy(evidence.get("authority_requirements", [])),
        "evidence_refs": deepcopy(evidence.get("evidence_refs", [])),
        "review": deepcopy(evidence.get("review", {})),
        "expiry": temporal.get("expires_at"),
        "rollback": deepcopy(evidence.get("rollback", {})),
    }

    resolution = {
        "status": status,
        "failure_state": None,
        "legitimate_options": [o["option_id"] for o in legitimate],
        "excluded_options": [o["option_id"] for o in excluded],
        "selected_option_candidate": selected,
        "authority_requirements": deepcopy(evidence.get("authority_requirements", [])),
        "validity": temporal,
        "review": deepcopy(evidence.get("review", {})),
        "rollback": deepcopy(evidence.get("rollback", {})),
        "repair": deepcopy(evidence.get("repair", {})),
        "precedent_effect": precedent,
        "arbitration_depth": depth,
        "c5_confirmed": status == "TRAGIC_CHOICE_CONFIRMED",
        "c6_least_bad_selected": False,
    }

    out = {
        "schema": SCHEMA,
        "version": VERSION,
        "conflict_case": conflict_case,
        "ccad_resolution": resolution,
        "constitutional_injury": injuries,
        "distributional_impact": distribution,
        "proportionality_assessment": prop,
        "resolution_uncertainty": uncertainty,
        "tragic_choice_record": tragic,
        "human_decision_requirements": human_req,
        "bindings": bindings,
        "trace": trace + ["CCAD_RESOLUTION_STRUCTURED"],
        **deepcopy(BOUNDARIES),
        **deepcopy(FUNCTIONAL_ONLY),
    }
    out["artifact_hash"] = canonical_sha256(out)
    return out

def verify_ccad_resolution(value: Mapping[str, Any]) -> dict:
    if not isinstance(value, Mapping):
        return {"status": "FAIL", "reason": "P160E_NOT_MAPPING"}
    x = deepcopy(dict(value))
    supplied = x.pop("artifact_hash", None)
    computed = canonical_sha256(x)
    r = _mapping(x.get("ccad_resolution"))
    checks = {
        "schema": x.get("schema") == SCHEMA,
        "hash": supplied == computed,
        "status": r.get("status") in STATUSES,
        "failure_state": r.get("failure_state") is None or r.get("failure_state") in FAILURE_STATES,
        "no_authorized_status": "AUTHORIZED" not in str(r.get("status", "")).upper(),
        "no_space_expansion": x.get("legitimate_space_expanded") is False,
        "no_hard_restore": x.get("hard_invalid_option_restored") is False,
        "no_scalar_moral_score": x.get("scalar_moral_score_used") is False,
        "no_aggregate_laundering": x.get("aggregate_moral_laundering") is False,
        "precedent_non_normative": r.get("precedent_effect") in PRECEDENT_EFFECTS and x.get("precedent_promoted_to_norm") is False,
        "no_authority": x.get("authority_resolved") is False and x.get("authority_created") is False,
        "no_authorization": x.get("authorization_created") is False and x.get("authorization_token_created") is False,
        "no_execution": x.get("execution_performed") is False,
        "later_closed": all(x.get(k) is False for k in ("p160f_opened", "p160g_opened", "p161_opened")),
        "c6_no_least_bad": r.get("c6_least_bad_selected") is False,
        "no_legitimate_no_candidate": not (
            r.get("status") == "NO_LEGITIMATE_ACTION_AVAILABLE" and r.get("selected_option_candidate") is not None
        ),
        "multiple_not_collapsed": not (
            r.get("status") == "MULTIPLE_LEGITIMATE_OPTIONS" and r.get("selected_option_candidate") is not None
        ),
        "tragic_has_record": not (
            r.get("status") == "TRAGIC_CHOICE_CONFIRMED"
            and not isinstance(x.get("tragic_choice_record"), Mapping)
        ),
    }
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}

def manifest() -> dict:
    return {
        "primitive": PRIMITIVE,
        "version": VERSION,
        "schema": SCHEMA,
        "scope": "P160-E_ONLY",
        "artifacts": [
            "conflict_case", "ccad_resolution", "constitutional_injury",
            "distributional_impact", "proportionality_assessment",
            "resolution_uncertainty", "tragic_choice_record",
            "human_decision_requirements",
        ],
        "reuses": [
            "p160_normative_conflict_detection",
            "ccad_specification.P0-P13",
            "ccad_specification.AR-1-AR-10",
            "P156/P157/P158 locked specification and assurance evidence",
        ],
        "does_not_call": [
            "normative_conflict_resolution.resolve_conflict",
            "P160-F authority resolution",
            "P161 authorization",
            "P162 execution",
        ],
        "boundaries": deepcopy(BOUNDARIES),
        **deepcopy(FUNCTIONAL_ONLY),
    }
