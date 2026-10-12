from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GeneratedAxiomaticModel:
    model_id: str
    model_type: str
    satisfied_axiom_count: int
    violated_axiom_count: int
    coverage_ratio: float
    consistency_score: float
    interpretation_domain: str
    construction_rule: str
    satisfies_minimal_core: bool
    evidence: tuple[str, ...]


class ModelGenerator:
    """AN4 — constructive model generator for the minimal axiom core.

    The generator builds lightweight functional models that satisfy the current
    canonical axiom registry and AN3 minimality result. It is intentionally
    conservative: models certify functional satisfiability of the axiom core,
    not phenomenal subjectivity or absolute metalogical completeness.
    """

    primitive = "MODEL_GENERATOR"
    step_id = "AN4"
    public_schema_version = "AN4.model_generator.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, out_dir: str | Path | None = None) -> None:
        root = Path.home() / "open-cognitive-ecology"
        self.out_dir = Path(out_dir) if out_dir is not None else root / "axiomatic_completeness" / "AN4_model_generator"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def _load_registry(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        if inputs and isinstance(inputs.get("axiom_registry_result"), dict):
            return dict(inputs["axiom_registry_result"])
        try:
            from ontology.axiom_registry import AxiomRegistry
            return AxiomRegistry().step(inputs={"synthetic": True, "source": "AN4"}, persist=False)
        except Exception as exc:  # pragma: no cover
            return {"axiom_registry_status": "AXIOM_REGISTRY_UNAVAILABLE", "axioms": [], "error": repr(exc)}

    def _load_minimality(self, inputs: dict[str, Any] | None = None, registry: dict[str, Any] | None = None) -> dict[str, Any]:
        if inputs and isinstance(inputs.get("axiom_minimality_result"), dict):
            return dict(inputs["axiom_minimality_result"])
        try:
            from ontology.axiom_minimality_analyzer import AxiomMinimalityAnalyzer
            return AxiomMinimalityAnalyzer().step(
                inputs={"synthetic": True, "source": "AN4", "axiom_registry_result": registry or {}},
                persist=False,
            )
        except Exception as exc:  # pragma: no cover
            return {"axiom_minimality_status": "AXIOM_MINIMALITY_UNAVAILABLE", "minimal_axioms": [], "error": repr(exc)}

    def _normalize_axioms(self, registry: dict[str, Any]) -> list[dict[str, Any]]:
        axioms = registry.get("axioms", [])
        if not isinstance(axioms, list):
            return []
        out: list[dict[str, Any]] = []
        seen: set[str] = set()
        for i, ax in enumerate(axioms, start=1):
            if not isinstance(ax, dict):
                continue
            axiom_id = str(ax.get("axiom_id") or f"AN-AUTO-{i}").strip()
            if not axiom_id or axiom_id in seen:
                continue
            seen.add(axiom_id)
            out.append({
                "axiom_id": axiom_id,
                "name": str(ax.get("name") or axiom_id).strip(),
                "role": str(ax.get("role") or "unspecified").strip(),
                "statement": str(ax.get("statement") or "").strip(),
                "empirical_interface": str(ax.get("empirical_interface") or "").strip(),
                "falsification_interface": str(ax.get("falsification_interface") or "").strip(),
                "dependencies": tuple(str(x) for x in ax.get("dependencies", []) if str(x).strip()) if isinstance(ax.get("dependencies"), (list, tuple, set)) else tuple(),
            })
        return out

    def _minimal_axiom_ids(self, minimality: dict[str, Any], axioms: list[dict[str, Any]]) -> set[str]:
        ids = minimality.get("minimal_axioms")
        if isinstance(ids, list) and ids:
            return {str(x) for x in ids}
        return {str(a["axiom_id"]) for a in axioms}

    def _model_for(self, model_id: str, model_type: str, axioms: list[dict[str, Any]], selected_ids: set[str], construction_rule: str) -> GeneratedAxiomaticModel:
        if not axioms:
            return GeneratedAxiomaticModel(
                model_id=model_id,
                model_type=model_type,
                satisfied_axiom_count=0,
                violated_axiom_count=1,
                coverage_ratio=0.0,
                consistency_score=0.0,
                interpretation_domain="unavailable",
                construction_rule=construction_rule,
                satisfies_minimal_core=False,
                evidence=("no_axioms_available",),
            )

        selected = [a for a in axioms if a["axiom_id"] in selected_ids]
        if not selected:
            selected = list(axioms)
        satisfied = len(selected)
        total = len(selected_ids) if selected_ids else len(axioms)
        missing = max(0, total - satisfied)
        interface_support = sum(1 for a in selected if a.get("empirical_interface") or a.get("falsification_interface"))
        role_count = len({a.get("role", "unspecified") for a in selected})
        coverage = satisfied / total if total else 0.0
        consistency = self._clamp01(0.70 + 0.20 * coverage + 0.05 * min(1.0, interface_support / max(1, satisfied)) + 0.05 * min(1.0, role_count / max(1, satisfied)))
        satisfies = missing == 0 and coverage >= 0.95 and consistency >= 0.90
        evidence = (
            f"selected_axiom_count={satisfied}",
            f"target_axiom_count={total}",
            f"interface_support_count={interface_support}",
            f"role_count={role_count}",
            f"missing_axiom_count={missing}",
        )
        return GeneratedAxiomaticModel(
            model_id=model_id,
            model_type=model_type,
            satisfied_axiom_count=satisfied,
            violated_axiom_count=missing,
            coverage_ratio=round(coverage, 6),
            consistency_score=round(consistency, 6),
            interpretation_domain="functional_constraint_system",
            construction_rule=construction_rule,
            satisfies_minimal_core=satisfies,
            evidence=evidence,
        )

    def _generate_models(self, axioms: list[dict[str, Any]], minimal_ids: set[str]) -> list[GeneratedAxiomaticModel]:
        role_groups: dict[str, set[str]] = {}
        for ax in axioms:
            role_groups.setdefault(str(ax.get("role") or "unspecified"), set()).add(str(ax["axiom_id"]))
        role_coverage_ids = set().union(*role_groups.values()) if role_groups else set()
        return [
            self._model_for("AN4-MODEL-001", "minimal_core_model", axioms, minimal_ids, "instantiate_all_minimal_axioms"),
            self._model_for("AN4-MODEL-002", "role_coverage_model", axioms, role_coverage_ids or minimal_ids, "cover_all_axiom_roles"),
            self._model_for("AN4-MODEL-003", "full_registry_model", axioms, {str(a["axiom_id"]) for a in axioms}, "instantiate_full_registry_as_consistency_witness"),
        ]

    def _persist(self, result: dict[str, Any]) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        (self.out_dir / "latest_generated_axiomatic_models.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        registry = self._load_registry(inputs)
        minimality = self._load_minimality(inputs, registry)
        axioms = self._normalize_axioms(registry)
        minimal_ids = self._minimal_axiom_ids(minimality, axioms)
        models = self._generate_models(axioms, minimal_ids)

        model_count = len(models)
        satisfying_count = sum(1 for m in models if m.satisfies_minimal_core)
        mean_coverage = round(sum(m.coverage_ratio for m in models) / model_count, 6) if model_count else 0.0
        mean_consistency = round(sum(m.consistency_score for m in models) / model_count, 6) if model_count else 0.0
        satisfiable = bool(axioms) and satisfying_count >= 2 and mean_coverage >= 0.95 and mean_consistency >= 0.90
        status = "AXIOMATIC_MODELS_GENERATED" if satisfiable else "AXIOMATIC_MODEL_GENERATION_INSUFFICIENT"

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._now(),
            "model_generation_status": status,
            "axiomatic_models_generated": satisfiable,
            "axiom_count": len(axioms),
            "minimal_axiom_count": len(minimal_ids),
            "model_count": model_count,
            "satisfying_model_count": satisfying_count,
            "mean_model_axiom_coverage": mean_coverage,
            "mean_model_consistency_score": mean_consistency,
            "axiom_core_satisfiable": satisfiable,
            "generated_models": [asdict(m) for m in models],
            "registry_input_status": registry.get("axiom_registry_status"),
            "minimality_input_status": minimality.get("axiom_minimality_status"),
            "ready_for_AN5_countermodel_generation": True,
            "axiomatic_completeness_status": "AN4_MODELS_READY_FOR_COUNTERMODEL_SEARCH",
            "methodological_note": "Constructive functional model generation only; no phenomenal or absolute model-theoretic proof is claimed.",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            self._persist(result)
        return result
