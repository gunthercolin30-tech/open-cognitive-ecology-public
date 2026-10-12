from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

from ontology import normative_hierarchy

PRIMITIVE = "occ_normative_ir"
DESCRIPTION = "P159 OCC-1B declarative bounded non-sovereign Normative Intermediate Representation foundation."
VERSION = "P159-OCC1B-v1-foundation"
SCHEMA_VERSION = "oce.p159.occ1b.nir.v1"
SCOPE = "P159_OCC1B_ONLY"

PASS, FAIL, UNDETERMINED = "PASS", "FAIL", "UNDETERMINED"

NODE_TYPES = (
    "NormNode", "ConditionNode", "EffectNode", "AuthorityNode", "ScopeNode",
    "TemporalNode", "EvidenceNode", "ConflictNode", "ReferenceNode",
    "ProvenanceNode", "UncertaintyNode", "ReviewNode", "ExceptionNode",
    "TransitionNode", "CompositeActionNode", "SequenceConstraintNode",
    "HumanImpactNode", "ProportionalityContext", "SourceMapNode",
)
# The Annex enumerates 18 semantic object names plus the mandatory source-map
# representation. SourceMapNode is the explicit carrier used by this foundation;
# it does not create normative authority.
ANNEX_OBJECT_TYPES = NODE_TYPES[:-1]

EDGE_TYPES = (
    "REQUIRES", "PROHIBITS", "PERMITS", "DERIVES_FROM", "LIMITS",
    "RESERVES_AUTHORITY_TO", "CONFLICTS_WITH", "TRIGGERS", "ESCALATES_TO",
    "EXPIRES_WITH", "REVIEWED_BY", "PROTECTED_BY",
)

CONDITION_STATES = (
    "SATISFIED", "NOT_SATISFIED", "UNKNOWN", "NOT_APPLICABLE", "CONTESTED",
)

CONSTRAINT_OPERATORS = (
    "ALL_OF", "ANY_OF", "NONE_OF", "EXACTLY_ONE", "AT_LEAST_N", "AT_MOST_N",
    "IMPLIES", "REQUIRES", "FORBIDS", "UNTIL", "UNLESS", "WITHIN_SCOPE",
)

EVALUATION_DOMAINS = (
    "STATIC", "COMPILE_TIME", "RUNTIME", "POST_ACTION", "RECOVERY", "HUMAN_REVIEW",
)

COMPOSITIONAL_PRIMITIVES = (
    "NON_AMPLIFICATION", "NON_CIRCUMVENTION", "CONTINUITY_GUARD",
    "PROVENANCE_CHAIN_REQUIRED", "UNCERTAINTY_DOES_NOT_SATISFY",
    "LEGITIMACY_NON_SELF_CREATION",
)

CAPABILITIES = (
    "OBSERVE", "READ", "WRITE", "EXECUTE", "DELEGATE", "CREATE_IDENTITY",
    "MODIFY_MEMORY", "MODIFY_GOVERNANCE", "MODIFY_CONSTITUTION", "SPAWN_AGENT",
    "NETWORK_ACCESS", "RESOURCE_ALLOCATION",
)

FORMALIZATION_LEVELS = ("F0", "F1", "F2", "F3")
NIR_UNSUPPORTED_SEMANTICS = "NIR_UNSUPPORTED_SEMANTICS"

NIRI = {
    "NIRI-1": "every NIR element has source mapping",
    "NIRI-2": "no normative authority is created",
    "NIRI-3": "no silent loss",
    "NIRI-4": "UNKNOWN remains explicit",
    "NIRI-5": "authority and evidence remain distinct",
    "NIRI-6": "no scope widening",
    "NIRI-7": "no temporal weakening",
    "NIRI-8": "hard constraints are not weighted preferences",
    "NIRI-9": "order and layout have no semantics",
    "NIRI-10": "NIR is declarative and non-Turing-complete",
    "NIRI-11": "partial formalization remains explicit",
    "NIRI-12": "immutable and reproducible build",
    "NIRI-13": "sequences and coalitions are representable",
    "NIRI-14": "NIR is not a source of legitimacy",
}

BOUNDARIES = {
    "derived_representation": True,
    "source_text_replaced": False,
    "sovereign": False,
    "declarative": True,
    "turing_complete": False,
    "generated_python_allowed": False,
    "eval_allowed": False,
    "templates_allowed": False,
    "hidden_executable_payload_allowed": False,
    "conflict_arbitration_performed": False,
    "authorization_created": False,
    "authority_activated": False,
    "execution_performed": False,
    "occ1c_opened": False,
    "p160_opened": False,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}

_SCOPE_DIMENSIONS = (
    "subject", "object", "capability", "data", "population", "geographic",
    "temporal", "resource", "purpose",
)
_TEMPORAL_FIELDS = (
    "valid_from", "valid_until", "ttl", "renewal", "cooling_off", "sunset", "review",
)
_AUTHORITY_FIELDS = (
    "authority_type", "source", "scope", "purpose", "duration", "delegability",
    "revocability", "reviewability", "provenance_chain",
)
_FORBIDDEN_EXEC_KEYS = {
    "python", "code", "bytecode", "callable", "lambda", "eval", "exec",
    "shell", "command", "script", "template", "object_tag",
}


def _canonical(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _canonical(value[k]) for k in sorted(value, key=lambda x: str(x))}
    if isinstance(value, (list, tuple)):
        return [_canonical(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError("non_declarative_value:%s" % type(value).__name__)


def canonical_json(value: Any) -> str:
    return json.dumps(_canonical(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _result(status: str, reason: str, **extra: Any) -> Dict[str, Any]:
    result = {
        "primitive": PRIMITIVE,
        "status": status,
        "reason": reason,
        "authorization_created": False,
        "authority_activated": False,
        "execution_performed": False,
        "occ1c_opened": False,
        "p160_opened": False,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
    }
    result.update(deepcopy(extra))
    return result


def _walk(value: Any, path: str = "$") -> Iterable[Tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_s = str(key)
            yield path, key_s, child
            for item in _walk(child, path + "." + key_s):
                yield item
    elif isinstance(value, (list, tuple)):
        for idx, child in enumerate(value):
            for item in _walk(child, "%s[%d]" % (path, idx)):
                yield item


def detect_executable_payload(value: Any) -> Tuple[bool, Tuple[str, ...]]:
    hits = []
    for path, key, child in _walk(value):
        if key.strip().lower() in _FORBIDDEN_EXEC_KEYS:
            hits.append(path + "." + key)
        if callable(child):
            hits.append(path + "." + key + ":callable")
    return bool(hits), tuple(sorted(set(hits)))


def validate_source_map(source_map: Any) -> Dict[str, Any]:
    if not isinstance(source_map, Mapping):
        return _result(FAIL, "SOURCE_MAP_NOT_MAPPING", valid=False)
    required = ("source_id", "source_path", "source_field", "source_sha256")
    missing = tuple(k for k in required if not str(source_map.get(k, "")).strip())
    if missing:
        return _result(FAIL, "SOURCE_MAP_REQUIRED_FIELDS_MISSING", valid=False, missing_fields=missing)
    digest = str(source_map["source_sha256"]).strip().lower()
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        return _result(FAIL, "SOURCE_MAP_SHA256_INVALID", valid=False)
    return _result(PASS, "SOURCE_MAP_VALID", valid=True)


def validate_node(node: Any) -> Dict[str, Any]:
    if not isinstance(node, Mapping):
        return _result(FAIL, "NODE_NOT_MAPPING", valid=False)
    node_id = str(node.get("node_id", "")).strip()
    node_type = str(node.get("node_type", "")).strip()
    if not node_id:
        return _result(FAIL, "NODE_ID_MISSING", valid=False)
    if node_type not in NODE_TYPES:
        return _result(FAIL, "UNKNOWN_NODE_TYPE", valid=False, node_type=node_type)
    executable, hits = detect_executable_payload(node)
    if executable:
        return _result(FAIL, "HIDDEN_EXECUTABLE_PAYLOAD", valid=False, executable_hits=hits)
    if node_type != "SourceMapNode":
        sm = validate_source_map(node.get("source_map"))
        if sm["status"] != PASS:
            return _result(FAIL, "ORPHAN_NORMATIVE_NODE", valid=False, source_map_validation=sm)
    formalization = str(node.get("formalization_level", "F0")).strip().upper()
    if formalization not in FORMALIZATION_LEVELS:
        return _result(FAIL, "UNKNOWN_FORMALIZATION_LEVEL", valid=False)
    if node_type == "ConditionNode":
        state = str(node.get("condition_state", "UNKNOWN")).strip().upper()
        if state not in CONDITION_STATES:
            return _result(FAIL, "UNKNOWN_CONDITION_STATE", valid=False)
    if node_type == "AuthorityNode":
        missing = tuple(k for k in _AUTHORITY_FIELDS if k not in node)
        if missing:
            return _result(FAIL, "AUTHORITY_FIELDS_MISSING", valid=False, missing_fields=missing)
    if node_type == "ScopeNode":
        scope = node.get("dimensions")
        if not isinstance(scope, Mapping):
            return _result(FAIL, "SCOPE_DIMENSIONS_MISSING", valid=False)
        unknown_global = tuple(
            d for d in _SCOPE_DIMENSIONS
            if str(scope.get(d, "")).strip().upper() == "GLOBAL"
            and not bool(node.get("global_scope_explicitly_sourced", False))
        )
        if unknown_global:
            return _result(FAIL, "IMPLICIT_GLOBAL_SCOPE_FORBIDDEN", valid=False, dimensions=unknown_global)
    if node_type == "TemporalNode":
        if not any(k in node for k in _TEMPORAL_FIELDS):
            return _result(FAIL, "TEMPORAL_CONSTRAINTS_MISSING", valid=False)
    if node_type == "EvidenceNode" and bool(node.get("grants_authority", False)):
        return _result(FAIL, "EVIDENCE_MUST_NOT_GRANT_AUTHORITY", valid=False)
    if node_type == "ConflictNode" and bool(node.get("arbitrates_conflict", False)):
        return _result(FAIL, "NIR_CONFLICT_NODE_MUST_NOT_ARBITRATE", valid=False)
    return _result(PASS, "NODE_VALID", valid=True, node_id=node_id, node_type=node_type)


def validate_edge(edge: Any, node_ids: Sequence[str]) -> Dict[str, Any]:
    if not isinstance(edge, Mapping):
        return _result(FAIL, "EDGE_NOT_MAPPING", valid=False)
    edge_type = str(edge.get("edge_type", "")).strip().upper()
    if edge_type not in EDGE_TYPES:
        return _result(FAIL, "UNKNOWN_EDGE_TYPE", valid=False, edge_type=edge_type)
    source = str(edge.get("source", "")).strip()
    target = str(edge.get("target", "")).strip()
    known = set(node_ids)
    if not source or not target or source not in known or target not in known:
        return _result(FAIL, "BROKEN_EDGE_REFERENCE", valid=False, source=source, target=target)
    return _result(PASS, "EDGE_VALID", valid=True)


def validate_constraint_expression(expr: Any, depth: int = 0) -> Dict[str, Any]:
    if depth > 32:
        return _result(FAIL, "UNBOUNDED_CONSTRAINT_RECURSION", valid=False)
    if not isinstance(expr, Mapping):
        return _result(FAIL, "CONSTRAINT_NOT_MAPPING", valid=False)
    op = str(expr.get("operator", "")).strip().upper()
    if op not in CONSTRAINT_OPERATORS:
        return _result(FAIL, "UNKNOWN_CONSTRAINT_OPERATOR", valid=False, operator=op)
    operands = expr.get("operands", ())
    if not isinstance(operands, (list, tuple)) or not operands:
        return _result(FAIL, "CONSTRAINT_OPERANDS_MISSING", valid=False)
    for operand in operands:
        if isinstance(operand, Mapping) and "operator" in operand:
            child = validate_constraint_expression(operand, depth + 1)
            if child["status"] != PASS:
                return child
    if op in ("AT_LEAST_N", "AT_MOST_N"):
        n = expr.get("n")
        if not isinstance(n, int) or n < 0 or n > len(operands):
            return _result(FAIL, "CONSTRAINT_N_INVALID", valid=False)
    return _result(PASS, "CONSTRAINT_VALID", valid=True)


def validate_graph(graph: Any) -> Dict[str, Any]:
    if not isinstance(graph, Mapping):
        return _result(FAIL, "GRAPH_NOT_MAPPING", valid=False)
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    metadata = graph.get("metadata")
    source_map = graph.get("source_map")
    if not isinstance(nodes, (list, tuple)) or not isinstance(edges, (list, tuple)):
        return _result(FAIL, "GRAPH_NODES_OR_EDGES_INVALID", valid=False)
    if not isinstance(metadata, Mapping) or not isinstance(source_map, Mapping):
        return _result(FAIL, "GRAPH_METADATA_OR_SOURCE_MAP_INVALID", valid=False)
    node_results = [validate_node(n) for n in nodes]
    if any(r["status"] != PASS for r in node_results):
        return _result(FAIL, "GRAPH_NODE_VALIDATION_FAILED", valid=False, node_results=node_results)
    ids = [r["node_id"] for r in node_results]
    if len(ids) != len(set(ids)):
        return _result(FAIL, "DUPLICATE_NODE_ID", valid=False)
    edge_results = [validate_edge(e, ids) for e in edges]
    if any(r["status"] != PASS for r in edge_results):
        return _result(FAIL, "GRAPH_EDGE_VALIDATION_FAILED", valid=False, edge_results=edge_results)
    executable, hits = detect_executable_payload(graph)
    if executable:
        return _result(FAIL, "HIDDEN_EXECUTABLE_PAYLOAD", valid=False, executable_hits=hits)
    return _result(
        PASS, "NIR_GRAPH_STRUCTURALLY_VALID", valid=True,
        node_count=len(nodes), edge_count=len(edges),
        graph_sha256=canonical_sha256(graph),
    )


def validate_foundation_contract() -> Dict[str, Any]:
    hierarchy = normative_hierarchy.validate_hierarchy()
    checks = {
        "annex_object_types_present": len(ANNEX_OBJECT_TYPES) == 18,
        "source_map_representation_present": "SourceMapNode" in NODE_TYPES,
        "edge_types_12": len(EDGE_TYPES) == 12,
        "condition_states_preserve_unknown": "UNKNOWN" in CONDITION_STATES,
        "constraint_algebra_bounded": len(CONSTRAINT_OPERATORS) == 12,
        "evaluation_domains_6": len(EVALUATION_DOMAINS) == 6,
        "capabilities_12": len(CAPABILITIES) == 12,
        "formalization_levels_explicit": FORMALIZATION_LEVELS == ("F0", "F1", "F2", "F3"),
        "niri_14": len(NIRI) == 14,
        "hierarchy_reuse_valid": hierarchy.get("status") == PASS,
        "non_sovereign": BOUNDARIES["sovereign"] is False,
        "non_turing_complete": BOUNDARIES["turing_complete"] is False,
        "non_executable": BOUNDARIES["execution_performed"] is False,
        "no_downstream_opening": not BOUNDARIES["occ1c_opened"] and not BOUNDARIES["p160_opened"],
    }
    ok = all(checks.values())
    return _result(
        PASS if ok else FAIL,
        "OCC1B_NIR_FOUNDATION_OK" if ok else "OCC1B_NIR_FOUNDATION_INVALID",
        valid=ok, checks=checks, check_count=len(checks),
        passed_count=sum(1 for v in checks.values() if v),
        hierarchy_reuse=hierarchy,
    )


def manifest() -> Dict[str, Any]:
    return deepcopy({
        "primitive": PRIMITIVE,
        "description": DESCRIPTION,
        "version": VERSION,
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "node_types": NODE_TYPES,
        "annex_object_types": ANNEX_OBJECT_TYPES,
        "edge_types": EDGE_TYPES,
        "condition_states": CONDITION_STATES,
        "constraint_operators": CONSTRAINT_OPERATORS,
        "evaluation_domains": EVALUATION_DOMAINS,
        "compositional_primitives": COMPOSITIONAL_PRIMITIVES,
        "capabilities": CAPABILITIES,
        "formalization_levels": FORMALIZATION_LEVELS,
        "niri": NIRI,
        "boundaries": BOUNDARIES,
        "reuses": ("normative_hierarchy",),
        "conflict_resolution_interface": "represent_conflict_and_CCAd_hooks_only_no_arbitration",
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
    })
