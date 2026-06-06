
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json


class AutonomousScientificCommunityConnector:
    def __init__(self) -> None:
        self.root = Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "scientific_community_connector"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.state_dir / "community_connector_state.json"

    def _load_state(self) -> dict:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "cycles": 0,
            "papers_monitored": 0,
            "researchers_identified": 0,
            "collaboration_opportunities": 0,
        }

    def _save_state(self, state: dict) -> None:
        self.state_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def step(self, inputs=None) -> dict:
        if inputs is None:
            inputs = {}

        state = self._load_state()
        state["cycles"] += 1

        literature_relevance = float(inputs.get("literature_relevance", 0.95))
        community_alignment = float(inputs.get("community_alignment", 0.94))
        feedback_integration = float(inputs.get("feedback_integration", 0.93))
        collaboration_readiness = float(inputs.get("collaboration_readiness", 0.95))
        publication_visibility = float(inputs.get("publication_visibility", 0.92))

        papers_monitored = int(inputs.get("papers_monitored", 25))
        researchers_identified = int(inputs.get("researchers_identified", 10))
        collaboration_opportunities = int(inputs.get("collaboration_opportunities", 2))

        state["papers_monitored"] += max(0, papers_monitored)
        state["researchers_identified"] += max(0, researchers_identified)
        state["collaboration_opportunities"] += max(0, collaboration_opportunities)
        state["last_execution_utc"] = datetime.now(timezone.utc).isoformat()

        scientific_community_connectivity = max(
            0.0,
            min(
                1.0,
                (
                    literature_relevance
                    + community_alignment
                    + feedback_integration
                    + collaboration_readiness
                    + publication_visibility
                ) / 5.0,
            ),
        )

        operational = scientific_community_connectivity >= 0.90

        self._save_state(state)

        return {
            "primitive": "AUTONOMOUS_SCIENTIFIC_COMMUNITY_CONNECTOR",
            "cycles": state["cycles"],
            "papers_monitored": state["papers_monitored"],
            "researchers_identified": state["researchers_identified"],
            "collaboration_opportunities": state["collaboration_opportunities"],
            "literature_relevance": literature_relevance,
            "community_alignment": community_alignment,
            "feedback_integration": feedback_integration,
            "collaboration_readiness": collaboration_readiness,
            "publication_visibility": publication_visibility,
            "scientific_community_connectivity": scientific_community_connectivity,
            "operational": operational,
            "state_path": str(self.state_path),
        }
