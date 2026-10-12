"""
AA3 — Dynamic Graph Constructor.

This module reconstructs G from R for the A* ontological reconstruction
program. It consumes relation candidates produced by AA2 and builds a dynamic
relation graph with nodes, edges, components, cycles, invariants, and stability
metrics.

Scope
-----
AA3 demonstrates R => G. It does not certify the whole foundational chain;
that role is reserved for AA4. It also does not claim consciousness,
subjectivity, qualia, or phenomenology.
"""

from __future__ import annotations

import json
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Set, Tuple


@dataclass(frozen=True)
class DynamicGraphNode:
    """Node extracted from relation endpoints."""

    node_id: str
    label: str
    incoming_degree: int
    outgoing_degree: int
    total_degree: int
    role: str


@dataclass(frozen=True)
class DynamicGraphEdge:
    """Directed edge reconstructed from an AA2 relation candidate."""

    edge_id: str
    source: str
    target: str
    relation_type: str
    weight: float
    basis_relation_id: str
    derivation_rule: str


class DynamicGraphConstructor:
    """AA3 reconstruction of G from R with certification and phenomenology guards."""

    PRIMITIVE = "DYNAMIC_GRAPH_CONSTRUCTOR"
    READY_STATUS = "DYNAMIC_GRAPH_CONSTRUCTOR_READY"
    DEGRADED_STATUS = "DYNAMIC_GRAPH_CONSTRUCTOR_DEGRADED"

    FORBIDDEN_POSITIVE_CLAIMS = (
        "consciousness_proven",
        "phenomenology_proven",
        "subjectivity_proven",
        "qualia_proven",
        "sentience_proven",
        "foundational_reconstruction_validated",
    )

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "foundational_reconstruction"
        self.latest_json_path = self.output_dir / "latest_dynamic_graph_constructor.json"
        self.latest_markdown_path = self.output_dir / "latest_dynamic_graph_constructor.md"
        self.history_path = self.output_dir / "history_dynamic_graph_constructor.jsonl"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _clamp(value: Any) -> float:
        try:
            x = float(value)
        except Exception:
            x = 0.0
        return round(max(0.0, min(1.0, x)), 6)

    @staticmethod
    def _string(value: Any, fallback: str) -> str:
        text = str(value).strip() if value is not None else ""
        return text or fallback

    def _inventory_names(self) -> List[str]:
        path = self.root / "ontology_inventory.txt"
        if not path.exists():
            return []
        return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _catalog_mentions(self) -> Dict[str, bool]:
        path = self.root / "global_module_catalog.txt"
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        candidates = [
            "dynamic_graph_constructor", "relation_genesis_engine",
            "ontology_topology_governance", "ontological_attractor_mapping",
            "topological_pressure_monitor", "attractor_basin",
            "attractor_persistence_analyzer", "cognitive_phase_transitions",
            "critical_transitions", "cognitive_graph.graph",
        ]
        return {name: name in text for name in candidates}

    def _load_relation_context(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        if isinstance(inputs.get("relation_payload"), Mapping):
            return dict(inputs["relation_payload"])
        try:
            from ontology.relation_genesis_engine import RelationGenesisEngine
            return dict(RelationGenesisEngine(root=self.root).step(persist=False))
        except Exception as exc:  # pragma: no cover - diagnostic resilience
            return {
                "available": False,
                "error": repr(exc),
                "symbol": "R",
                "relations": [],
                "metrics": {"relation_genesis_score": 0.0},
            }

    def _normalize_relations(self, relation_payload: Mapping[str, Any], inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
        raw = inputs.get("relations", relation_payload.get("relations", []))
        if raw is None:
            raw = []
        if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
            raw = []
        relations: List[Dict[str, Any]] = []
        for i, item in enumerate(raw):
            if not isinstance(item, Mapping):
                continue
            source = self._string(item.get("source"), f"source_{i}")
            target = self._string(item.get("target"), f"target_{i}")
            strength = self._clamp(item.get("strength", item.get("weight", 0.0)))
            relation_type = self._string(item.get("relation_type", item.get("type")), "unspecified")
            relations.append({
                "relation_id": self._string(item.get("relation_id", item.get("id")), f"R{i+1:04d}"),
                "relation_type": relation_type,
                "source": source,
                "target": target,
                "strength": strength,
                "basis_atom_ids": list(item.get("basis_atom_ids", [])) if isinstance(item.get("basis_atom_ids", []), list) else [],
                "derivation_rule": self._string(item.get("derivation_rule"), "relation_to_graph_edge"),
                "evidence": self._string(item.get("evidence"), "relation_payload"),
            })
        return relations

    def _construct_edges(self, relations: List[Dict[str, Any]]) -> List[DynamicGraphEdge]:
        edges: List[DynamicGraphEdge] = []
        for i, rel in enumerate(relations):
            if rel["source"] == rel["target"] or rel["strength"] <= 0.0:
                continue
            edges.append(DynamicGraphEdge(
                edge_id=f"G_E{i+1:04d}",
                source=rel["source"],
                target=rel["target"],
                relation_type=rel["relation_type"],
                weight=rel["strength"],
                basis_relation_id=rel["relation_id"],
                derivation_rule="R_candidate_to_directed_dynamic_edge",
            ))
        return edges

    def _construct_nodes(self, edges: List[DynamicGraphEdge]) -> List[DynamicGraphNode]:
        incoming: Dict[str, int] = defaultdict(int)
        outgoing: Dict[str, int] = defaultdict(int)
        labels: Set[str] = set()
        for edge in edges:
            labels.add(edge.source)
            labels.add(edge.target)
            outgoing[edge.source] += 1
            incoming[edge.target] += 1
        nodes: List[DynamicGraphNode] = []
        for i, label in enumerate(sorted(labels)):
            in_d = incoming[label]
            out_d = outgoing[label]
            total = in_d + out_d
            if in_d and out_d:
                role = "mediating"
            elif out_d:
                role = "source"
            elif in_d:
                role = "sink"
            else:
                role = "isolated"
            nodes.append(DynamicGraphNode(
                node_id=f"G_N{i+1:04d}",
                label=label,
                incoming_degree=in_d,
                outgoing_degree=out_d,
                total_degree=total,
                role=role,
            ))
        return nodes

    def _adjacency(self, edges: List[DynamicGraphEdge]) -> Dict[str, List[str]]:
        adjacency: Dict[str, List[str]] = defaultdict(list)
        for edge in edges:
            adjacency[edge.source].append(edge.target)
            adjacency.setdefault(edge.target, [])
        return {k: sorted(v) for k, v in adjacency.items()}

    def _components(self, nodes: List[DynamicGraphNode], edges: List[DynamicGraphEdge]) -> List[Dict[str, Any]]:
        undirected: Dict[str, Set[str]] = {n.label: set() for n in nodes}
        for edge in edges:
            undirected.setdefault(edge.source, set()).add(edge.target)
            undirected.setdefault(edge.target, set()).add(edge.source)
        seen: Set[str] = set()
        comps: List[Dict[str, Any]] = []
        for label in sorted(undirected):
            if label in seen:
                continue
            queue: deque[str] = deque([label])
            seen.add(label)
            members: List[str] = []
            while queue:
                x = queue.popleft()
                members.append(x)
                for y in sorted(undirected.get(x, set())):
                    if y not in seen:
                        seen.add(y)
                        queue.append(y)
            comps.append({
                "component_id": f"C{len(comps)+1:03d}",
                "nodes": sorted(members),
                "node_count": len(members),
            })
        return comps

    def _cycle_edges(self, edges: List[DynamicGraphEdge]) -> List[Dict[str, Any]]:
        edge_set = {(e.source, e.target) for e in edges}
        cycles: List[Dict[str, Any]] = []
        recorded: Set[Tuple[str, str]] = set()
        for source, target in sorted(edge_set):
            if (target, source) in edge_set and (target, source) not in recorded:
                cycles.append({
                    "cycle_id": f"CY{len(cycles)+1:03d}",
                    "nodes": [source, target],
                    "cycle_type": "reciprocal_pair",
                })
                recorded.add((source, target))
        return cycles

    def _invariants(self, nodes: List[DynamicGraphNode], edges: List[DynamicGraphEdge], components: List[Dict[str, Any]], cycles: List[Dict[str, Any]]) -> Dict[str, Any]:
        relation_types = sorted({e.relation_type for e in edges})
        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "component_count": len(components),
            "cycle_count": len(cycles),
            "relation_types_preserved": relation_types,
            "no_edge_without_relation_basis": all(bool(e.basis_relation_id) for e in edges),
            "directed_edge_schema_preserved": all(bool(e.source and e.target and e.edge_id) for e in edges),
        }

    def _metrics(self, nodes: List[DynamicGraphNode], edges: List[DynamicGraphEdge], components: List[Dict[str, Any]], cycles: List[Dict[str, Any]]) -> Dict[str, float]:
        node_count = len(nodes)
        edge_count = len(edges)
        if node_count == 0 or edge_count == 0:
            return {
                "node_count": float(node_count),
                "edge_count": float(edge_count),
                "component_count": float(len(components)),
                "cycle_count": float(len(cycles)),
                "graph_density": 0.0,
                "local_stability_score": 0.0,
                "global_stability_score": 0.0,
                "r_to_g_derivation_score": 0.0,
                "dynamic_graph_score": 0.0,
            }
        possible = max(1, node_count * max(1, node_count - 1))
        density = self._clamp(edge_count / possible)
        mean_weight = sum(e.weight for e in edges) / edge_count
        largest_component = max((c["node_count"] for c in components), default=0)
        component_coherence = self._clamp(largest_component / max(1, node_count))
        cycle_bonus = self._clamp(0.5 + min(0.5, len(cycles) / max(1, edge_count)))
        local = self._clamp((mean_weight + density + cycle_bonus) / 3.0)
        global_stability = self._clamp((component_coherence + mean_weight + (1.0 if components else 0.0)) / 3.0)
        derivation = self._clamp(min(1.0, edge_count / max(1, edge_count)))
        score = self._clamp((local + global_stability + derivation) / 3.0)
        return {
            "node_count": float(node_count),
            "edge_count": float(edge_count),
            "component_count": float(len(components)),
            "cycle_count": float(len(cycles)),
            "graph_density": density,
            "local_stability_score": local,
            "global_stability_score": global_stability,
            "r_to_g_derivation_score": derivation,
            "dynamic_graph_score": score,
        }

    def _failure_conditions(self, relations: List[Dict[str, Any]], edges: List[DynamicGraphEdge], forbidden: List[str]) -> List[str]:
        failures: List[str] = []
        if not relations:
            failures.append("no_relation_candidates")
        if relations and not edges:
            failures.append("no_valid_edges_from_relations")
        if forbidden:
            failures.append("forbidden_positive_phenomenal_or_certification_claim")
        return failures

    def _validation_criteria(self) -> List[str]:
        return [
            "AA2 R payload is available or explicit relations are provided",
            "each graph edge is derived from a relation candidate",
            "nodes are extracted only from relation endpoints",
            "components, cycles, invariants, local stability, and global stability are computed",
            "foundational certification is deferred to AA4",
            "no consciousness, subjectivity, qualia, or phenomenology claim is asserted",
        ]

    def _falsification_criteria(self) -> List[str]:
        return [
            "G can be constructed without any R basis",
            "edges exist without source, target, relation type, and basis relation id",
            "AA3 certifies the full foundational reconstruction instead of deferring to AA4",
            "a positive phenomenal or consciousness claim appears before later certification axes",
            "graph construction cannot degrade under empty relation inputs",
        ]

    def _non_redundancy_analysis(self, inventory: List[str], catalog: Dict[str, bool]) -> Dict[str, Any]:
        nearby = [
            "ontology_topology_governance", "ontological_attractor_mapping",
            "topological_pressure_monitor", "attractor_basin",
            "attractor_persistence_analyzer", "cognitive_phase_transitions",
            "critical_transitions",
        ]
        return {
            "target_already_present": "dynamic_graph_constructor" in inventory,
            "nearby_modules_detected": [name for name in nearby if name in inventory or catalog.get(name)],
            "non_redundant_role": "AA3 derives the canonical dynamic graph G from AA2 relation candidates; existing modules analyze topology, attractors, or phase transitions but do not prove R => G inside the A* reconstruction chain.",
            "preferred_action": "create_new_foundational_module",
        }

    def _epistemic_guard(self, forbidden: List[str]) -> Dict[str, Any]:
        return {
            "relation_required": True,
            "graph_derived_from_relation_only": True,
            "certification_deferred_to_AA4": True,
            "phenomenology_undetermined": True,
            "consciousness_not_assumed": True,
            "subjectivity_not_assumed": True,
            "qualia_not_assumed": True,
            "functional_conclusion_only": True,
            "forbidden_positive_claims_detected": forbidden,
        }

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = self.output_dir / f"dynamic_graph_constructor_{stamp}.json"
        md_path = self.output_dir / f"dynamic_graph_constructor_{stamp}.md"
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        json_path.write_text(text, encoding="utf-8")
        self.latest_json_path.write_text(text, encoding="utf-8")
        markdown = self._markdown(result)
        md_path.write_text(markdown, encoding="utf-8")
        self.latest_markdown_path.write_text(markdown, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "latest_json": str(self.latest_json_path),
            "latest_markdown": str(self.latest_markdown_path),
            "history": str(self.history_path),
        }

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# AA3 — Dynamic Graph Constructor",
            "",
            f"Status: {result['dynamic_graph_constructor_status']}",
            f"Symbol: {result['symbol']}",
            "",
            "## Claim",
            "AA3 demonstrates R => G: a dynamic graph is constructed only from relation candidates.",
            "",
            "## Graph summary",
            f"- nodes: {len(result['nodes'])}",
            f"- edges: {len(result['edges'])}",
            f"- components: {len(result['components'])}",
            f"- cycles: {len(result['cycles'])}",
            "",
            "## Invariants",
        ]
        for key, value in result["invariants"].items():
            lines.append(f"- {key}: {value}")
        lines.extend(["", "## Metrics"])
        for key, value in result["metrics"].items():
            lines.append(f"- {key}: {value}")
        lines.extend(["", "## Epistemic guard"])
        guard = result["epistemic_guard"]
        for key in ["certification_deferred_to_AA4", "phenomenology_undetermined", "consciousness_not_assumed", "functional_conclusion_only"]:
            lines.append(f"- {key}: {guard[key]}")
        return "\n".join(lines) + "\n"

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        relation_payload = self._load_relation_context(inputs)
        relations = self._normalize_relations(relation_payload, inputs)
        edges = self._construct_edges(relations)
        nodes = self._construct_nodes(edges)
        adjacency = self._adjacency(edges)
        components = self._components(nodes, edges)
        cycles = self._cycle_edges(edges)
        invariants = self._invariants(nodes, edges, components, cycles)
        forbidden = [claim for claim in self.FORBIDDEN_POSITIVE_CLAIMS if bool(inputs.get("forced_bad_claim", {}).get(claim))]
        failures = self._failure_conditions(relations, edges, forbidden)
        metrics = self._metrics(nodes, edges, components, cycles)
        status = self.READY_STATUS if not failures else self.DEGRADED_STATUS
        inventory = self._inventory_names()
        catalog = self._catalog_mentions()
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "aa_stage": "AA3",
            "symbol": "G",
            "derived_from_symbol": "R",
            "dynamic_graph_constructor_status": status,
            "timestamp_utc": self._now(),
            "relation_available": bool(relations),
            "r_to_g_demonstrated": bool(edges) and not failures,
            "relation_derived": bool(relations),
            "graph_constructed": bool(edges) and not failures,
            "foundational_reconstruction_validated": False,
            "relations_used": relations,
            "nodes": [asdict(n) for n in nodes],
            "edges": [asdict(e) for e in edges],
            "adjacency": adjacency,
            "components": components,
            "cycles": cycles,
            "invariants": invariants,
            "metrics": metrics,
            "validation_criteria": self._validation_criteria(),
            "falsification_criteria": self._falsification_criteria(),
            "failure_conditions": failures,
            "derivation_constraints": {
                "relation_required_before_graph": True,
                "edges_derive_from_relation_candidates": True,
                "nodes_derive_from_relation_endpoints": True,
                "certification_deferred_to_AA4": True,
            },
            "hierarchy": {
                "AA0": "reconstruction_identity_blueprint",
                "AA1": "difference_space_foundation",
                "AA2": "relation_genesis_engine",
                "AA3": "dynamic_graph_constructor",
                "AA4": "foundational_reconstruction_certifier",
            },
            "dependencies": {
                "incoming": [
                    "reconstruction_identity_blueprint",
                    "difference_space_foundation",
                    "relation_genesis_engine",
                    "ontology_topology_governance",
                    "ontological_attractor_mapping",
                    "topological_pressure_monitor",
                    "structural_continuity",
                    "constraint_fields",
                    "constraint_induced_domain",
                ],
                "outgoing": ["foundational_reconstruction_certifier"],
            },
            "public_interfaces": {
                "DynamicGraphConstructor().step(persist=False)": "returns G construction payload without persistence",
                "DynamicGraphConstructor().step(inputs={'relations': [...]}, persist=False)": "constructs graph from explicit R candidates",
                "DynamicGraphConstructor().step(persist=True)": "writes JSON, Markdown, latest files, and JSONL history",
            },
            "data_structures": {
                "DynamicGraphNode": "node_id, label, incoming_degree, outgoing_degree, total_degree, role",
                "DynamicGraphEdge": "edge_id, source, target, relation_type, weight, basis_relation_id, derivation_rule",
            },
            "non_redundancy_analysis": self._non_redundancy_analysis(inventory, catalog),
            "epistemic_guard": self._epistemic_guard(forbidden),
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "inputs_observed": inputs,
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
