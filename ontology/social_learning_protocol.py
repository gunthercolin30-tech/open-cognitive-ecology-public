
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Iterable


class SocialLearningProtocol:
    """
    N4 - Social learning protocol.

    This module is a second-level supervisor for distributed civilizational
    social learning. It does not replace collective_intelligence,
    knowledge_accumulation, knowledge_integration_engine,
    intra_species_social_interaction or inter_individual_coordination_protocol.

    It aggregates their functional signals into measurable indicators:
    - social_learning_rate
    - knowledge_diffusion_rate
    - learning_efficiency
    - social_learning_score
    - social_learning_state
    """

    primitive = "SOCIAL_LEARNING_PROTOCOL"

    DEFAULT_DEPENDENCIES = [
        "collective_intelligence",
        "collective_deliberation_engine",
        "knowledge_accumulation",
        "knowledge_integration_engine",
        "intra_species_social_interaction",
        "inter_individual_coordination_protocol",
        "population_ecological_extraction",
        "multi_individual_civilizational_ecology",
    ]

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.report_dir = self.root / "civilizational_ecology" / "social_learning_protocol"

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            x = float(value)
        except (TypeError, ValueError):
            x = default
        if x < 0.0:
            return 0.0
        if x > 1.0:
            return 1.0
        return x

    @staticmethod
    def _safe_ratio(numerator: int | float, denominator: int | float) -> float:
        try:
            den = float(denominator)
            if den <= 0.0:
                return 0.0
            return max(0.0, min(1.0, float(numerator) / den))
        except (TypeError, ValueError, ZeroDivisionError):
            return 0.0

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, set):
            return sorted(value, key=lambda x: str(x))
        return [value]

    def _derive_from_items(self, inputs: dict[str, Any]) -> dict[str, float]:
        learners = self._as_list(inputs.get("learners") or inputs.get("individuals"))
        sources = self._as_list(inputs.get("knowledge_sources") or inputs.get("source_knowledge"))
        learned = self._as_list(inputs.get("learned_items") or inputs.get("acquired_knowledge"))
        shared = self._as_list(inputs.get("shared_knowledge") or inputs.get("diffused_knowledge"))
        integrated = self._as_list(inputs.get("integrated_knowledge") or inputs.get("retained_knowledge"))

        source_count = len(set(map(str, sources)))
        learned_count = len(set(map(str, learned)))
        shared_count = len(set(map(str, shared)))
        integrated_count = len(set(map(str, integrated)))
        learner_count = len(set(map(str, learners)))

        derived: dict[str, float] = {}
        if source_count:
            derived["social_learning_rate"] = self._safe_ratio(learned_count, source_count)
            derived["knowledge_diffusion_rate"] = self._safe_ratio(shared_count, source_count)
            derived["learning_efficiency"] = self._safe_ratio(integrated_count, max(learned_count, 1))
        if learner_count and source_count:
            # More learners sharing/integrating knowledge improves the effective social coverage.
            derived["participation_score"] = self._safe_ratio(learner_count, max(source_count, learner_count))
        return derived

    def _metric(self, inputs: dict[str, Any], key: str, aliases: Iterable[str], default: float) -> float:
        if key in inputs:
            return self._clamp(inputs.get(key), default)
        for alias in aliases:
            if alias in inputs:
                return self._clamp(inputs.get(alias), default)
        return self._clamp(default)

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = dict(inputs or {})
        derived = self._derive_from_items(inputs)
        merged = {**derived, **inputs}

        collective_intelligence_score = self._metric(
            merged,
            "collective_intelligence_score",
            ["collective_intelligence_index", "emergent_problem_solving_score"],
            0.72,
        )
        knowledge_accumulation_score = self._metric(
            merged,
            "knowledge_accumulation_score",
            ["knowledge_accumulation_index", "knowledge_growth_score"],
            0.70,
        )
        knowledge_integration_score = self._metric(
            merged,
            "knowledge_integration_score",
            ["integration_capacity", "integration_consistency_score"],
            0.70,
        )
        social_interaction_score = self._metric(
            merged,
            "social_interaction_score",
            ["intra_species_social_interaction_index", "interaction_effectiveness"],
            0.70,
        )
        coordination_score = self._metric(
            merged,
            "coordination_score",
            ["inter_individual_coordination_score", "coordination_efficiency"],
            0.70,
        )
        population_diversity_score = self._metric(
            merged,
            "population_diversity_score",
            ["lineage_diversity_score", "population_ecological_diversity"],
            0.68,
        )
        cultural_transmission_score = self._metric(
            merged,
            "cultural_transmission_score",
            ["transmission_fidelity", "cultural_evolution_index"],
            0.68,
        )
        participation_score = self._metric(
            merged,
            "participation_score",
            ["participation_rate", "collective_participation_score"],
            0.70,
        )

        social_learning_rate = self._metric(
            merged,
            "social_learning_rate",
            ["social_learning_gain", "learning_rate"],
            mean([social_interaction_score, collective_intelligence_score, participation_score]),
        )
        knowledge_diffusion_rate = self._metric(
            merged,
            "knowledge_diffusion_rate",
            ["diffusion_rate", "knowledge_sharing_rate"],
            mean([knowledge_accumulation_score, knowledge_integration_score, cultural_transmission_score]),
        )
        learning_efficiency = self._metric(
            merged,
            "learning_efficiency",
            ["collective_learning_efficiency", "learning_effectiveness"],
            mean([knowledge_integration_score, coordination_score, population_diversity_score]),
        )

        misinformation_pressure = self._metric(
            merged,
            "misinformation_pressure",
            ["noise_pressure", "epistemic_noise_index"],
            0.18,
        )
        fragmentation_pressure = self._metric(
            merged,
            "fragmentation_pressure",
            ["symbolic_fragmentation_index", "social_fragmentation_index"],
            0.18,
        )
        coordination_failure_pressure = self._metric(
            merged,
            "coordination_failure_pressure",
            ["coordination_failure_risk", "coordination_breakdown_index"],
            0.18,
        )

        social_learning_risk_pressure = mean([
            misinformation_pressure,
            fragmentation_pressure,
            coordination_failure_pressure,
        ])

        positive_score = mean([
            social_learning_rate,
            knowledge_diffusion_rate,
            learning_efficiency,
            collective_intelligence_score,
            knowledge_accumulation_score,
            knowledge_integration_score,
            social_interaction_score,
            coordination_score,
            population_diversity_score,
            cultural_transmission_score,
            participation_score,
        ])

        social_learning_score = self._clamp(
            (positive_score * 0.78) + ((1.0 - social_learning_risk_pressure) * 0.22)
        )

        if social_learning_score >= 0.74 and social_learning_risk_pressure <= 0.35:
            social_learning_state = "social_learning_healthy"
        elif social_learning_score >= 0.48 and social_learning_risk_pressure <= 0.68:
            social_learning_state = "social_learning_warning"
        else:
            social_learning_state = "social_learning_risk"

        recommended_actions: list[str] = []
        if social_learning_rate < 0.55:
            recommended_actions.append("increase_social_learning_interactions")
        if knowledge_diffusion_rate < 0.55:
            recommended_actions.append("improve_knowledge_diffusion_channels")
        if learning_efficiency < 0.55:
            recommended_actions.append("strengthen_collective_learning_integration")
        if social_learning_risk_pressure > 0.60:
            recommended_actions.append("reduce_fragmentation_and_noise_pressure")

        result: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "social_learning_rate": round(social_learning_rate, 6),
            "knowledge_diffusion_rate": round(knowledge_diffusion_rate, 6),
            "learning_efficiency": round(learning_efficiency, 6),
            "social_learning_score": round(social_learning_score, 6),
            "social_learning_state": social_learning_state,
            "social_learning_risk_pressure": round(social_learning_risk_pressure, 6),
            "collective_intelligence_score": round(collective_intelligence_score, 6),
            "knowledge_accumulation_score": round(knowledge_accumulation_score, 6),
            "knowledge_integration_score": round(knowledge_integration_score, 6),
            "social_interaction_score": round(social_interaction_score, 6),
            "coordination_score": round(coordination_score, 6),
            "population_diversity_score": round(population_diversity_score, 6),
            "cultural_transmission_score": round(cultural_transmission_score, 6),
            "participation_score": round(participation_score, 6),
            "risk_components": {
                "misinformation_pressure": round(misinformation_pressure, 6),
                "fragmentation_pressure": round(fragmentation_pressure, 6),
                "coordination_failure_pressure": round(coordination_failure_pressure, 6),
            },
            "recommended_actions": recommended_actions,
            "dependencies": list(self.DEFAULT_DEPENDENCIES),
            "diagnostics": {
                "role": "second_level_social_learning_supervisor",
                "non_redundancy": "aggregates social learning rate, diffusion and efficiency without replacing existing collective modules",
                "input_mode": "explicit_payload_or_default_architectural_prior",
            },
        }

        if persist:
            self.report_dir.mkdir(parents=True, exist_ok=True)
            report_path = self.report_dir / "latest_social_learning_protocol.json"
            report_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            result["report_path"] = str(report_path)
        return result


if __name__ == "__main__":
    print(json.dumps(SocialLearningProtocol().step(persist=True), ensure_ascii=False, indent=2, sort_keys=True))
