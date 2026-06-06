"""
performance_improvement_planner.py

Transforms performance gaps and optimization opportunities into a
prioritized improvement plan.
Extended with civilizational viability projection and planning history.
"""

from datetime import datetime


class PerformanceImprovementPlanner:
    """Plan prioritized actions to improve system performance."""

    def __init__(self):
        self.plan_counter = 0
        self.planning_history = []

    @staticmethod
    def _clamp(value):
        return max(0.0, min(1.0, float(value)))

    def _recommend_next_primitive(self, priority_ranking):
        if not priority_ranking:
            return "NO_ACTION_REQUIRED"

        mapping = {
            "memory_recall": "PERSONAL_MEMORY_RECALL_VALIDATOR",
            "query_resolution": "COMPLEX_QUERY_RESOLUTION_ENGINE",
            "parameter_stability": "SELF_PARAMETER_OPTIMIZATION_ENGINE",
        }

        return mapping.get(
            priority_ranking[0],
            priority_ranking[0].upper(),
        )

    def step(self, inputs):
        self.plan_counter += 1

        performance_gaps = inputs.get(
            "performance_gaps",
            {
                "memory_recall": 0.15,
                "query_resolution": 0.08,
                "parameter_stability": 0.05,
            },
        )

        improvement_candidates = inputs.get(
            "improvement_candidates",
            [
                "increase_memory_validation_cycles",
                "expand_query_decomposition_rules",
                "run_additional_parameter_search",
            ],
        )

        sorted_gaps = sorted(
            performance_gaps.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        priority_ranking = [name for name, _ in sorted_gaps]

        recommended_actions = [
            {
                "priority": index + 1,
                "target": target,
                "recommended_action": (
                    improvement_candidates[index]
                    if index < len(improvement_candidates)
                    else f"improve_{target}"
                ),
            }
            for index, target in enumerate(priority_ranking)
        ]

        projected_gain = self._clamp(sum(performance_gaps.values()))
        improvement_confidence = self._clamp(1.0 - projected_gain * 0.2)

        current_cvi = self._clamp(
            inputs.get("civilizational_viability_index", 0.9573)
        )
        civilizational_viability_projection = self._clamp(
            current_cvi + projected_gain * 0.25
        )

        recommended_next_primitive = self._recommend_next_primitive(
            priority_ranking
        )

        improvement_plan_trace = {
            "plan_id": f"PIP-{self.plan_counter:04d}",
            "timestamp": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            "priority_count": len(priority_ranking),
        }

        result = {
            "primitive": "PERFORMANCE_IMPROVEMENT_PLANNER",
            "performance_gaps": performance_gaps,
            "improvement_candidates": improvement_candidates,
            "priority_ranking": priority_ranking,
            "recommended_actions": recommended_actions,
            "projected_gain": projected_gain,
            "improvement_plan_trace": improvement_plan_trace,
            "improvement_confidence": improvement_confidence,
            "civilizational_viability_projection":
                civilizational_viability_projection,
            "recommended_next_primitive":
                recommended_next_primitive,
        }

        self.planning_history.append(
            {
                "timestamp": improvement_plan_trace["timestamp"],
                "projected_gain": projected_gain,
                "recommended_next_primitive":
                    recommended_next_primitive,
            }
        )

        result["planning_history_length"] = len(self.planning_history)

        return result
