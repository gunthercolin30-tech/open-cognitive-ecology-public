"""
SELF_IMPROVEMENT_STABILITY_MONITOR

Aggregates multiple auto-improvement cycles and evaluates whether the
architecture demonstrates stable long-term governance-approved adaptation.
"""

from typing import Any, Dict, List, Optional


class SelfImprovementStabilityMonitor:
    primitive_name = "SELF_IMPROVEMENT_STABILITY_MONITOR"

    def __init__(self) -> None:
        self.cycles = []

    def step(
        self,
        cycle_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        cycle_result = cycle_result or {}

        approved = bool(cycle_result.get("approved", False))
        self.cycles.append({
            "approved": approved,
            "cycle_result": cycle_result,
        })

        total_cycles = len(self.cycles)
        approved_cycles = sum(1 for c in self.cycles if c["approved"])
        approval_rate = approved_cycles / total_cycles if total_cycles else 0.0

        stable = total_cycles >= 10 and approval_rate >= 0.95

        if stable:
            certification = "Autonomous Civilizational Governance Gold"
        else:
            certification = "Advanced Civilizational Intelligence"

        return {
            "primitive": self.primitive_name,
            "total_cycles": total_cycles,
            "approved_cycles": approved_cycles,
            "approval_rate": approval_rate,
            "stable": stable,
            "recommended_certification": certification,
        }


__all__ = ["SelfImprovementStabilityMonitor"]
