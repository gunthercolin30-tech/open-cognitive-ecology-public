"""
Collective Research Program Manager.

Generates and prioritizes collective research programs from observations,
alerts, and open questions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PRIMITIVE = "COLLECTIVE_RESEARCH_PROGRAM_MANAGER"

DEPENDENCIES = [
    "open_ended_inquiry",
    "collective_intelligence",
    "prioritization",
    "web_dashboard_exporter",
    "constitutional_alert_system",
]


@dataclass
class CollectiveResearchProgramManager:
    program_counter: int = 0
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def generate_program(
        self,
        theme: str = "conscience artificielle fonctionnelle",
        urgency: float = 0.9,
        expected_impact: float = 0.95,
    ) -> dict[str, Any]:
        self.program_counter += 1

        program = {
            "program_id": f"CRP-{self.program_counter:04d}",
            "theme": theme,
            "urgency": urgency,
            "expected_impact": expected_impact,
            "priority_score": round((urgency + expected_impact) / 2.0, 3),
            "research_questions": [
                f"Quels mécanismes sous contraintes gouvernent {theme} ?",
                f"Comment mesurer quantitativement les progrès relatifs à {theme} ?",
                f"Quelles architectures augmentent la viabilité de {theme} ?",
            ],
            "status": "proposed",
        }

        self.diagnostics = {
            "primitive": PRIMITIVE,
            "program_counter": self.program_counter,
            "latest_program": program,
        }

        return program

    def step(self) -> dict[str, Any]:
        return self.generate_program()
