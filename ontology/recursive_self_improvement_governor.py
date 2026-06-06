"""
Recursive Self Improvement Governor.

Supervises and records self-modification proposals while enforcing
constitutional and reversibility constraints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
import json

PRIMITIVE = "RECURSIVE_SELF_IMPROVEMENT_GOVERNOR"

DEPENDENCIES = [
    "constitutional_alert_system",
    "autonomous_publication_pipeline",
    "collective_research_program_manager",
    "non_closure",
    "constitutional_alignment",
]


@dataclass
class RecursiveSelfImprovementGovernor:
    output_dir: Path = Path("self_improvement_governance")
    proposal_counter: int = 0
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def evaluate_proposal(
        self,
        proposal: dict[str, Any] | None = None,
        constitutional_alignment: float = 1.0,
        non_closure: float = 1.0,
        reversibility: float = 1.0,
    ) -> dict[str, Any]:
        proposal = proposal or {
            "title": "Default self-improvement proposal",
            "description": "No explicit proposal provided.",
        }

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.proposal_counter += 1

        approved = (
            constitutional_alignment >= 0.85
            and non_closure >= 0.85
            and reversibility >= 0.85
        )

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        record = {
            "proposal_id": f"RSIG-{self.proposal_counter:04d}",
            "timestamp": timestamp,
            "proposal": proposal,
            "constitutional_alignment": constitutional_alignment,
            "non_closure": non_closure,
            "reversibility": reversibility,
            "approved": approved,
        }

        json_path = self.output_dir / f"{record['proposal_id']}_{timestamp}.json"
        json_path.write_text(
            json.dumps(record, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        self.diagnostics = {
            "primitive": PRIMITIVE,
            "proposal_counter": self.proposal_counter,
            "approved": approved,
            "record_path": str(json_path),
        }

        return self.diagnostics

    def step(self) -> dict[str, Any]:
        return self.evaluate_proposal()
