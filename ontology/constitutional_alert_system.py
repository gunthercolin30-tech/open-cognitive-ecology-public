"""
Constitutional Alert System.

Monitors constitutional alignment, non-closure, and global viability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PRIMITIVE = "CONSTITUTIONAL_ALERT_SYSTEM"

DEPENDENCIES = [
    "constitutional_alignment",
    "non_closure",
    "global_viability_score",
    "monitoring",
]


@dataclass
class ConstitutionalAlertSystem:
    alignment_threshold: float = 0.85
    non_closure_threshold: float = 0.85
    viability_threshold: float = 0.85
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def evaluate(
        self,
        constitutional_alignment: float = 1.0,
        non_closure: float = 1.0,
        global_viability: float = 1.0,
    ) -> dict[str, Any]:
        alerts = []

        if constitutional_alignment < self.alignment_threshold:
            alerts.append("constitutional_alignment_below_threshold")

        if non_closure < self.non_closure_threshold:
            alerts.append("non_closure_below_threshold")

        if global_viability < self.viability_threshold:
            alerts.append("global_viability_below_threshold")

        self.diagnostics = {
            "primitive": PRIMITIVE,
            "constitutional_alignment": constitutional_alignment,
            "non_closure": non_closure,
            "global_viability": global_viability,
            "alert_count": len(alerts),
            "alerts": alerts,
            "system_stable": len(alerts) == 0,
        }

        return self.diagnostics

    def step(self) -> dict[str, Any]:
        return self.evaluate()
