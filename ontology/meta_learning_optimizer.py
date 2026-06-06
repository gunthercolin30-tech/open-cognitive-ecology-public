"""
META_LEARNING_OPTIMIZER

Analyzes accumulated experience records and identifies the most effective
strategy adjustments over time.
"""

from typing import Any, Dict, List


class MetaLearningOptimizer:
    primitive_name = "META_LEARNING_OPTIMIZER"

    def step(self, experience_records: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        experience_records = experience_records or []

        if not experience_records:
            return {
                "primitive": self.primitive_name,
                "optimized": False,
                "reason": "no_experience_records",
                "recommended_global_strategy": "collect_more_experience",
                "strategy_statistics": {},
            }

        strategy_stats: Dict[str, Dict[str, float]] = {}

        for record in experience_records:
            strategy = record.get("strategy_adjustment", "unknown")
            gap = float(record.get("performance_gap", 0.0))

            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    "count": 0,
                    "total_gap": 0.0,
                }

            strategy_stats[strategy]["count"] += 1
            strategy_stats[strategy]["total_gap"] += gap

        for strategy, stats in strategy_stats.items():
            stats["average_gap"] = stats["total_gap"] / max(stats["count"], 1)

        best_strategy = min(
            strategy_stats.items(),
            key=lambda item: item[1]["average_gap"]
        )[0]

        return {
            "primitive": self.primitive_name,
            "optimized": True,
            "experience_count": len(experience_records),
            "recommended_global_strategy": best_strategy,
            "strategy_statistics": strategy_stats,
        }


__all__ = ["MetaLearningOptimizer"]
