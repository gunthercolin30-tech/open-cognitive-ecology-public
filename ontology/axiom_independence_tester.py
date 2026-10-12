from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class AxiomIndependenceFinding:
    axiom_id: str
    name: str
    independence_status: str
    independence_score: float
    derivable_from_others: bool
    circular_dependency_detected: bool
    shared_dependency_count: int
    unique_dependency_count: int
    evidence: tuple[str, ...]


class AxiomIndependenceTester:
    """AN2 — structural independence tester for registered axioms.

    The tester is deliberately conservative: it does not claim a complete
    metalogical proof of independence. It checks public, auditable dependency
    signals from AN1 and reports functional independence under the available
    dependency model. This keeps the result useful for engineering while
    preserving epistemic guardrails.
    """

    primitive = "AXIOM_INDEPENDENCE_TESTER"
    step_id = "AN2"
    public_schema_version = "AN2.axiom_independence_tester.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, out_dir: str | Path | None = None) -> None:
        root = Path.home() / "open-cognitive-ecology"
        self.out_dir = Path(out_dir) if out_dir is not None else root / "axiomatic_completeness" / "AN2_axiom_independence_tester"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _as_tuple(value: Any) -> tuple[str, ...]:
        if isinstance(value, (list, tuple, set)):
            return tuple(str(x) for x in value if str(x).strip())
        return tuple()

    def _load_registry(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        if inputs and isinstance(inputs.get("axiom_registry_result"), dict):
            return dict(inputs["axiom_registry_result"])
        try:
            from ontology.axiom_registry import AxiomRegistry
            return AxiomRegistry().step(inputs={"synthetic": True, "source": "AN2"}, persist=False)
        except Exception as exc:  # pragma: no cover - defensive fallback
            return {
                "axiom_registry_status": "AXIOM_REGISTRY_UNAVAILABLE",
                "axioms": [],
                "error": repr(exc),
            }

    def _normalize_axioms(self, registry: dict[str, Any]) -> list[dict[str, Any]]:
        axioms = registry.get("axioms", [])
        if not isinstance(axioms, list):
            return []
        normalized: list[dict[str, Any]] = []
        seen: set[str] = set()
        for i, ax in enumerate(axioms, start=1):
            if not isinstance(ax, dict):
                continue
            axiom_id = str(ax.get("axiom_id") or f"AN-AUTO-{i}").strip()
            if not axiom_id or axiom_id in seen:
                continue
            seen.add(axiom_id)
            normalized.append({
                "axiom_id": axiom_id,
                "name": str(ax.get("name") or axiom_id).strip(),
                "statement": str(ax.get("statement") or "").strip(),
                "role": str(ax.get("role") or "unspecified").strip(),
                "minimality_role": str(ax.get("minimality_role") or "").strip(),
                "independence_target": str(ax.get("independence_target") or "").strip(),
                "dependencies": self._as_tuple(ax.get("dependencies")),
                "empirical_interface": str(ax.get("empirical_interface") or "").strip(),
                "falsification_interface": str(ax.get("falsification_interface") or "").strip(),
            })
        return normalized

    def _find_cycles(self, axioms: list[dict[str, Any]]) -> set[str]:
        ids = {a["axiom_id"] for a in axioms}
        name_to_id = {a["name"]: a["axiom_id"] for a in axioms}
        graph: dict[str, set[str]] = {a["axiom_id"]: set() for a in axioms}
        for a in axioms:
            for dep in a["dependencies"]:
                dep_id = dep if dep in ids else name_to_id.get(dep)
                if dep_id and dep_id != a["axiom_id"]:
                    graph[a["axiom_id"]].add(dep_id)
        cyclic: set[str] = set()
        visiting: set[str] = set()
        visited: set[str] = set()

        def dfs(node: str, stack: tuple[str, ...]) -> None:
            if node in visiting:
                if node in stack:
                    cyclic.update(stack[stack.index(node):])
                return
            if node in visited:
                return
            visiting.add(node)
            for nxt in graph.get(node, set()):
                dfs(nxt, stack + (nxt,))
            visiting.remove(node)
            visited.add(node)

        for node in graph:
            dfs(node, (node,))
        return cyclic

    def _score_axiom(self, axiom: dict[str, Any], all_axioms: list[dict[str, Any]], cyclic_ids: set[str]) -> AxiomIndependenceFinding:
        ax_deps = set(axiom["dependencies"])
        other_deps: set[str] = set()
        for other in all_axioms:
            if other["axiom_id"] != axiom["axiom_id"]:
                other_deps.update(other["dependencies"])
        shared = len(ax_deps & other_deps)
        unique = len(ax_deps - other_deps)
        has_independence_target = bool(axiom["independence_target"])
        has_falsification = bool(axiom["falsification_interface"])
        has_unique_role = sum(1 for other in all_axioms if other.get("role") == axiom.get("role")) == 1
        circular = axiom["axiom_id"] in cyclic_ids

        # Conservative derivability proxy: no unique dependencies, no explicit
        # independence target, no unique role and heavy overlap with the rest.
        derivable = (not has_independence_target) and (not has_unique_role) and unique == 0 and shared >= 2

        score = 0.35
        if has_independence_target:
            score += 0.22
        if has_falsification:
            score += 0.14
        if unique > 0:
            score += 0.16
        if has_unique_role:
            score += 0.10
        if not derivable:
            score += 0.08
        if circular:
            score -= 0.30
        if shared >= 4 and unique == 0:
            score -= 0.10
        score = self._clamp01(score)

        if circular:
            status = "CIRCULAR_DEPENDENCY_REQUIRES_REVIEW"
        elif derivable:
            status = "POTENTIALLY_DERIVABLE_REQUIRES_REVIEW"
        elif score >= 0.72:
            status = "STRUCTURALLY_INDEPENDENT"
        else:
            status = "WEAKLY_INDEPENDENT_REQUIRES_REVIEW"

        evidence = [
            f"unique_dependencies={unique}",
            f"shared_dependencies={shared}",
            f"explicit_independence_target={has_independence_target}",
            f"falsification_interface_present={has_falsification}",
            f"unique_role={has_unique_role}",
            f"derivable_proxy={derivable}",
        ]
        if circular:
            evidence.append("cycle_detected=True")

        return AxiomIndependenceFinding(
            axiom_id=axiom["axiom_id"],
            name=axiom["name"],
            independence_status=status,
            independence_score=round(score, 6),
            derivable_from_others=derivable,
            circular_dependency_detected=circular,
            shared_dependency_count=shared,
            unique_dependency_count=unique,
            evidence=tuple(evidence),
        )

    def _compute_findings(self, axioms: list[dict[str, Any]]) -> list[AxiomIndependenceFinding]:
        cyclic_ids = self._find_cycles(axioms)
        return [self._score_axiom(ax, axioms, cyclic_ids) for ax in axioms]

    def _persist(self, result: dict[str, Any]) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        (self.out_dir / "latest_axiom_independence_test.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        registry = self._load_registry(inputs)
        axioms = self._normalize_axioms(registry)
        findings = self._compute_findings(axioms)

        total = len(findings)
        independent = sum(1 for f in findings if f.independence_status == "STRUCTURALLY_INDEPENDENT")
        weak = sum(1 for f in findings if f.independence_status == "WEAKLY_INDEPENDENT_REQUIRES_REVIEW")
        derivable = sum(1 for f in findings if f.derivable_from_others)
        cyclic = sum(1 for f in findings if f.circular_dependency_detected)
        mean_score = round(sum(f.independence_score for f in findings) / total, 6) if total else 0.0
        independence_ratio = round(independent / total, 6) if total else 0.0
        review_ratio = round((weak + derivable + cyclic) / total, 6) if total else 1.0

        status = "AXIOM_INDEPENDENCE_TESTED" if total > 0 and cyclic == 0 else "AXIOM_INDEPENDENCE_REQUIRES_REVIEW"
        structurally_independent = total > 0 and derivable == 0 and cyclic == 0 and mean_score >= 0.70

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._now(),
            "axiom_independence_status": status,
            "axiom_independence_tested": True,
            "axiom_count": total,
            "structurally_independent_axiom_count": independent,
            "weakly_independent_axiom_count": weak,
            "potentially_derivable_axiom_count": derivable,
            "circular_dependency_count": cyclic,
            "mean_axiom_independence_score": mean_score,
            "axiom_independence_ratio": independence_ratio,
            "independence_review_ratio": review_ratio,
            "axiom_set_structurally_independent": structurally_independent,
            "findings": [asdict(f) for f in findings],
            "independent_axioms": [f.axiom_id for f in findings if f.independence_status == "STRUCTURALLY_INDEPENDENT"],
            "axioms_requiring_review": [f.axiom_id for f in findings if f.independence_status != "STRUCTURALLY_INDEPENDENT"],
            "derivable_axioms": [f.axiom_id for f in findings if f.derivable_from_others],
            "circular_axioms": [f.axiom_id for f in findings if f.circular_dependency_detected],
            "registry_input_status": registry.get("axiom_registry_status"),
            "ready_for_AN3_minimality_analysis": True,
            "axiomatic_completeness_status": "AN2_INDEPENDENCE_READY_FOR_MINIMALITY",
            "methodological_note": "Functional structural independence test only; no phenomenal or absolute metalogical proof is claimed.",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            self._persist(result)
        return result
