from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AxiomMinimalityFinding:
    axiom_id: str
    name: str
    minimality_status: str
    indispensability_score: float
    removable_without_detected_loss: bool
    replacement_candidate_count: int
    independence_score: float
    role_uniqueness: bool
    evidence: tuple[str, ...]


class AxiomMinimalityAnalyzer:
    """AN3 — conservative minimality analyzer for the canonical axiom set.

    This component tests functional minimality under the dependency and
    independence information available from AN1/AN2. It does not claim an
    absolute mathematical proof of minimality; it classifies whether any axiom
    is structurally removable without detected loss of coverage, independence,
    empirical interface, or falsification interface.
    """

    primitive = "AXIOM_MINIMALITY_ANALYZER"
    step_id = "AN3"
    public_schema_version = "AN3.axiom_minimality_analyzer.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, out_dir: str | Path | None = None) -> None:
        root = Path.home() / "open-cognitive-ecology"
        self.out_dir = Path(out_dir) if out_dir is not None else root / "axiomatic_completeness" / "AN3_axiom_minimality_analyzer"

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
            return AxiomRegistry().step(inputs={"synthetic": True, "source": "AN3"}, persist=False)
        except Exception as exc:  # pragma: no cover - defensive fallback
            return {"axiom_registry_status": "AXIOM_REGISTRY_UNAVAILABLE", "axioms": [], "error": repr(exc)}

    def _load_independence(self, inputs: dict[str, Any] | None = None, registry: dict[str, Any] | None = None) -> dict[str, Any]:
        if inputs and isinstance(inputs.get("axiom_independence_result"), dict):
            return dict(inputs["axiom_independence_result"])
        try:
            from ontology.axiom_independence_tester import AxiomIndependenceTester
            return AxiomIndependenceTester().step(
                inputs={"synthetic": True, "source": "AN3", "axiom_registry_result": registry or {}},
                persist=False,
            )
        except Exception as exc:  # pragma: no cover - defensive fallback
            return {"axiom_independence_status": "AXIOM_INDEPENDENCE_UNAVAILABLE", "findings": [], "error": repr(exc)}

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

    def _independence_by_axiom(self, independence: dict[str, Any]) -> dict[str, dict[str, Any]]:
        findings = independence.get("findings", [])
        mapping: dict[str, dict[str, Any]] = {}
        if isinstance(findings, list):
            for item in findings:
                if isinstance(item, dict) and item.get("axiom_id"):
                    mapping[str(item["axiom_id"])] = item
        return mapping

    def _score_axiom(self, axiom: dict[str, Any], axioms: list[dict[str, Any]], independence_finding: dict[str, Any] | None) -> AxiomMinimalityFinding:
        dependencies = set(axiom.get("dependencies", ()))
        role = axiom.get("role", "unspecified")
        same_role = [a for a in axioms if a.get("role") == role and a.get("axiom_id") != axiom.get("axiom_id")]
        role_uniqueness = len(same_role) == 0

        independence_score = 0.0
        derivable = False
        circular = False
        if independence_finding:
            independence_score = float(independence_finding.get("independence_score", 0.0) or 0.0)
            derivable = bool(independence_finding.get("derivable_from_others", False))
            circular = bool(independence_finding.get("circular_dependency_detected", False))

        has_minimality_role = bool(axiom.get("minimality_role"))
        has_independence_target = bool(axiom.get("independence_target"))
        has_empirical_interface = bool(axiom.get("empirical_interface"))
        has_falsification_interface = bool(axiom.get("falsification_interface"))
        dependency_support = min(0.12, 0.03 * len(dependencies))

        replacement_candidates = 0
        for other in same_role:
            other_deps = set(other.get("dependencies", ()))
            if dependencies and dependencies.issubset(other_deps):
                replacement_candidates += 1
            elif not dependencies and other.get("minimality_role") == axiom.get("minimality_role"):
                replacement_candidates += 1

        score = 0.34
        score += min(0.24, independence_score * 0.24)
        if role_uniqueness:
            score += 0.16
        if has_minimality_role:
            score += 0.10
        if has_independence_target:
            score += 0.08
        if has_empirical_interface:
            score += 0.05
        if has_falsification_interface:
            score += 0.05
        score += dependency_support
        if derivable:
            score -= 0.28
        if circular:
            score -= 0.16
        if replacement_candidates > 0 and not role_uniqueness:
            score -= min(0.18, 0.06 * replacement_candidates)
        score = self._clamp01(score)

        removable = (
            derivable
            or (replacement_candidates > 0 and independence_score < 0.62 and not role_uniqueness)
            or (not has_minimality_role and not has_independence_target and independence_score < 0.55 and not role_uniqueness)
        )

        if removable:
            status = "POTENTIALLY_REMOVABLE_REQUIRES_REVIEW"
        elif score >= 0.72:
            status = "MINIMALITY_SUPPORTED"
        else:
            status = "MINIMALITY_WEAK_REQUIRES_REVIEW"

        evidence = (
            f"role_uniqueness={role_uniqueness}",
            f"minimality_role_present={has_minimality_role}",
            f"independence_target_present={has_independence_target}",
            f"empirical_interface_present={has_empirical_interface}",
            f"falsification_interface_present={has_falsification_interface}",
            f"replacement_candidate_count={replacement_candidates}",
            f"derivable_from_others={derivable}",
            f"circular_dependency_detected={circular}",
        )

        return AxiomMinimalityFinding(
            axiom_id=str(axiom["axiom_id"]),
            name=str(axiom["name"]),
            minimality_status=status,
            indispensability_score=round(score, 6),
            removable_without_detected_loss=bool(removable),
            replacement_candidate_count=replacement_candidates,
            independence_score=round(independence_score, 6),
            role_uniqueness=role_uniqueness,
            evidence=evidence,
        )

    def _compute_findings(self, axioms: list[dict[str, Any]], independence: dict[str, Any]) -> list[AxiomMinimalityFinding]:
        by_axiom = self._independence_by_axiom(independence)
        return [self._score_axiom(ax, axioms, by_axiom.get(ax["axiom_id"])) for ax in axioms]

    def _persist(self, result: dict[str, Any]) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        (self.out_dir / "latest_axiom_minimality_analysis.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        registry = self._load_registry(inputs)
        independence = self._load_independence(inputs, registry)
        axioms = self._normalize_axioms(registry)
        findings = self._compute_findings(axioms, independence)

        total = len(findings)
        supported = sum(1 for f in findings if f.minimality_status == "MINIMALITY_SUPPORTED")
        weak = sum(1 for f in findings if f.minimality_status == "MINIMALITY_WEAK_REQUIRES_REVIEW")
        removable = sum(1 for f in findings if f.removable_without_detected_loss)
        mean_score = round(sum(f.indispensability_score for f in findings) / total, 6) if total else 0.0
        minimality_ratio = round(supported / total, 6) if total else 0.0
        removable_ratio = round(removable / total, 6) if total else 1.0

        status = "AXIOM_MINIMALITY_ANALYZED" if total > 0 else "AXIOM_MINIMALITY_UNAVAILABLE"
        axiom_set_functionally_minimal = total > 0 and removable == 0 and mean_score >= 0.70

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._now(),
            "axiom_minimality_status": status,
            "axiom_minimality_analyzed": True,
            "axiom_count": total,
            "minimal_axiom_count": supported,
            "weak_minimality_axiom_count": weak,
            "redundant_axiom_count": removable,
            "removable_axiom_count": removable,
            "mean_axiom_indispensability_score": mean_score,
            "axiom_minimality_score": mean_score,
            "axiom_minimality_ratio": minimality_ratio,
            "removable_axiom_ratio": removable_ratio,
            "axiom_set_functionally_minimal": axiom_set_functionally_minimal,
            "minimality_findings": [asdict(f) for f in findings],
            "minimal_axioms": [f.axiom_id for f in findings if not f.removable_without_detected_loss],
            "removable_axioms": [f.axiom_id for f in findings if f.removable_without_detected_loss],
            "axioms_requiring_minimality_review": [f.axiom_id for f in findings if f.minimality_status != "MINIMALITY_SUPPORTED"],
            "registry_input_status": registry.get("axiom_registry_status"),
            "independence_input_status": independence.get("axiom_independence_status"),
            "ready_for_AN4_model_generation": True,
            "axiomatic_completeness_status": "AN3_MINIMALITY_READY_FOR_MODEL_GENERATION",
            "methodological_note": "Functional minimality analysis only; no phenomenal or absolute metalogical proof is claimed.",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            self._persist(result)
        return result
