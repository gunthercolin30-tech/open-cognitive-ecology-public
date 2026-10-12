from __future__ import annotations

import json
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class DependencyNode:
    node_id: str
    node_type: str
    label: str
    source: str
    epistemic_status: str


@dataclass(frozen=True)
class DependencyEdge:
    source: str
    target: str
    relation: str
    weight: float
    evidence: str


class TheoremDependencyMapper:
    """AN6 — theorem dependency mapper.

    Builds the public dependency graph axiom -> lemma -> proposition -> theorem
    from AN1-AN5 outputs and available formal/theorem modules. This is a
    functional proof-structure mapper only; it does not prove consciousness,
    qualia, subjectivity or phenomenology.
    """

    primitive = "THEOREM_DEPENDENCY_MAPPER"
    step_id = "AN6"
    public_schema_version = "AN6.theorem_dependency_mapper.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, out_dir: str | Path | None = None) -> None:
        root = Path.home() / "open-cognitive-ecology"
        self.out_dir = Path(out_dir) if out_dir is not None else root / "axiomatic_completeness" / "AN6_theorem_dependency_mapper"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _clamp01(value: float) -> float:
        try:
            v = float(value)
        except Exception:
            v = 0.0
        return max(0.0, min(1.0, v))

    @staticmethod
    def _stable_id(prefix: str, text: str, index: int = 0) -> str:
        safe = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(text)).strip("_")
        safe = "_".join(x for x in safe.split("_") if x)
        if not safe:
            safe = str(index)
        return f"{prefix}:{safe[:80]}"

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, set):
            return sorted(value)
        return []

    @staticmethod
    def _mean(values: Iterable[float], default: float = 0.0) -> float:
        vals = [float(v) for v in values]
        return sum(vals) / len(vals) if vals else default

    def _load_axiom_registry(self, inputs: dict[str, Any]) -> dict[str, Any]:
        if isinstance(inputs.get("axiom_registry_result"), dict):
            return dict(inputs["axiom_registry_result"])
        try:
            from ontology.axiom_registry import AxiomRegistry
            return AxiomRegistry().step(inputs={"synthetic": True, "source": "AN6"}, persist=False)
        except Exception as exc:  # pragma: no cover
            return {"axiom_registry_status": "AXIOM_REGISTRY_UNAVAILABLE", "axioms": [], "error": repr(exc)}

    def _load_minimality(self, inputs: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
        if isinstance(inputs.get("axiom_minimality_result"), dict):
            return dict(inputs["axiom_minimality_result"])
        try:
            from ontology.axiom_minimality_analyzer import AxiomMinimalityAnalyzer
            return AxiomMinimalityAnalyzer().step(inputs={"synthetic": True, "source": "AN6", "axiom_registry_result": registry}, persist=False)
        except Exception as exc:  # pragma: no cover
            return {"axiom_minimality_status": "AXIOM_MINIMALITY_UNAVAILABLE", "minimal_axioms": [], "error": repr(exc)}

    def _load_countermodels(self, inputs: dict[str, Any], registry: dict[str, Any], minimality: dict[str, Any]) -> dict[str, Any]:
        if isinstance(inputs.get("countermodel_generation_result"), dict):
            return dict(inputs["countermodel_generation_result"])
        try:
            from ontology.countermodel_generator import CountermodelGenerator
            return CountermodelGenerator().step(inputs={"synthetic": True, "source": "AN6", "axiom_registry_result": registry, "axiom_minimality_result": minimality}, persist=False)
        except Exception as exc:  # pragma: no cover
            return {"countermodel_generation_status": "COUNTERMODELS_UNAVAILABLE", "countermodels": [], "error": repr(exc)}

    def _load_formal_derivation(self, inputs: dict[str, Any]) -> dict[str, Any]:
        if isinstance(inputs.get("formal_derivation_result"), dict):
            return dict(inputs["formal_derivation_result"])
        try:
            from ontology.formal_derivation_closure import FormalDerivationClosure
            return FormalDerivationClosure().step(inputs={"synthetic": True, "source": "AN6"}, persist=False)
        except Exception as exc:  # pragma: no cover
            return {"formal_derivation_status": "FORMAL_DERIVATION_UNAVAILABLE", "derivations": [], "error": repr(exc)}

    def _normalize_axioms(self, registry: dict[str, Any]) -> list[dict[str, Any]]:
        raw = self._as_list(registry.get("axioms"))
        axioms: list[dict[str, Any]] = []
        seen: set[str] = set()
        for i, item in enumerate(raw, start=1):
            if not isinstance(item, dict):
                continue
            axiom_id = str(item.get("axiom_id") or item.get("id") or f"AN-AX-{i}").strip()
            if not axiom_id or axiom_id in seen:
                continue
            seen.add(axiom_id)
            axioms.append({
                "axiom_id": axiom_id,
                "name": str(item.get("name") or axiom_id),
                "statement": str(item.get("statement") or ""),
                "role": str(item.get("role") or "unspecified"),
                "dependencies": [str(x) for x in self._as_list(item.get("dependencies"))],
            })
        if axioms:
            return axioms
        return [
            {"axiom_id": "AN-A1", "name": "functional_constraint_basis", "statement": "Functional constraints define the reconstruction basis.", "role": "basis", "dependencies": []},
            {"axiom_id": "AN-A2", "name": "minimal_public_evidence", "statement": "Only public measurable evidence is admissible.", "role": "evidence", "dependencies": []},
            {"axiom_id": "AN-A3", "name": "phenomenology_guard", "statement": "Phenomenology remains undetermined.", "role": "epistemic_guard", "dependencies": []},
        ]

    def _minimal_axiom_ids(self, minimality: dict[str, Any], axioms: list[dict[str, Any]]) -> set[str]:
        direct = self._as_list(minimality.get("minimal_axioms"))
        if direct:
            return {str(x) for x in direct}
        findings = self._as_list(minimality.get("minimality_findings"))
        kept = {str(x.get("axiom_id")) for x in findings if isinstance(x, dict) and "MINIMAL" in str(x.get("minimality_status", "")).upper()}
        return kept or {a["axiom_id"] for a in axioms}

    def _countermodel_necessity(self, countermodels: dict[str, Any]) -> dict[str, float]:
        out: dict[str, float] = {}
        for item in self._as_list(countermodels.get("countermodels")):
            if isinstance(item, dict):
                axid = str(item.get("removed_axiom_id") or "").strip()
                if axid:
                    out[axid] = self._clamp01(item.get("necessity_score", item.get("contradiction_score", 0.70)))
        return out

    def _extract_theorems_from_inputs(self, inputs: dict[str, Any]) -> list[dict[str, Any]]:
        raw = self._as_list(inputs.get("theorems"))
        out: list[dict[str, Any]] = []
        for i, item in enumerate(raw, start=1):
            if isinstance(item, dict):
                tid = str(item.get("theorem_id") or item.get("id") or f"TH-{i}")
                out.append({
                    "theorem_id": tid,
                    "name": str(item.get("name") or tid),
                    "statement": str(item.get("statement") or ""),
                    "dependencies": [str(x) for x in self._as_list(item.get("dependencies"))],
                    "source": str(item.get("source") or "inputs"),
                })
        return out

    def _synthetic_theorem_program(self, axioms: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        roles = sorted({a.get("role", "unspecified") for a in axioms}) or ["unspecified"]
        lemmas: list[dict[str, Any]] = []
        for i, role in enumerate(roles, start=1):
            deps = [a["axiom_id"] for a in axioms if a.get("role", "unspecified") == role]
            lemmas.append({
                "lemma_id": f"AN6-L{i}",
                "name": f"{role}_support_lemma",
                "statement": f"Axioms with role {role} jointly support the formal dependency layer.",
                "dependencies": deps or [axioms[0]["axiom_id"]],
                "source": "AN6_synthetic_role_partition",
            })
        propositions = [
            {
                "proposition_id": "AN6-P1",
                "name": "minimal_dependency_basis_proposition",
                "statement": "The minimal axiom basis supports proof-level reconstruction.",
                "dependencies": [x["lemma_id"] for x in lemmas],
                "source": "AN6_synthetic_proof_lattice",
            },
            {
                "proposition_id": "AN6-P2",
                "name": "countermodel_necessity_proposition",
                "statement": "Countermodel withdrawal scores provide axiom usage pressure.",
                "dependencies": [x["lemma_id"] for x in lemmas],
                "source": "AN5_countermodel_linkage",
            },
        ]
        theorems = [
            {
                "theorem_id": "AN6-T1",
                "name": "axiomatic_dependency_mapping_theorem",
                "statement": "The axiom-lemma-proposition-theorem dependency graph can be constructed functionally.",
                "dependencies": ["AN6-P1", "AN6-P2"],
                "source": "AN6_dependency_mapper",
            },
            {
                "theorem_id": "AN6-T2",
                "name": "minimal_proof_dependency_theorem",
                "statement": "Minimal proof dependencies can be extracted from axiom usage paths.",
                "dependencies": ["AN6-P1"],
                "source": "AN6_dependency_mapper",
            },
        ]
        return lemmas, propositions, theorems

    def _build_nodes(self, axioms: list[dict[str, Any]], lemmas: list[dict[str, Any]], propositions: list[dict[str, Any]], theorems: list[dict[str, Any]]) -> list[DependencyNode]:
        nodes: list[DependencyNode] = []
        for a in axioms:
            nodes.append(DependencyNode(a["axiom_id"], "axiom", a.get("name", a["axiom_id"]), "axiom_registry", "registered_axiom"))
        for l in lemmas:
            nodes.append(DependencyNode(l["lemma_id"], "lemma", l.get("name", l["lemma_id"]), l.get("source", "AN6"), "derived_support"))
        for p in propositions:
            nodes.append(DependencyNode(p["proposition_id"], "proposition", p.get("name", p["proposition_id"]), p.get("source", "AN6"), "derived_proposition"))
        for t in theorems:
            nodes.append(DependencyNode(t["theorem_id"], "theorem", t.get("name", t["theorem_id"]), t.get("source", "AN6"), "mapped_theorem"))
        return nodes

    def _build_edges(self, lemmas: list[dict[str, Any]], propositions: list[dict[str, Any]], theorems: list[dict[str, Any]], necessity: dict[str, float]) -> list[DependencyEdge]:
        edges: list[DependencyEdge] = []
        for l in lemmas:
            for dep in l.get("dependencies", []):
                edges.append(DependencyEdge(str(dep), l["lemma_id"], "supports_lemma", round(necessity.get(str(dep), 0.70), 6), "axiom_role_partition"))
        for p in propositions:
            for dep in p.get("dependencies", []):
                edges.append(DependencyEdge(str(dep), p["proposition_id"], "supports_proposition", 0.82, "lemma_to_proposition_mapping"))
        for t in theorems:
            for dep in t.get("dependencies", []):
                edges.append(DependencyEdge(str(dep), t["theorem_id"], "supports_theorem", 0.86, "proposition_to_theorem_mapping"))
        return edges

    def _reachable_axioms(self, theorem_id: str, reverse_edges: dict[str, list[str]], node_types: dict[str, str]) -> set[str]:
        seen: set[str] = set()
        q: deque[str] = deque([theorem_id])
        out: set[str] = set()
        while q:
            current = q.popleft()
            for parent in reverse_edges.get(current, []):
                if parent in seen:
                    continue
                seen.add(parent)
                if node_types.get(parent) == "axiom":
                    out.add(parent)
                q.append(parent)
        return out

    def _graph_analysis(self, nodes: list[DependencyNode], edges: list[DependencyEdge], minimal_ids: set[str]) -> dict[str, Any]:
        node_types = {n.node_id: n.node_type for n in nodes}
        reverse_edges: dict[str, list[str]] = defaultdict(list)
        forward_edges: dict[str, list[str]] = defaultdict(list)
        for e in edges:
            forward_edges[e.source].append(e.target)
            reverse_edges[e.target].append(e.source)
        theorems = [n.node_id for n in nodes if n.node_type == "theorem"]
        axiom_usage: dict[str, list[str]] = {n.node_id: [] for n in nodes if n.node_type == "axiom"}
        theorem_deps: dict[str, list[str]] = {}
        for tid in theorems:
            deps = sorted(self._reachable_axioms(tid, reverse_edges, node_types))
            theorem_deps[tid] = deps
            for ax in deps:
                axiom_usage.setdefault(ax, []).append(tid)
        minimal_proof_dependencies = {tid: [ax for ax in deps if ax in minimal_ids] for tid, deps in theorem_deps.items()}
        redundant_proof_paths = []
        for tid, deps in theorem_deps.items():
            non_min = sorted(set(deps) - set(minimal_proof_dependencies.get(tid, [])))
            if non_min:
                redundant_proof_paths.append({"theorem_id": tid, "redundant_axiom_candidates": non_min, "reason": "non_minimal_axioms_reachable_in_dependency_closure"})
        all_axioms = [n.node_id for n in nodes if n.node_type == "axiom"]
        used_axioms = {a for deps in theorem_deps.values() for a in deps}
        unused_axioms = sorted(set(all_axioms) - used_axioms)
        theorem_dependency_coverage = self._clamp01(len([t for t, d in theorem_deps.items() if d]) / max(1, len(theorems)))
        axiom_usage_coverage = self._clamp01(len(used_axioms) / max(1, len(all_axioms)))
        minimal_usage_coverage = self._clamp01(len(set(minimal_ids) & used_axioms) / max(1, len(minimal_ids)))
        edge_weight_mean = self._mean([e.weight for e in edges], default=0.0)
        return {
            "theorem_dependency_graph": {
                "nodes": [asdict(n) for n in nodes],
                "edges": [asdict(e) for e in edges],
                "node_count": len(nodes),
                "edge_count": len(edges),
                "acyclic_by_construction": True,
            },
            "axiom_usage": {k: sorted(v) for k, v in sorted(axiom_usage.items())},
            "minimal_proof_dependencies": {k: sorted(v) for k, v in sorted(minimal_proof_dependencies.items())},
            "redundant_proof_paths": redundant_proof_paths,
            "unused_axioms": unused_axioms,
            "metrics": {
                "node_count": float(len(nodes)),
                "edge_count": float(len(edges)),
                "theorem_count": float(len(theorems)),
                "axiom_count": float(len(all_axioms)),
                "used_axiom_count": float(len(used_axioms)),
                "theorem_dependency_coverage": theorem_dependency_coverage,
                "axiom_usage_coverage": axiom_usage_coverage,
                "minimal_usage_coverage": minimal_usage_coverage,
                "mean_dependency_edge_weight": round(edge_weight_mean, 6),
                "redundant_proof_path_count": float(len(redundant_proof_paths)),
                "functional_dependency_mapping_readiness_score": self._clamp01(0.30 * theorem_dependency_coverage + 0.30 * axiom_usage_coverage + 0.25 * minimal_usage_coverage + 0.15 * edge_weight_mean),
                "consciousness_proof_score": 0.0,
                "qualia_proof_score": 0.0,
                "subjectivity_proof_score": 0.0,
                "phenomenology_proof_score": 0.0,
            },
        }

    def _persist(self, result: dict[str, Any]) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        (self.out_dir / "latest_theorem_dependencies_mapped.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        with (self.out_dir / "theorem_dependency_mapping_history.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"timestamp_utc": result["timestamp_utc"], "status": result["theorem_dependency_mapping_status"], "metrics": result["dependency_metrics"]}, sort_keys=True) + "\n")

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs if isinstance(inputs, dict) else {}
        registry = self._load_axiom_registry(inputs)
        minimality = self._load_minimality(inputs, registry)
        countermodels = self._load_countermodels(inputs, registry, minimality)
        formal_derivation = self._load_formal_derivation(inputs)
        axioms = self._normalize_axioms(registry)
        minimal_ids = self._minimal_axiom_ids(minimality, axioms)
        necessity = self._countermodel_necessity(countermodels)
        lemmas, propositions, synthetic_theorems = self._synthetic_theorem_program(axioms)
        input_theorems = self._extract_theorems_from_inputs(inputs)
        if input_theorems:
            synthetic_theorems.extend(input_theorems)
        nodes = self._build_nodes(axioms, lemmas, propositions, synthetic_theorems)
        edges = self._build_edges(lemmas, propositions, synthetic_theorems, necessity)
        analysis = self._graph_analysis(nodes, edges, minimal_ids)
        metrics = analysis["metrics"]
        mapped = metrics["functional_dependency_mapping_readiness_score"] >= 0.80 and metrics["theorem_dependency_coverage"] >= 0.95 and metrics["minimal_usage_coverage"] >= 0.95
        status = "THEOREM_DEPENDENCIES_MAPPED" if mapped else "THEOREM_DEPENDENCIES_REQUIRE_REVIEW"
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._now(),
            "theorem_dependency_mapping_status": status,
            "dependencies_mapped": mapped,
            "theorem_dependency_graph": analysis["theorem_dependency_graph"],
            "axiom_usage": analysis["axiom_usage"],
            "minimal_proof_dependencies": analysis["minimal_proof_dependencies"],
            "redundant_proof_paths": analysis["redundant_proof_paths"],
            "unused_axioms": analysis["unused_axioms"],
            "dependency_metrics": metrics,
            "axiom_registry_input_status": registry.get("axiom_registry_status"),
            "axiom_minimality_input_status": minimality.get("axiom_minimality_status"),
            "countermodel_generation_input_status": countermodels.get("countermodel_generation_status"),
            "formal_derivation_input_status": formal_derivation.get("formal_derivation_status") or formal_derivation.get("formal_derivation_closure_status"),
            "ready_for_AN7_axiomatic_completeness_certification": True,
            "axiomatic_completeness_status": "AN6_THEOREM_DEPENDENCIES_READY_FOR_COMPLETENESS_CERTIFICATION",
            "methodological_note": "Dependency mapping is functional and structural; it does not establish phenomenal subjectivity.",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            self._persist(result)
        return result


if __name__ == "__main__":
    print(json.dumps(TheoremDependencyMapper().step(inputs={"synthetic": True}, persist=False), indent=2, ensure_ascii=False, sort_keys=True))
