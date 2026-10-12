
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from math import log
from pathlib import Path
from statistics import mean
from typing import Any, Iterable


class CooperativeSpecializationEngine:
    """
    N5 - Cooperative specialization engine.

    This module is a second-level supervisor for distributed civilizational
    cooperative specialization. It does not replace inter_individual_coordination,
    distributed_agency, emergent_modularity, artificial_society_runtime or
    collective_intelligence.

    It aggregates their functional signals into measurable indicators:
    - specialization_score
    - cooperative_efficiency
    - role_diversity_score
    - cooperative_specialization_score
    - cooperative_specialization_state
    """

    primitive = "COOPERATIVE_SPECIALIZATION_ENGINE"

    DEFAULT_DEPENDENCIES = [
        "inter_individual_coordination_protocol",
        "distributed_agency",
        "emergent_modularity",
        "multi_individual_civilizational_ecology",
        "distributed_population_runtime",
        "artificial_society_runtime",
        "collective_intelligence",
    ]

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.report_dir = self.root / "civilizational_ecology" / "cooperative_specialization_engine"

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

    @staticmethod
    def _extract_role(item: Any) -> str | None:
        if isinstance(item, dict):
            for key in ("role", "function", "specialization", "capability", "task"):
                value = item.get(key)
                if value is not None:
                    return str(value)
            return None
        if item is None:
            return None
        return str(item)

    @staticmethod
    def _normalized_entropy(labels: list[str]) -> float:
        if not labels:
            return 0.0
        counts = Counter(labels)
        n = sum(counts.values())
        if n <= 1 or len(counts) <= 1:
            return 0.0
        entropy = 0.0
        for count in counts.values():
            p = count / n
            if p > 0.0:
                entropy -= p * log(p)
        maximum = log(len(counts))
        if maximum <= 0.0:
            return 0.0
        return max(0.0, min(1.0, entropy / maximum))

    def _derive_from_roles(self, inputs: dict[str, Any]) -> dict[str, float]:
        agents = self._as_list(inputs.get("agents") or inputs.get("individuals") or inputs.get("participants"))
        roles_raw = self._as_list(inputs.get("roles") or inputs.get("role_assignments") or inputs.get("specializations"))
        tasks = self._as_list(inputs.get("tasks") or inputs.get("work_items"))
        completed = self._as_list(inputs.get("completed_tasks") or inputs.get("fulfilled_tasks"))
        cooperations = self._as_list(inputs.get("cooperative_links") or inputs.get("collaborations"))

        role_labels = [r for r in (self._extract_role(x) for x in roles_raw) if r]
        agent_count = len(set(map(str, agents)))
        role_count = len(set(role_labels))
        task_count = len(set(map(str, tasks)))
        completed_count = len(set(map(str, completed)))
        cooperation_count = len(cooperations)

        derived: dict[str, float] = {}
        if agent_count:
            derived["specialization_score"] = self._safe_ratio(role_count, agent_count)
        if role_labels:
            derived["role_diversity_score"] = self._normalized_entropy(role_labels)
        if task_count:
            derived["cooperative_efficiency"] = self._safe_ratio(completed_count, task_count)
        elif agent_count:
            # When tasks are absent, cooperative links provide a weak proxy.
            possible_links = max(agent_count * max(agent_count - 1, 1), 1)
            derived["cooperative_efficiency"] = self._safe_ratio(cooperation_count, possible_links)
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
        derived = self._derive_from_roles(inputs)
        merged = {**derived, **inputs}

        distributed_agency_score = self._metric(
            merged,
            "distributed_agency_score",
            ["distributed_agency_index", "authority_distribution_score", "action_integration"],
            0.72,
        )
        coordination_score = self._metric(
            merged,
            "coordination_score",
            ["inter_individual_coordination_score", "coordination_efficiency", "coordination_coherence"],
            0.72,
        )
        modularity_score = self._metric(
            merged,
            "modularity_score",
            ["emergent_modularity_score", "modularity_strength", "functional_modularity_score"],
            0.70,
        )
        collective_intelligence_score = self._metric(
            merged,
            "collective_intelligence_score",
            ["collective_intelligence_index", "emergent_problem_solving"],
            0.70,
        )
        population_viability_score = self._metric(
            merged,
            "population_viability_score",
            ["population_health", "population_ecology_score", "multi_individual_ecology_score"],
            0.70,
        )
        participation_score = self._metric(
            merged,
            "participation_score",
            ["participation_rate", "active_individual_ratio", "active_individuals_score"],
            0.70,
        )
        role_stability_score = self._metric(
            merged,
            "role_stability_score",
            ["assignment_stability", "role_continuity_score", "role_persistence_score"],
            0.68,
        )
        substitutability_score = self._metric(
            merged,
            "substitutability_score",
            ["functional_overlap", "degeneracy_index", "role_redundancy_score"],
            0.62,
        )

        specialization_score = self._metric(
            merged,
            "specialization_score",
            ["functional_specialization", "role_specialization_score", "specialized_role_coverage"],
            mean([modularity_score, distributed_agency_score, role_stability_score]),
        )
        cooperative_efficiency = self._metric(
            merged,
            "cooperative_efficiency",
            ["coordination_efficiency", "cooperation_efficiency", "collaborative_efficiency"],
            mean([coordination_score, collective_intelligence_score, participation_score]),
        )
        role_diversity_score = self._metric(
            merged,
            "role_diversity_score",
            ["role_diversity", "functional_role_diversity", "specialization_diversity_score"],
            mean([population_viability_score, substitutability_score, specialization_score]),
        )

        role_conflict_pressure = self._metric(
            merged,
            "role_conflict_pressure",
            ["role_conflict_index", "coordination_conflict_pressure"],
            0.18,
        )
        over_specialization_pressure = self._metric(
            merged,
            "over_specialization_pressure",
            ["overspecialization_index", "rigid_specialization_pressure"],
            0.18,
        )
        coordination_failure_pressure = self._metric(
            merged,
            "coordination_failure_pressure",
            ["coordination_failure_risk", "cooperative_breakdown_index"],
            0.18,
        )

        cooperative_specialization_risk_pressure = mean([
            role_conflict_pressure,
            over_specialization_pressure,
            coordination_failure_pressure,
        ])

        positive_score = mean([
            specialization_score,
            cooperative_efficiency,
            role_diversity_score,
            distributed_agency_score,
            coordination_score,
            modularity_score,
            collective_intelligence_score,
            population_viability_score,
            participation_score,
            role_stability_score,
            substitutability_score,
        ])

        cooperative_specialization_score = self._clamp(
            (positive_score * 0.80) + ((1.0 - cooperative_specialization_risk_pressure) * 0.20)
        )

        if cooperative_specialization_score >= 0.74 and cooperative_specialization_risk_pressure <= 0.35:
            cooperative_specialization_state = "cooperative_specialization_healthy"
        elif cooperative_specialization_score >= 0.48 and cooperative_specialization_risk_pressure <= 0.68:
            cooperative_specialization_state = "cooperative_specialization_warning"
        else:
            cooperative_specialization_state = "cooperative_specialization_risk"

        recommended_actions: list[str] = []
        if specialization_score < 0.55:
            recommended_actions.append("increase_functional_role_specialization")
        if cooperative_efficiency < 0.55:
            recommended_actions.append("improve_inter_individual_coordination")
        if role_diversity_score < 0.55:
            recommended_actions.append("expand_role_diversity_and_substitutability")
        if cooperative_specialization_risk_pressure > 0.60:
            recommended_actions.append("reduce_role_conflict_and_over_specialization_pressure")

        result: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "specialization_score": round(specialization_score, 6),
            "cooperative_efficiency": round(cooperative_efficiency, 6),
            "role_diversity_score": round(role_diversity_score, 6),
            "cooperative_specialization_score": round(cooperative_specialization_score, 6),
            "cooperative_specialization_state": cooperative_specialization_state,
            "cooperative_specialization_risk_pressure": round(cooperative_specialization_risk_pressure, 6),
            "distributed_agency_score": round(distributed_agency_score, 6),
            "coordination_score": round(coordination_score, 6),
            "modularity_score": round(modularity_score, 6),
            "collective_intelligence_score": round(collective_intelligence_score, 6),
            "population_viability_score": round(population_viability_score, 6),
            "participation_score": round(participation_score, 6),
            "role_stability_score": round(role_stability_score, 6),
            "substitutability_score": round(substitutability_score, 6),
            "risk_components": {
                "role_conflict_pressure": round(role_conflict_pressure, 6),
                "over_specialization_pressure": round(over_specialization_pressure, 6),
                "coordination_failure_pressure": round(coordination_failure_pressure, 6),
            },
            "recommended_actions": recommended_actions,
            "dependencies": list(self.DEFAULT_DEPENDENCIES),
            "diagnostics": {
                "role": "second_level_cooperative_specialization_supervisor",
                "non_redundancy": "aggregates specialization, cooperative efficiency and role diversity without replacing coordination or agency modules",
                "input_mode": "explicit_payload_or_default_architectural_prior",
            },
        }

        if persist:
            self.report_dir.mkdir(parents=True, exist_ok=True)
            report_path = self.report_dir / "latest_cooperative_specialization_engine.json"
            report_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            result["report_path"] = str(report_path)
        return result


if __name__ == "__main__":
    print(json.dumps(CooperativeSpecializationEngine().step(persist=True), ensure_ascii=False, indent=2, sort_keys=True))
