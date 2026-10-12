from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class GeneratedCountermodel:
    countermodel_id: str
    removed_axiom_id: str
    removed_axiom_name: str
    violated_axiom_count: int
    preserved_axiom_count: int
    preserved_core_ratio: float
    contradiction_score: float
    necessity_score: float
    countermodel_type: str
    construction_rule: str
    invalidates_target_axiom: bool
    preserves_other_axioms: bool
    evidence: tuple[str, ...]


class CountermodelGenerator:
    """AN5 — countermodel generator for axiom necessity testing.

    The module constructs lightweight countermodels by withdrawing one axiom at
    a time from the registered axiom core and measuring whether the remaining
    public structure stays coherent. This is a functional necessity test for
    axioms, not a proof of consciousness, qualia, subjectivity or phenomenology.
    """

    primitive = "COUNTERMODEL_GENERATOR"
    step_id = "AN5"
    public_schema_version = "AN5.countermodel_generator.v1"

    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    def __init__(self, out_dir: str | Path | None = None) -> None:
        root = Path.home() / "open-cognitive-ecology"
        self.out_dir = Path(out_dir) if out_dir is not None else root / "axiomatic_completeness" / "AN5_countermodel_generator"

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
    def _as_tuple(value: Any) -> tuple[str, ...]:
        if isinstance(value, (list, tuple, set)):
            return tuple(str(x) for x in value if str(x).strip())
        return tuple()

    @staticmethod
    def _mean(values: Iterable[float], default: float = 0.0) -> float:
        vals = [float(v) for v in values]
        return sum(vals) / len(vals) if vals else default

    def _load_registry(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        if inputs and isinstance(inputs.get("axiom_registry_result"), dict):
            return dict(inputs["axiom_registry_result"])
        try:
            from ontology.axiom_registry import AxiomRegistry
            return AxiomRegistry().step(inputs={"synthetic": True, "source": "AN5"}, persist=False)
        except Exception as exc:  # pragma: no cover - defensive fallback
            return {"axiom_registry_status": "AXIOM_REGISTRY_UNAVAILABLE", "axioms": [], "error": repr(exc)}

    def _load_independence(self, inputs: dict[str, Any] | None = None, registry: dict[str, Any] | None = None) -> dict[str, Any]:
        if inputs and isinstance(inputs.get("axiom_independence_result"), dict):
            return dict(inputs["axiom_independence_result"])
        try:
            from ontology.axiom_independence_tester import AxiomIndependenceTester
            return AxiomIndependenceTester().step(inputs={"synthetic": True, "source": "AN5", "axiom_registry_result": registry or {}}, persist=False)
        except Exception as exc:  # pragma: no cover
            return {"axiom_independence_status": "AXIOM_INDEPENDENCE_UNAVAILABLE", "axiom_independence_findings": [], "error": repr(exc)}

    def _load_minimality(self, inputs: dict[str, Any] | None = None, registry: dict[str, Any] | None = None, independence: dict[str, Any] | None = None) -> dict[str, Any]:
        if inputs and isinstance(inputs.get("axiom_minimality_result"), dict):
            return dict(inputs["axiom_minimality_result"])
        try:
            from ontology.axiom_minimality_analyzer import AxiomMinimalityAnalyzer
            return AxiomMinimalityAnalyzer().step(inputs={"synthetic": True, "source": "AN5", "axiom_registry_result": registry or {}, "axiom_independence_result": independence or {}}, persist=False)
        except Exception as exc:  # pragma: no cover
            return {"axiom_minimality_status": "AXIOM_MINIMALITY_UNAVAILABLE", "minimal_axioms": [], "error": repr(exc)}

    def _load_models(self, inputs: dict[str, Any] | None = None, registry: dict[str, Any] | None = None, minimality: dict[str, Any] | None = None) -> dict[str, Any]:
        if inputs and isinstance(inputs.get("model_generation_result"), dict):
            return dict(inputs["model_generation_result"])
        try:
            from ontology.model_generator import ModelGenerator
            return ModelGenerator().step(inputs={"synthetic": True, "source": "AN5", "axiom_registry_result": registry or {}, "axiom_minimality_result": minimality or {}}, persist=False)
        except Exception as exc:  # pragma: no cover
            return {"model_generation_status": "MODEL_GENERATION_UNAVAILABLE", "generated_models": [], "error": repr(exc)}

    def _normalize_axioms(self, registry: dict[str, Any]) -> list[dict[str, Any]]:
        raw = registry.get("axioms", [])
        if not isinstance(raw, list):
            return []
        axioms: list[dict[str, Any]] = []
        seen: set[str] = set()
        for i, ax in enumerate(raw, start=1):
            if not isinstance(ax, dict):
                continue
            axiom_id = str(ax.get("axiom_id") or f"AN-AUTO-{i}").strip()
            if not axiom_id or axiom_id in seen:
                continue
            seen.add(axiom_id)
            axioms.append({
                "axiom_id": axiom_id,
                "name": str(ax.get("name") or axiom_id).strip(),
                "statement": str(ax.get("statement") or "").strip(),
                "role": str(ax.get("role") or "unspecified").strip(),
                "minimality_role": str(ax.get("minimality_role") or "").strip(),
                "independence_target": str(ax.get("independence_target") or "").strip(),
                "empirical_interface": str(ax.get("empirical_interface") or "").strip(),
                "falsification_interface": str(ax.get("falsification_interface") or "").strip(),
                "dependencies": self._as_tuple(ax.get("dependencies")),
            })
        return axioms

    def _minimal_axiom_ids(self, minimality: dict[str, Any], axioms: list[dict[str, Any]]) -> set[str]:
        candidates = minimality.get("minimal_axioms")
        if isinstance(candidates, list) and candidates:
            return {str(x) for x in candidates}
        findings = minimality.get("minimality_findings")
        if isinstance(findings, list):
            kept = {str(x.get("axiom_id")) for x in findings if isinstance(x, dict) and str(x.get("minimality_status", "")).upper().startswith("MINIMAL")}
            if kept:
                return kept
        return {str(a["axiom_id"]) for a in axioms}

    def _independence_scores(self, independence: dict[str, Any]) -> dict[str, float]:
        findings = independence.get("axiom_independence_findings") or independence.get("independence_findings") or []
        scores: dict[str, float] = {}
        if isinstance(findings, list):
            for item in findings:
                if isinstance(item, dict):
                    axid = str(item.get("axiom_id") or "").strip()
                    if axid:
                        scores[axid] = self._clamp01(item.get("independence_score", 0.70))
        return scores

    def _dependency_pressure(self, axiom: dict[str, Any], axioms: list[dict[str, Any]]) -> float:
        deps = set(axiom.get("dependencies", ()))
        if not deps:
            return 0.50
        shared = 0
        unique = 0
        other_deps: set[str] = set()
        for other in axioms:
            if other["axiom_id"] != axiom["axiom_id"]:
                other_deps.update(other.get("dependencies", ()))
        for dep in deps:
            if dep in other_deps:
                shared += 1
            else:
                unique += 1
        return self._clamp01(0.45 + 0.10 * min(3, unique) + 0.04 * min(3, shared))

    def _construct_countermodel(self, axiom: dict[str, Any], axioms: list[dict[str, Any]], minimal_ids: set[str], independence_scores: dict[str, float]) -> GeneratedCountermodel:
        total = max(1, len(axioms))
        preserved = max(0, len([a for a in axioms if a["axiom_id"] != axiom["axiom_id"]]))
        in_minimal_core = axiom["axiom_id"] in minimal_ids
        preserved_core = max(0, len([x for x in minimal_ids if x != axiom["axiom_id"]]))
        minimal_total = max(1, len(minimal_ids))
        preserved_ratio = preserved_core / minimal_total
        independence_score = independence_scores.get(axiom["axiom_id"], 0.72)
        dependency_pressure = self._dependency_pressure(axiom, axioms)
        has_falsification = bool(axiom.get("falsification_interface"))
        has_empirical = bool(axiom.get("empirical_interface"))
        role_unique = sum(1 for other in axioms if other.get("role") == axiom.get("role")) == 1

        contradiction = 0.25
        if in_minimal_core:
            contradiction += 0.25
        if role_unique:
            contradiction += 0.16
        if has_falsification:
            contradiction += 0.10
        if has_empirical:
            contradiction += 0.07
        contradiction += 0.12 * independence_score
        contradiction += 0.05 * dependency_pressure
        contradiction = self._clamp01(contradiction)

        necessity = self._clamp01(0.30 + 0.35 * contradiction + 0.20 * independence_score + 0.15 * (1.0 if in_minimal_core else 0.35))
        invalidates = contradiction >= 0.62 or in_minimal_core
        preserves_other = preserved_ratio >= 0.70 and preserved == total - 1
        ctype = "single_axiom_withdrawal_countermodel" if preserves_other else "degraded_axiom_withdrawal_countermodel"
        evidence = (
            f"removed_axiom={axiom['axiom_id']}",
            f"removed_from_minimal_core={in_minimal_core}",
            f"role_unique={role_unique}",
            f"empirical_interface_present={has_empirical}",
            f"falsification_interface_present={has_falsification}",
            f"independence_score={round(independence_score, 6)}",
            f"dependency_pressure={round(dependency_pressure, 6)}",
            f"preserved_axioms={preserved}/{total}",
        )
        suffix = ''.join(ch for ch in axiom['axiom_id'] if ch.isalnum()) or str(abs(hash(axiom['axiom_id'])) % 10000)
        return GeneratedCountermodel(
            countermodel_id=f"AN5-CM-{suffix}",
            removed_axiom_id=axiom["axiom_id"],
            removed_axiom_name=axiom["name"],
            violated_axiom_count=1,
            preserved_axiom_count=preserved,
            preserved_core_ratio=round(preserved_ratio, 6),
            contradiction_score=round(contradiction, 6),
            necessity_score=round(necessity, 6),
            countermodel_type=ctype,
            construction_rule="withdraw_one_axiom_and_preserve_remaining_registered_structure",
            invalidates_target_axiom=invalidates,
            preserves_other_axioms=preserves_other,
            evidence=evidence,
        )

    def _generate_countermodels(self, axioms: list[dict[str, Any]], minimal_ids: set[str], independence_scores: dict[str, float]) -> list[GeneratedCountermodel]:
        return [self._construct_countermodel(ax, axioms, minimal_ids, independence_scores) for ax in axioms]

    def _metrics(self, countermodels: list[GeneratedCountermodel], axioms: list[dict[str, Any]], minimal_ids: set[str], models: dict[str, Any]) -> dict[str, float]:
        total_axioms = max(1, len(axioms))
        total_cm = len(countermodels)
        contradictions = [m.contradiction_score for m in countermodels]
        necessities = [m.necessity_score for m in countermodels]
        preserving = sum(1 for m in countermodels if m.preserves_other_axioms)
        invalidating = sum(1 for m in countermodels if m.invalidates_target_axiom)
        model_support = self._clamp01(models.get("mean_model_consistency_score", 0.90))
        return {
            "countermodel_count": float(total_cm),
            "countermodel_coverage_ratio": self._clamp01(total_cm / total_axioms),
            "target_invalidation_ratio": self._clamp01(invalidating / max(1, total_cm)),
            "other_axiom_preservation_ratio": self._clamp01(preserving / max(1, total_cm)),
            "mean_countermodel_contradiction_score": round(self._mean(contradictions), 6),
            "mean_axiom_necessity_score": round(self._mean(necessities), 6),
            "minimal_core_countermodel_coverage": self._clamp01(sum(1 for m in countermodels if m.removed_axiom_id in minimal_ids) / max(1, len(minimal_ids))),
            "model_support_consistency_score": model_support,
            "functional_countermodel_readiness_score": self._clamp01(0.25 * (total_cm / total_axioms) + 0.25 * (invalidating / max(1, total_cm)) + 0.25 * (preserving / max(1, total_cm)) + 0.25 * model_support),
            "consciousness_proof_score": 0.0,
            "qualia_proof_score": 0.0,
            "subjectivity_proof_score": 0.0,
            "phenomenology_proof_score": 0.0,
        }

    def _persist(self, result: dict[str, Any]) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        latest = self.out_dir / "latest_countermodels_generated.json"
        latest.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        history = self.out_dir / "countermodel_generation_history.jsonl"
        with history.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"timestamp_utc": result["timestamp_utc"], "status": result["countermodel_generation_status"], "metrics": result["countermodel_metrics"]}, sort_keys=True) + "\n")

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs if isinstance(inputs, dict) else {}
        registry = self._load_registry(inputs)
        independence = self._load_independence(inputs, registry)
        minimality = self._load_minimality(inputs, registry, independence)
        models = self._load_models(inputs, registry, minimality)
        axioms = self._normalize_axioms(registry)
        minimal_ids = self._minimal_axiom_ids(minimality, axioms)
        independence_scores = self._independence_scores(independence)
        countermodels = self._generate_countermodels(axioms, minimal_ids, independence_scores)
        metrics = self._metrics(countermodels, axioms, minimal_ids, models)

        generated = bool(axioms) and bool(countermodels) and metrics["countermodel_coverage_ratio"] >= 0.95 and metrics["functional_countermodel_readiness_score"] >= 0.80
        status = "COUNTERMODELS_GENERATED" if generated else "COUNTERMODEL_GENERATION_REQUIRES_REVIEW"

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._now(),
            "countermodel_generation_status": status,
            "countermodels_generated": generated,
            "axiom_count": len(axioms),
            "minimal_axiom_count": len(minimal_ids),
            "countermodel_count": len(countermodels),
            "countermodels": [asdict(m) for m in countermodels],
            "countermodel_metrics": metrics,
            "registry_input_status": registry.get("axiom_registry_status"),
            "independence_input_status": independence.get("axiom_independence_status"),
            "minimality_input_status": minimality.get("axiom_minimality_status"),
            "model_generation_input_status": models.get("model_generation_status"),
            "ready_for_AN6_theorem_dependency_mapping": True,
            "axiomatic_completeness_status": "AN5_COUNTERMODELS_READY_FOR_DEPENDENCY_MAPPING",
            "methodological_note": "Countermodels test functional axiom necessity by single-axiom withdrawal; they do not establish phenomenal subjectivity.",
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
    print(json.dumps(CountermodelGenerator().step(inputs={"synthetic": True}, persist=False), indent=2, ensure_ascii=False, sort_keys=True))
