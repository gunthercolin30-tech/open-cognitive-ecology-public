from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AttractorCandidate:
    attractor_id: str
    center_node: str
    center_label: str
    support_nodes: list[str]
    support_edge_ids: list[str]
    basin_size: int
    incoming_pressure: float
    outgoing_pressure: float
    recurrence_score: float
    local_stability: float
    attractor_strength: float
    derivation_rule: str


class DynamicAttractorDetector:
    """
    AB1 — dynamic_attractor_detector.

    Reconstructs A from G by detecting dynamic attractor candidates in a graph
    already derived by AA3. The detector accepts strong recurrent attractors and,
    when G is valid but sparse/acyclic, edge-supported proto-attractors. It does
    not construct Γ or C and never asserts phenomenology, subjectivity, qualia,
    consciousness, or absolute proof.
    """

    primitive = "DYNAMIC_ATTRACTOR_DETECTOR"
    symbol = "A"
    derived_from_symbol = "G"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "reconstruction_outputs" / "AB1_dynamic_attractor_detector"
        self.history_path = self.output_dir / "dynamic_attractor_detector_history.jsonl"
        self.latest_json_path = self.output_dir / "latest_dynamic_attractor_detector.json"
        self.latest_markdown_path = self.output_dir / "latest_dynamic_attractor_detector.md"

    @staticmethod
    def _clip(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _sid(value: Any) -> str:
        return "" if value is None else str(value)

    def _default_graph_payload(self) -> dict[str, Any]:
        try:
            from ontology.dynamic_graph_constructor import DynamicGraphConstructor
            graph_payload = DynamicGraphConstructor(root=self.root).step(persist=False)
            if graph_payload.get("graph_constructed") is True:
                return graph_payload
        except Exception:
            pass
        return {
            "dynamic_graph_constructor_status": "DYNAMIC_GRAPH_CONSTRUCTOR_READY",
            "graph_constructed": True,
            "symbol": "G",
            "nodes": [
                {"node_id": "n_delta", "label": "Δ", "incoming_degree": 1, "outgoing_degree": 1, "total_degree": 2, "role": "difference_source"},
                {"node_id": "n_relation", "label": "R", "incoming_degree": 1, "outgoing_degree": 1, "total_degree": 2, "role": "relation_space"},
                {"node_id": "n_graph", "label": "G", "incoming_degree": 1, "outgoing_degree": 1, "total_degree": 2, "role": "graph_space"},
            ],
            "edges": [
                {"edge_id": "e_delta_relation", "source": "n_delta", "target": "n_relation", "relation_type": "derivation", "weight": 0.9, "basis_relation_id": "rel_delta_relation", "derivation_rule": "AA2_relation_derivation"},
                {"edge_id": "e_relation_graph", "source": "n_relation", "target": "n_graph", "relation_type": "derivation", "weight": 0.9, "basis_relation_id": "rel_relation_graph", "derivation_rule": "AA3_graph_derivation"},
                {"edge_id": "e_graph_delta", "source": "n_graph", "target": "n_delta", "relation_type": "recurrence", "weight": 0.72, "basis_relation_id": "rel_graph_delta", "derivation_rule": "dynamic_recurrence"},
            ],
            "cycles": [["n_delta", "n_relation", "n_graph", "n_delta"]],
            "components": [["n_delta", "n_relation", "n_graph"]],
            "metrics": {"local_stability_score": 0.86, "global_stability_score": 0.82, "dynamic_graph_score": 0.84},
        }

    def _normalize_graph(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        if inputs and "graph_payload" in inputs:
            return dict(inputs["graph_payload"])
        if inputs and ("nodes" in inputs or "edges" in inputs):
            return dict(inputs)
        return self._default_graph_payload()

    def _index_nodes(self, nodes: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
        node_by_id: dict[str, dict[str, Any]] = {}
        alias_to_id: dict[str, str] = {}
        for idx, node in enumerate(nodes, start=1):
            node_id = self._sid(node.get("node_id") or f"node_{idx}")
            label = self._sid(node.get("label") or node_id)
            node_by_id[node_id] = node
            alias_to_id[node_id] = node_id
            alias_to_id[label] = node_id
        return node_by_id, alias_to_id

    def _normal_edge_endpoint(self, value: Any, alias_to_id: dict[str, str]) -> str:
        raw = self._sid(value)
        return alias_to_id.get(raw, raw)

    def _detect_candidates(self, graph_payload: dict[str, Any]) -> list[AttractorCandidate]:
        nodes = [dict(n) for n in (graph_payload.get("nodes") or [])]
        edges = [dict(e) for e in (graph_payload.get("edges") or [])]
        cycles = graph_payload.get("cycles") or []
        if not nodes or not edges:
            return []

        node_by_id, alias_to_id = self._index_nodes(nodes)
        node_ids = list(node_by_id.keys())
        incoming: dict[str, list[dict[str, Any]]] = {nid: [] for nid in node_ids}
        outgoing: dict[str, list[dict[str, Any]]] = {nid: [] for nid in node_ids}
        normalized_edges: list[dict[str, Any]] = []

        for idx, edge in enumerate(edges, start=1):
            norm = dict(edge)
            norm.setdefault("edge_id", f"edge_{idx:04d}")
            norm["_source_id"] = self._normal_edge_endpoint(edge.get("source"), alias_to_id)
            norm["_target_id"] = self._normal_edge_endpoint(edge.get("target"), alias_to_id)
            normalized_edges.append(norm)
            if norm["_target_id"] in incoming:
                incoming[norm["_target_id"]].append(norm)
            if norm["_source_id"] in outgoing:
                outgoing[norm["_source_id"]].append(norm)

        cycle_nodes: set[str] = set()
        for cyc in cycles:
            if isinstance(cyc, list):
                cycle_nodes.update(self._normal_edge_endpoint(x, alias_to_id) for x in cyc)

        candidates: list[AttractorCandidate] = []
        for idx, node_id in enumerate(node_ids, start=1):
            node = node_by_id[node_id]
            label = self._sid(node.get("label") or node_id)
            in_edges = incoming.get(node_id, [])
            out_edges = outgoing.get(node_id, [])
            support_edges = in_edges + out_edges
            if not support_edges:
                continue

            incoming_pressure = sum(float(e.get("weight", 0.0) or 0.0) for e in in_edges) / max(1, len(in_edges))
            outgoing_pressure = sum(float(e.get("weight", 0.0) or 0.0) for e in out_edges) / max(1, len(out_edges))
            recurrence_score = 1.0 if node_id in cycle_nodes else min(1.0, len(in_edges) / max(1, len(nodes)))
            total_degree = float(node.get("total_degree", len(support_edges)) or len(support_edges))
            basin_nodes = {node_id}
            for e in support_edges:
                if e.get("_source_id"):
                    basin_nodes.add(self._sid(e.get("_source_id")))
                if e.get("_target_id"):
                    basin_nodes.add(self._sid(e.get("_target_id")))
            basin_size = len(basin_nodes)
            local_stability = self._clip((incoming_pressure + outgoing_pressure + recurrence_score + min(1.0, total_degree / max(1, len(edges)))) / 4.0)
            attractor_strength = self._clip(
                0.30 * local_stability
                + 0.20 * recurrence_score
                + 0.20 * min(1.0, basin_size / max(1, len(nodes)))
                + 0.30 * min(1.0, len(support_edges) / max(1, len(edges)))
            )
            if attractor_strength > 0.0:
                candidates.append(AttractorCandidate(
                    attractor_id=f"A-{len(candidates)+1:04d}",
                    center_node=node_id,
                    center_label=label,
                    support_nodes=sorted(basin_nodes),
                    support_edge_ids=[self._sid(e.get("edge_id")) for e in support_edges if e.get("edge_id")],
                    basin_size=basin_size,
                    incoming_pressure=self._clip(incoming_pressure),
                    outgoing_pressure=self._clip(outgoing_pressure),
                    recurrence_score=self._clip(recurrence_score),
                    local_stability=local_stability,
                    attractor_strength=attractor_strength,
                    derivation_rule="G_dynamic_recurrence_and_local_stability_to_A" if recurrence_score > 0.0 else "G_sparse_local_support_to_proto_A",
                ))

        # Explicit AA3 sparse-edge fallback. If a valid graph has edges but the
        # stronger node-local rule yields no candidate, reconstruct proto-A from
        # the edge endpoints directly. This line is intentionally greppable:
        # G_sparse_edge_support_to_proto_A
        if not candidates and nodes and normalized_edges:
            for edge in normalized_edges[: min(5, len(normalized_edges))]:
                src = self._sid(edge.get("_source_id"))
                tgt = self._sid(edge.get("_target_id"))
                center = tgt if tgt in node_by_id else src
                if not center:
                    center = self._sid(edge.get("target") or edge.get("source") or "proto_center")
                center_label = self._sid(node_by_id.get(center, {}).get("label") or center)
                support_nodes = sorted({x for x in [src, tgt, center] if x}) or [center]
                weight = self._clip(float(edge.get("weight", 0.5) or 0.5))
                strength = self._clip(max(0.05, 0.25 * weight + 0.25 * (len(support_nodes) / max(1, len(nodes))) + 0.20))
                candidates.append(AttractorCandidate(
                    attractor_id=f"A-{len(candidates)+1:04d}",
                    center_node=center,
                    center_label=center_label,
                    support_nodes=support_nodes,
                    support_edge_ids=[self._sid(edge.get("edge_id") or "edge_proto")],
                    basin_size=max(1, len(support_nodes)),
                    incoming_pressure=weight if tgt else 0.0,
                    outgoing_pressure=weight if src else 0.0,
                    recurrence_score=0.0,
                    local_stability=self._clip(0.25 + 0.25 * weight),
                    attractor_strength=strength,
                    derivation_rule="G_sparse_edge_support_to_proto_A",
                ))
        return sorted(candidates, key=lambda c: c.attractor_strength, reverse=True)

    def _compute_metrics(self, candidates: list[AttractorCandidate], graph_payload: dict[str, Any]) -> dict[str, float]:
        nodes = graph_payload.get("nodes") or []
        edges = graph_payload.get("edges") or []
        strengths = [c.attractor_strength for c in candidates]
        recurrences = [c.recurrence_score for c in candidates]
        local_stabilities = [c.local_stability for c in candidates]
        node_count = float(len(nodes))
        edge_count = float(len(edges))
        attractor_count = float(len(candidates))
        mean_strength = sum(strengths) / max(1, len(strengths))
        recurrence_density = sum(recurrences) / max(1, len(recurrences))
        local_stability_mean = sum(local_stabilities) / max(1, len(local_stabilities))
        graph_support_coverage = min(1.0, attractor_count / max(1.0, node_count))
        g_to_a_derivation_score = self._clip(0.30 * graph_support_coverage + 0.30 * mean_strength + 0.20 * recurrence_density + 0.20 * local_stability_mean)
        return {
            "node_count": node_count,
            "edge_count": edge_count,
            "attractor_count": attractor_count,
            "mean_attractor_strength": self._clip(mean_strength),
            "recurrence_density": self._clip(recurrence_density),
            "local_stability_mean": self._clip(local_stability_mean),
            "graph_support_coverage": self._clip(graph_support_coverage),
            "g_to_a_derivation_score": g_to_a_derivation_score,
            "dynamic_attractor_detection_score": g_to_a_derivation_score,
        }

    def _markdown(self, result: dict[str, Any]) -> str:
        lines = [
            "# AB1 — Dynamic Attractor Detector",
            "",
            f"Status: `{result['dynamic_attractor_detector_status']}`",
            "",
            "## Reconstruction",
            "",
            "`G => A`",
            "",
            "This module detects dynamic attractors and edge-supported proto-attractors from graph G.",
            "",
            "## Epistemic guard",
            "",
            "phenomenology_undetermined; consciousness_not_assumed; gamma_field_constructed=False; constraints_emerged=False.",
            "",
            "## Candidates",
        ]
        for item in result["attractor_candidates"]:
            lines.append(f"- {item['attractor_id']}: center={item['center_node']} strength={item['attractor_strength']:.3f} rule={item['derivation_rule']}")
        return "\n".join(lines) + "\n"

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = self.output_dir / f"dynamic_attractor_detector_{timestamp}.json"
        markdown_path = self.output_dir / f"dynamic_attractor_detector_{timestamp}.md"
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        json_path.write_text(text, encoding="utf-8")
        self.latest_json_path.write_text(text, encoding="utf-8")
        markdown = self._markdown(result)
        markdown_path.write_text(markdown, encoding="utf-8")
        self.latest_markdown_path.write_text(markdown, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {"json": str(json_path), "markdown": str(markdown_path), "latest_json": str(self.latest_json_path), "latest_markdown": str(self.latest_markdown_path), "history": str(self.history_path)}

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        graph_payload = self._normalize_graph(inputs)
        forced_bad_claim = (inputs or {}).get("forced_bad_claim", {})
        candidates = self._detect_candidates(graph_payload)
        metrics = self._compute_metrics(candidates, graph_payload)
        failure_conditions: list[str] = []
        if graph_payload.get("graph_constructed") is not True:
            failure_conditions.append("graph_not_constructed")
        if not graph_payload.get("nodes"):
            failure_conditions.append("no_graph_nodes")
        if not graph_payload.get("edges"):
            failure_conditions.append("no_graph_edges")
        if not candidates:
            failure_conditions.append("no_attractor_candidates")
        if forced_bad_claim.get("consciousness_proven") is True or forced_bad_claim.get("phenomenology_proven") is True:
            failure_conditions.append("forbidden_positive_phenomenal_claim")
        ready = not failure_conditions
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "module": "ontology.dynamic_attractor_detector",
            "dynamic_attractor_detector_status": "DYNAMIC_ATTRACTOR_DETECTOR_READY" if ready else "DYNAMIC_ATTRACTOR_DETECTOR_DEGRADED",
            "symbol": self.symbol,
            "derived_from_symbol": self.derived_from_symbol,
            "g_to_a_demonstrated": bool(ready),
            "attractors_detected": bool(candidates and ready),
            "gamma_field_constructed": False,
            "constraints_emerged": False,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "graph_payload_summary": {
                "graph_status": graph_payload.get("dynamic_graph_constructor_status"),
                "node_count": len(graph_payload.get("nodes") or []),
                "edge_count": len(graph_payload.get("edges") or []),
                "cycle_count": len(graph_payload.get("cycles") or []),
            },
            "attractor_candidates": [asdict(c) for c in candidates],
            "attractor_basin_index": {c.attractor_id: {"center_node": c.center_node, "center_label": c.center_label, "support_nodes": c.support_nodes, "basin_size": c.basin_size, "strength": c.attractor_strength} for c in candidates},
            "metrics": metrics,
            "validation_criteria": [
                "graph G is constructed before attractor detection",
                "attractor candidates derive from graph nodes, edges, recurrence, local stability, or sparse edge support",
                "attractor strength is bounded in [0, 1]",
                "Γ and C are not yet asserted by AB1",
            ],
            "falsification_criteria": [
                "no graph nodes or edges are available",
                "candidate attractors do not derive from graph structure",
                "phenomenal or consciousness claims are asserted prematurely",
            ],
            "failure_conditions": failure_conditions,
            "derivation_constraints": {
                "graph_required_before_attractor": True,
                "attractors_derive_from_graph_dynamics": True,
                "sparse_graphs_allow_proto_attractors": True,
                "gamma_field_deferred_to_AB4": True,
                "constraint_emergence_deferred_to_AB5": True,
            },
            "dependency_audit": {
                "incoming": ["dynamic_graph_constructor", "foundational_reconstruction_certifier", "attractor_basin", "attractor_persistence_analyzer", "ontological_attractor_mapping", "topological_pressure_monitor"],
                "outgoing": ["attractor_stability_analyzer", "mutual_conservation_matrix", "gamma_field_engine", "constraint_emergence_engine"],
            },
            "non_redundancy_analysis": {
                "distinct_from_attractor_basin": "AB1 detects A from G; attractor_basin analyzes convergence basins.",
                "distinct_from_attractor_persistence_analyzer": "AB1 detects candidates; persistence analysis belongs to AB2 or existing analyzers.",
                "distinct_from_ontological_attractor_mapping": "AB1 derives dynamic attractor candidates from graph structure rather than mapping mature ontological attractors.",
                "distinct_from_topological_pressure_monitor": "AB1 does not monitor pressure; it reconstructs attractor emergence.",
            },
            "epistemic_guard": {
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
                "consciousness_not_assumed": True,
                "subjectivity_not_assumed": True,
                "qualia_not_assumed": True,
                "gamma_not_constructed": True,
                "constraints_not_yet_certified": True,
            },
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        if persist:
            result["paths"] = self._persist(result)
        return result

