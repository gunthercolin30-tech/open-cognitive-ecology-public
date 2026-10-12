\
"""AY1 — governed construction of theoretical dependency graphs.

Consumes an AY0 TheoryGraph and explicit or candidate relation records. Only
explicit relations are placed in the validated dependency layer. Candidate
relations remain segregated and can never be promoted automatically.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

PRIMITIVE = "THEORY_DEPENDENCY_GRAPH"
STATUS_READY = "THEORY_DEPENDENCY_GRAPH_READY"
STATUS_DEGRADED = "THEORY_DEPENDENCY_GRAPH_DEGRADED"
PUBLIC_SCHEMA_VERSION = "1.0.0"
ALLOWED_RELATIONS = {"supports", "requires", "extends", "generalizes", "specializes", "contradicts"}
ALLOWED_STATUSES = {"validated", "candidate"}


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _norm(value: Any) -> str:
    return unicodedata.normalize("NFC", str(value or "")).strip()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clamp_confidence(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("confidence must be numeric") from exc
    if not math.isfinite(number) or not 0.0 <= number <= 1.0:
        raise ValueError("confidence must be finite and between 0 and 1")
    return round(number, 12)


def _atomic_write(path: Path, content: str, filesystem_effect_context: Any, slot_prefix: str) -> None:
    if filesystem_effect_context is None:
        raise RuntimeError("governed filesystem effect context required")
    if not path.parent.exists():
        filesystem_effect_context.execute_path(slot_prefix + ":create_parent", "FS_CREATE_DIR", path.parent)
    filesystem_effect_context.execute_path(slot_prefix + ":write_replace", "FS_WRITE_REPLACE_BYTES", path, payload=content.encode("utf-8"))


def _normalize_graph(graph: Mapping[str, Any]) -> tuple[list[dict[str, Any]], str]:
    nodes = graph.get("nodes", [])
    if not isinstance(nodes, list) or not all(isinstance(node, Mapping) for node in nodes):
        raise TypeError("theory_graph.nodes must be a list of mappings")
    normalized: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(nodes):
        node = dict(raw)
        node_id = _norm(node.get("id"))
        if not node_id:
            raise ValueError(f"node {index} has no id")
        if node_id in normalized and _canonical(normalized[node_id]) != _canonical(node):
            raise ValueError(f"conflicting duplicate node id: {node_id}")
        node["id"] = node_id
        normalized[node_id] = node
    return [normalized[key] for key in sorted(normalized)], _norm(graph.get("schema_version")) or "unknown"


def _normalize_relation(raw: Mapping[str, Any], index: int, node_ids: set[str]) -> dict[str, Any]:
    source = _norm(raw.get("source"))
    target = _norm(raw.get("target"))
    relation = _norm(raw.get("relation") or raw.get("type")).lower()
    status = _norm(raw.get("status") or "candidate").lower()
    if not source or not target:
        raise ValueError(f"relation {index} requires source and target")
    if source == target:
        raise ValueError(f"self dependency is forbidden: {source}")
    if source not in node_ids or target not in node_ids:
        raise ValueError(f"relation {index} references unknown node")
    if relation not in ALLOWED_RELATIONS:
        raise ValueError(f"unsupported relation at index {index}: {relation!r}")
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"unsupported status at index {index}: {status!r}")
    confidence = _clamp_confidence(raw.get("confidence", 1.0 if status == "validated" else 0.5))
    evidence = raw.get("evidence", [])
    if isinstance(evidence, str):
        evidence = [evidence]
    if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
        raise TypeError(f"relation {index} evidence must be a string or list of strings")
    evidence = sorted({_norm(item) for item in evidence if _norm(item)})
    if status == "validated" and not evidence:
        raise ValueError(f"validated relation {index} requires evidence")
    identity = {"source": source, "target": target, "relation": relation, "status": status, "evidence": evidence}
    return {
        "id": _norm(raw.get("id")) or f"edge:{_sha256(identity)[:24]}",
        "source": source,
        "target": target,
        "relation": relation,
        "status": status,
        "confidence": confidence,
        "evidence": evidence,
        "provenance": _norm(raw.get("provenance")) or "structured_input",
    }


def _deduplicate_edges(edges: Iterable[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    kept: dict[str, dict[str, Any]] = {}
    duplicates: list[dict[str, Any]] = []
    semantic: dict[tuple[str, str, str, str], str] = {}
    for raw in edges:
        edge = dict(raw)
        edge_id = edge["id"]
        key = (edge["source"], edge["target"], edge["relation"], edge["status"])
        if edge_id in kept:
            if _canonical(kept[edge_id]) != _canonical(edge):
                raise ValueError(f"conflicting duplicate edge id: {edge_id}")
            duplicates.append({"id": edge_id, "reason": "exact_duplicate_id"})
            continue
        if key in semantic:
            raise ValueError(f"semantic duplicate edge conflicts with {semantic[key]}")
        kept[edge_id] = edge
        semantic[key] = edge_id
    return [kept[key] for key in sorted(kept)], duplicates


def _degrees(node_ids: Iterable[str], edges: Iterable[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    result = {node_id: {"incoming": 0, "outgoing": 0, "total": 0} for node_id in node_ids}
    for edge in edges:
        result[edge["source"]]["outgoing"] += 1
        result[edge["target"]]["incoming"] += 1
    for values in result.values():
        values["total"] = values["incoming"] + values["outgoing"]
    return result


def _has_cycle(node_ids: Iterable[str], edges: Iterable[Mapping[str, Any]]) -> bool:
    adjacency = {node_id: [] for node_id in node_ids}
    indegree = {node_id: 0 for node_id in node_ids}
    for edge in edges:
        adjacency[edge["source"]].append(edge["target"])
        indegree[edge["target"]] += 1
    queue = sorted(node_id for node_id, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        current = queue.pop(0)
        visited += 1
        for target in sorted(adjacency[current]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
                queue.sort()
    return visited != len(indegree)


@dataclass
class TheoryDependencyGraph:
    root: Path | None = None

    def __post_init__(self) -> None:
        self.root = Path(self.root) if self.root is not None else Path.home() / "open-cognitive-ecology"

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False, filesystem_effect_context: Any = None) -> dict[str, Any]:
        supplied = dict(inputs or {})
        graph = supplied.get("theory_graph", {})
        if not isinstance(graph, Mapping):
            raise TypeError("theory_graph must be a mapping")
        nodes, input_schema = _normalize_graph(graph)
        node_ids = {node["id"] for node in nodes}
        records = supplied.get("relations", [])
        if not isinstance(records, list) or not all(isinstance(item, Mapping) for item in records):
            raise TypeError("relations must be a list of mappings")
        normalized = [_normalize_relation(record, index, node_ids) for index, record in enumerate(records)]
        edges, duplicates = _deduplicate_edges(normalized)
        validated_edges = [edge for edge in edges if edge["status"] == "validated"]
        candidate_edges = [edge for edge in edges if edge["status"] == "candidate"]
        relation_counts = {relation: 0 for relation in sorted(ALLOWED_RELATIONS)}
        for edge in validated_edges:
            relation_counts[edge["relation"]] += 1
        degraded_reasons: list[str] = []
        if not nodes:
            degraded_reasons.append("empty_input_theory_graph")
        if not validated_edges:
            degraded_reasons.append("no_validated_dependencies")
        status = STATUS_READY if not degraded_reasons else STATUS_DEGRADED
        graph_core = {
            "schema_version": PUBLIC_SCHEMA_VERSION,
            "input_theory_graph_schema_version": input_schema,
            "nodes": nodes,
            "validated_edges": validated_edges,
            "candidate_edges": candidate_edges,
            "relation_counts": relation_counts,
            "degrees": _degrees(sorted(node_ids), validated_edges),
            "validated_cycle_detected": _has_cycle(sorted(node_ids), validated_edges),
            "duplicate_records": duplicates,
            "candidate_auto_promotion": False,
        }
        dependency_hash = _sha256(graph_core)
        result = {
            "primitive": PRIMITIVE,
            "status": status,
            "dependency_graph_ready": status == STATUS_READY,
            "theory_dependency_graph": graph_core,
            "theory_dependency_graph_hash": dependency_hash,
            "node_count": len(nodes),
            "validated_edge_count": len(validated_edges),
            "candidate_edge_count": len(candidate_edges),
            "degraded_reasons": degraded_reasons,
            "persisted": False,
            "output_path": str(self.root / "theory_evolution" / "ay1" / "theory_dependency_graph.json"),
            "timestamp_utc": supplied.get("timestamp_utc") or _utc_now(),
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }
        if persist:
            payload = dict(result)
            payload["persisted"] = True
            _atomic_write(Path(result["output_path"]), json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", filesystem_effect_context, "theory_dependency_graph")
            result["persisted"] = True
        return result
