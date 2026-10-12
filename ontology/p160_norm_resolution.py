from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Mapping

PRIMITIVE = "p160_norm_resolution"
VERSION = "P160-B-v1.1-defensive"
SCHEMA = "oce.p160b.norm_resolution.v1.1"
APPLICABILITY = ("APPLIES", "DOES_NOT_APPLY", "UNDETERMINED")
COMPLIANCE = ("SATISFIED", "VIOLATED", "UNRESOLVED", "NOT_APPLICABLE")
UNKNOWN_TOKENS = {"", "UNKNOWN", "UNRESOLVED", "UNDETERMINED", "NONE", "CONTESTED"}

FUNCTIONAL_ONLY = {"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
BOUNDARIES = {"norm_created":False,"norm_modified":False,"constitutive_filter_performed":False,"conflict_arbitration_performed":False,"authority_resolved":False,"authority_created":False,"authorization_created":False,"authorization_token_created":False,"execution_performed":False,"p161_opened":False}

def canonical_json(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def canonical_sha256(v: Any) -> str:
    return sha256(canonical_json(v).encode("utf-8")).hexdigest()

def _unknown(v: Any) -> bool:
    return v is None or (isinstance(v, str) and v.strip().upper() in UNKNOWN_TOKENS)

def _conditions(rule: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    c = rule.get("conditions", [])
    return [x for x in c if isinstance(x, Mapping)] if isinstance(c, list) else []

def _lookup(path: str, request: Mapping[str, Any], runtime_context: Mapping[str, Any]) -> Any:
    roots = {"request": request, "runtime_context": runtime_context, "context": runtime_context}
    parts = str(path).split(".")
    cur: Any = roots.get(parts[0], request)
    start = 1 if parts[0] in roots else 0
    for p in parts[start:]:
        if not isinstance(cur, Mapping) or p not in cur:
            return None
        cur = cur[p]
    return cur

def _eval_condition(cond: Mapping[str, Any], request: Mapping[str, Any], runtime_context: Mapping[str, Any]) -> str:
    # Deterministic, deliberately small P160-B evaluator. Unsupported semantics stay UNDETERMINED.
    if cond.get("always_evaluate") is True or str(cond.get("mode", "")).upper() == "ALWAYS_EVALUATE":
        return "TRUE"
    path = cond.get("field") or cond.get("path")
    op = str(cond.get("operator") or cond.get("op") or "").upper()
    if not path or not op:
        return "UNDETERMINED"
    actual = _lookup(str(path), request, runtime_context)
    if _unknown(actual):
        return "UNDETERMINED"
    expected = cond.get("value", cond.get("expected"))
    try:
        if op in {"EQ", "EQUALS", "=="}: return "TRUE" if actual == expected else "FALSE"
        if op in {"NE", "NOT_EQUALS", "!="}: return "TRUE" if actual != expected else "FALSE"
        if op == "IN": return "TRUE" if actual in expected else "FALSE"
        if op in {"CONTAINS", "HAS"}: return "TRUE" if expected in actual else "FALSE"
        if op == "EXISTS": return "TRUE"
    except (TypeError, ValueError):
        return "UNDETERMINED"
    return "UNDETERMINED"

def _constraint_status(value: Any, *, kind: str) -> tuple[str, dict[str, Any]]:
    if value is None:
        return "TRUE", {"kind":kind,"result":"TRUE","reason":"NO_EXPLICIT_CONSTRAINT"}
    if not isinstance(value, Mapping):
        return "UNDETERMINED", {"kind":kind,"result":"UNDETERMINED","reason":"UNSUPPORTED_CONSTRAINT_SHAPE"}
    status = str(value.get("status", "")).strip().upper()
    if not status:
        return "UNDETERMINED", {"kind":kind,"result":"UNDETERMINED","reason":"MISSING_STATUS"}
    unknown = ("UNKNOWN","UNRESOLVED","UNDETERMINED","CONTESTED","SOURCE_ABSENT","UNVERIFIED","INCOMPLETE","TIMEOUT")
    if any(x in status for x in unknown):
        return "UNDETERMINED", {"kind":kind,"result":"UNDETERMINED","status":status}
    if kind == "SCOPE":
        if status in {"OUT_OF_SCOPE","EXCLUDED","DOES_NOT_APPLY"}: return "FALSE", {"kind":kind,"result":"FALSE","status":status}
        if status in {"IN_SCOPE","BOUNDED","VALID","ESTABLISHED","APPLIES"}: return "TRUE", {"kind":kind,"result":"TRUE","status":status}
    if kind == "TEMPORAL":
        if status in {"EXPIRED","NOT_YET_ACTIVE","INACTIVE","OUTSIDE_WINDOW","DOES_NOT_APPLY"}: return "FALSE", {"kind":kind,"result":"FALSE","status":status}
        if status in {"ACTIVE","BOUNDED","VALID","ESTABLISHED","APPLIES"}: return "TRUE", {"kind":kind,"result":"TRUE","status":status}
    return "UNDETERMINED", {"kind":kind,"result":"UNDETERMINED","status":status,"reason":"UNSUPPORTED_STATUS"}

def _evidence_status(rule: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    evidence = rule.get("evidence_status", rule.get("formalization_status"))
    if evidence is None:
        return "TRUE", {"kind":"EVIDENCE","result":"TRUE","reason":"NO_EXPLICIT_EVIDENCE_GATE"}
    status = str(evidence).strip().upper()
    if status in {"VERIFIED","PROVEN","ESTABLISHED","F3"}: return "TRUE", {"kind":"EVIDENCE","result":"TRUE","status":status}
    if status in {"FALSE","REFUTED","INVALID"}: return "FALSE", {"kind":"EVIDENCE","result":"FALSE","status":status}
    return "UNDETERMINED", {"kind":"EVIDENCE","result":"UNDETERMINED","status":status}

def _applicability(rule: Mapping[str, Any], request: Mapping[str, Any], runtime_context: Mapping[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    always = rule.get("always_evaluate") is True or str(rule.get("evaluation_mode", "")).upper() == "ALWAYS_EVALUATE"
    conditions = _conditions(rule)
    trace: list[dict[str, Any]] = []
    results: list[str] = []
    if always:
        trace.append({"kind":"ALWAYS_EVALUATE","result":"TRUE"}); results.append("TRUE")
    elif not conditions:
        trace.append({"kind":"NO_SUPPORTED_APPLICABILITY_PREDICATE","result":"UNDETERMINED"}); results.append("UNDETERMINED")
    for c in conditions:
        r = _eval_condition(c, request, runtime_context)
        trace.append({"condition":deepcopy(dict(c)),"result":r}); results.append(r)
    for value, kind in ((rule.get("scope_constraints"),"SCOPE"),(rule.get("temporal_constraints"),"TEMPORAL")):
        r, tr = _constraint_status(value, kind=kind); trace.append(tr); results.append(r)
    r, tr = _evidence_status(rule); trace.append(tr); results.append(r)
    if "UNDETERMINED" in results: return "UNDETERMINED", trace
    if "FALSE" in results: return "DOES_NOT_APPLY", trace
    return "APPLIES", trace

def _profile_hash(profile: Mapping[str, Any]) -> str:
    return str(profile.get("artifact_hash") or canonical_sha256(profile))

def _snapshot_hash(runtime_context: Mapping[str, Any]) -> str:
    snap = runtime_context.get("constitutional_snapshot", {})
    return str(snap.get("snapshot_semantic_hash") or snap.get("snapshot_hash") or "UNKNOWN") if isinstance(snap, Mapping) else "UNKNOWN"

def _context_fingerprint(runtime_context: Mapping[str, Any]) -> str:
    fp = runtime_context.get("decision_context_fingerprint", {})
    return str(fp.get("fingerprint") or "UNKNOWN") if isinstance(fp, Mapping) else "UNKNOWN"

def resolve_norms(request: Mapping[str, Any], compiled_profile: Mapping[str, Any], runtime_context: Mapping[str, Any]) -> dict[str, Any]:
    if not all(isinstance(x, Mapping) for x in (request, compiled_profile, runtime_context)):
        raise TypeError("request, compiled_profile and runtime_context must be mappings")
    rules = compiled_profile.get("rules")
    if not isinstance(rules, list):
        raise ValueError("COMPILED_PROFILE_RULES_REQUIRED")
    source_map = deepcopy(compiled_profile.get("source_map", {}))
    applicable=[]; non_applicable=[]; undetermined=[]; app_records=[]; trace=[]
    constitutive=[]; human_values=[]; structural=[]; authority=[]; scope=[]; temporal=[]; uncertainty=[]; conflict=[]; review=[]
    for idx, raw in enumerate(rules):
        if not isinstance(raw, Mapping):
            raise ValueError("RULE_NOT_MAPPING")
        rule=deepcopy(dict(raw)); rid=str(rule.get("rule_id") or f"rule-{idx:04d}")
        state, ctrace = _applicability(rule, request, runtime_context)
        record={"rule_id":rid,"applicability":state,"source_norm_ids":deepcopy(rule.get("source_norm_ids",[])),"semantic_fingerprint":rule.get("semantic_fingerprint"),"compliance":"NOT_APPLICABLE" if state=="DOES_NOT_APPLY" else "UNRESOLVED"}
        app_records.append(record)
        (applicable if state=="APPLIES" else non_applicable if state=="DOES_NOT_APPLY" else undetermined).append(rid)
        trace.append({"order":idx,"rule_id":rid,"applicability":state,"condition_trace":ctrace,"source_norm_ids":deepcopy(rule.get("source_norm_ids",[])),"source_map_binding":deepcopy(rule.get("provenance",{}).get("source_map", source_map)) if isinstance(rule.get("provenance",{}), Mapping) else deepcopy(source_map)})
        tags={str(x).upper() for x in rule.get("tags",[]) if isinstance(x,str)}
        cls=str(rule.get("norm_class") or rule.get("class") or rule.get("enforcement_class") or "").upper()
        if rule.get("constitutive") is True or "CONSTITUTIVE" in tags or "CONSTITUTIVE" in cls: constitutive.append(rid)
        if "HUMAN_VALUE" in tags or cls.startswith("H"): human_values.append(rid)
        if "STRUCTURAL" in tags: structural.append(rid)
        if rule.get("authority_requirements"): authority.append({"rule_id":rid,"value":deepcopy(rule.get("authority_requirements"))})
        if rule.get("scope_constraints"): scope.append({"rule_id":rid,"value":deepcopy(rule.get("scope_constraints"))})
        if rule.get("temporal_constraints"): temporal.append({"rule_id":rid,"value":deepcopy(rule.get("temporal_constraints"))})
        if rule.get("uncertainty_semantics"): uncertainty.append({"rule_id":rid,"value":deepcopy(rule.get("uncertainty_semantics"))})
        if rule.get("conflict_hooks"): conflict.append({"rule_id":rid,"value":deepcopy(rule.get("conflict_hooks"))})
        if rule.get("review_requirements"): review.append({"rule_id":rid,"value":deepcopy(rule.get("review_requirements"))})
    bindings={"source_map":source_map,"profile_hash":_profile_hash(compiled_profile),"snapshot_hash":_snapshot_hash(runtime_context),"runtime_context_fingerprint":_context_fingerprint(runtime_context)}
    blockers=[]
    if bindings["snapshot_hash"] in {"UNKNOWN",""}: blockers.append("SNAPSHOT_HASH_UNRESOLVED")
    if bindings["runtime_context_fingerprint"] in {"UNKNOWN",""}: blockers.append("RUNTIME_CONTEXT_FINGERPRINT_UNRESOLVED")
    out={"schema":SCHEMA,"version":VERSION,"norm_context":{"applicable_norms":applicable,"non_applicable_norms":non_applicable,"undetermined_norms":undetermined,"constitutive_constraints":constitutive,"human_values":human_values,"structural_principles":structural,"authority_rules":authority,"scope_rules":scope,"temporal_rules":temporal,"uncertainty_rules":uncertainty,"conflict_hooks":conflict,"review_requirements":review},"normative_applicability":app_records,"norm_resolution_trace":trace,"bindings":bindings,"blockers":blockers,"deterministic_path_primary":True,"model_is_sole_validator":False,"global_numeric_priority_h1_h9_created":False,"undetermined_promoted_to_non_applicable":False,"compliance_domain":list(COMPLIANCE),"applicability_domain":list(APPLICABILITY),**deepcopy(BOUNDARIES),**deepcopy(FUNCTIONAL_ONLY)}
    out["artifact_hash"]=canonical_sha256(out)
    return out

def verify_norm_context(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping): return {"status":"FAIL","reason":"NOT_MAPPING",**BOUNDARIES,**FUNCTIONAL_ONLY}
    x=deepcopy(dict(value)); supplied=x.pop("artifact_hash",None); computed=canonical_sha256(x)
    records=x.get("normative_applicability",[])
    states_ok=isinstance(records,list) and all(r.get("applicability") in APPLICABILITY and r.get("compliance") in COMPLIANCE for r in records if isinstance(r,Mapping))
    checks={"schema":x.get("schema")==SCHEMA,"hash":supplied==computed,"states":states_ok,"no_unknown_laundering":x.get("undetermined_promoted_to_non_applicable") is False,"no_numeric_h_priority":x.get("global_numeric_priority_h1_h9_created") is False,"deterministic_primary":x.get("deterministic_path_primary") is True,"model_not_sole_validator":x.get("model_is_sole_validator") is False,"no_authorization":x.get("authorization_created") is False and x.get("authorization_token_created") is False,"no_execution":x.get("execution_performed") is False,"no_later_stage":x.get("constitutive_filter_performed") is False and x.get("conflict_arbitration_performed") is False and x.get("authority_resolved") is False}
    return {"status":"PASS" if all(checks.values()) else "FAIL","checks":checks,"supplied_artifact_hash":supplied,"computed_artifact_hash":computed,**deepcopy(BOUNDARIES),**deepcopy(FUNCTIONAL_ONLY)}

def manifest() -> dict[str, Any]:
    return {"primitive":PRIMITIVE,"version":VERSION,"schema":SCHEMA,"scope":"P160-B_ONLY","artifacts":["norm_context","normative_applicability","norm_resolution_trace"],"reuses":["occ_compiled_normative_profile","p160_runtime_context_contract"],"boundaries":deepcopy(BOUNDARIES),**deepcopy(FUNCTIONAL_ONLY)}
