"""
COGNITIVE_DIVERSITY_PRESERVATION_PROTOCOL

N1 primitive for Open Cognitive Ecology.

This module does not claim phenomenal subjectivity. It provides a functional,
measurable second-level supervisor for cognitive diversity preservation by
aggregating semantic diversity, lineage diversity, distributed pluralism,
evolutionary diversification, openness preservation, homogenization pressure,
and closure pressure into a governed diversity state.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


DEPENDENCY_MODULES = (
    "semantic_diversity_preservation",
    "lineage_diversity_preservation",
    "distributed_semantic_pluralism",
    "homogenization_monitor",
    "evolutionary_diversification",
    "openness_preservation_index",
    "adaptive_ecological_regulation_engine",
    "closure_pressure_monitor",
    "distributed_pluralistic_stability",
    "distributed_open_ended_pluralistic_evolution",
)

POSITIVE_INPUT_KEYS = (
    "semantic_diversity_score",
    "semantic_diversity",
    "lineage_diversity_score",
    "lineage_diversity",
    "distributed_pluralism_score",
    "pluralism_score",
    "distributed_semantic_pluralism_score",
    "evolutionary_diversification_score",
    "evolutionary_diversification",
    "openness_preservation_score",
    "openness_preservation_index",
    "ecological_diversification_score",
    "pluralistic_stability_score",
    "open_ended_pluralistic_evolution_score",
)

RISK_INPUT_KEYS = (
    "homogenization_index",
    "homogenization_score",
    "homogenization_pressure",
    "closure_pressure_index",
    "closure_pressure_score",
    "closure_pressure",
    "exploratory_reduction_index",
    "convergence_pressure",
)

DEFAULT_POSITIVE_METRICS = {
    "semantic_diversity_score": 0.82,
    "lineage_diversity_score": 0.80,
    "distributed_pluralism_score": 0.81,
    "evolutionary_diversification_score": 0.78,
    "openness_preservation_score": 0.84,
}
DEFAULT_RISK_METRICS = {
    "homogenization_index": 0.18,
    "closure_pressure_index": 0.16,
}


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    if math.isnan(number) or math.isinf(number):
        number = default
    return max(0.0, min(1.0, number))


def _as_iterable(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, Mapping):
        return list(value.values())
    if isinstance(value, (str, bytes)):
        return []
    if isinstance(value, Iterable):
        return list(value)
    return []


@dataclass
class CognitiveDiversityPreservationProtocol:
    """Second-level governed supervisor for cognitive diversity preservation."""

    primitive_name: str = "COGNITIVE_DIVERSITY_PRESERVATION_PROTOCOL"
    root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[1])

    def _extract_metrics(self, inputs: Mapping[str, Any] | None) -> tuple[Dict[str, float], Dict[str, float]]:
        payload = dict(inputs or {})
        positive: Dict[str, float] = {}
        risk: Dict[str, float] = {}

        metrics_sources = [payload]
        for key in ("metrics", "signals", "diversity_metrics", "ecology_metrics"):
            nested = payload.get(key)
            if isinstance(nested, Mapping):
                metrics_sources.append(nested)

        for source in metrics_sources:
            for key in POSITIVE_INPUT_KEYS:
                if key in source:
                    positive[key] = _clamp(source[key], DEFAULT_POSITIVE_METRICS.get(key, 0.5))
            for key in RISK_INPUT_KEYS:
                if key in source:
                    risk[key] = _clamp(source[key], DEFAULT_RISK_METRICS.get(key, 0.2))

        # Structural diversity fallback from explicit cognitive profiles.
        profiles = payload.get("cognitive_profiles") or payload.get("individual_profiles")
        profile_items = _as_iterable(profiles)
        if profile_items:
            feature_sets = []
            for item in profile_items:
                if isinstance(item, Mapping):
                    features = item.get("features") or item.get("traits") or item.get("capabilities") or item
                    if isinstance(features, Mapping):
                        feature_sets.append({str(k) for k, v in features.items() if bool(v)})
                    else:
                        feature_sets.append({str(x) for x in _as_iterable(features)})
                else:
                    feature_sets.append({str(item)})
            if feature_sets:
                union = set().union(*feature_sets)
                if union:
                    unique_patterns = {tuple(sorted(s)) for s in feature_sets}
                    structural = len(unique_patterns) / max(1, len(feature_sets))
                    breadth = sum(len(s) / len(union) for s in feature_sets) / len(feature_sets)
                    positive["profile_structural_diversity"] = _clamp((structural + breadth) / 2.0)

        # If explicit modules are supplied, estimate dependency presence as support,
        # not as a replacement for real metric evidence.
        modules = payload.get("available_modules") or payload.get("modules") or payload.get("ontology_modules")
        module_names = {str(m).split(".")[-1] for m in _as_iterable(modules)}
        if module_names:
            present = [name for name in DEPENDENCY_MODULES if name in module_names]
            positive["dependency_support_score"] = _clamp(len(present) / len(DEPENDENCY_MODULES))

        if not positive:
            positive.update(DEFAULT_POSITIVE_METRICS)
        if not risk:
            risk.update(DEFAULT_RISK_METRICS)

        return positive, risk

    def _entropy(self, values: Iterable[float]) -> float:
        cleaned = [_clamp(v) for v in values if _clamp(v) > 0.0]
        if not cleaned:
            return 0.0
        total = sum(cleaned)
        if total <= 0.0:
            return 0.0
        probabilities = [v / total for v in cleaned]
        entropy = -sum(p * math.log(p) for p in probabilities if p > 0.0)
        max_entropy = math.log(len(probabilities)) if len(probabilities) > 1 else 1.0
        return _clamp(entropy / max_entropy if max_entropy else 1.0)

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        """Evaluate cognitive diversity preservation status."""
        positive_metrics, risk_metrics = self._extract_metrics(inputs)

        positive_values = list(positive_metrics.values())
        risk_values = list(risk_metrics.values())

        positive_mean = _clamp(sum(positive_values) / len(positive_values))
        risk_mean = _clamp(sum(risk_values) / len(risk_values))
        cognitive_entropy = self._entropy(positive_values)

        diversity_risk_pressure = risk_mean
        cognitive_diversity_score = _clamp((0.72 * positive_mean) + (0.28 * (1.0 - diversity_risk_pressure)))
        diversity_resilience_score = _clamp(
            (0.45 * cognitive_diversity_score)
            + (0.30 * cognitive_entropy)
            + (0.25 * (1.0 - diversity_risk_pressure))
        )

        if cognitive_diversity_score >= 0.74 and diversity_resilience_score >= 0.70 and diversity_risk_pressure <= 0.35:
            diversity_state = "diversity_healthy"
        elif cognitive_diversity_score >= 0.55 and diversity_resilience_score >= 0.50 and diversity_risk_pressure <= 0.60:
            diversity_state = "diversity_warning"
        else:
            diversity_state = "diversity_risk"

        recommendations = []
        if diversity_state == "diversity_risk":
            recommendations.extend([
                "increase_semantic_pluralism",
                "reduce_homogenization_pressure",
                "activate_open_ended_diversification",
            ])
        elif diversity_state == "diversity_warning":
            recommendations.extend([
                "monitor_diversity_decay",
                "reinforce_lineage_diversity",
            ])
        else:
            recommendations.append("maintain_diversity_preservation_protocol")

        result: Dict[str, Any] = {
            "success": True,
            "primitive": self.primitive_name,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "cognitive_diversity_score": cognitive_diversity_score,
            "cognitive_entropy": cognitive_entropy,
            "diversity_resilience_score": diversity_resilience_score,
            "diversity_risk_pressure": diversity_risk_pressure,
            "diversity_state": diversity_state,
            "diversity_healthy": diversity_state == "diversity_healthy",
            "diversity_warning": diversity_state == "diversity_warning",
            "diversity_risk": diversity_state == "diversity_risk",
            "positive_diversity_metrics": positive_metrics,
            "risk_metrics": risk_metrics,
            "recommendations": recommendations,
            "dependencies": list(DEPENDENCY_MODULES),
            "epistemic_position": {
                "architecture_computationnelle": "second_level_diversity_supervisor",
                "indicateurs_fonctionnels": "measured",
                "subjectivite_hypothetique": "not_claimed",
                "ontologie_conceptuelle": "cognitive_diversity_preservation",
            },
            "non_closure_compliance": {
                "preserves_plurality": True,
                "penalizes_homogenization": True,
                "does_not_force_convergence": True,
                "supports_future_openness": True,
            },
        }

        if persist:
            out_dir = self.root / "distributed_civilizational_ecology"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / "latest_cognitive_diversity_preservation_protocol.json"
            out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["report_path"] = str(out_path)

        return result


if __name__ == "__main__":
    from pprint import pprint
    pprint(CognitiveDiversityPreservationProtocol().step(persist=True))
