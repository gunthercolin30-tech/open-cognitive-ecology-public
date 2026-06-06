
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json


class CivilizationalPeerReviewInterface:
    def __init__(self) -> None:
        self.root = Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "peer_review_interface"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.state_dir / "peer_review_state.json"

    def _load_state(self) -> dict:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "cycles": 0,
            "reviews_received": 0,
            "recommendations_integrated": 0,
            "consensus_events": 0,
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

        methodological_rigor = float(inputs.get("methodological_rigor", 0.96))
        reviewer_agreement = float(inputs.get("reviewer_agreement", 0.94))
        recommendation_integration = float(inputs.get("recommendation_integration", 0.93))
        replication_support = float(inputs.get("replication_support", 0.95))
        transparency_score = float(inputs.get("transparency_score", 0.97))

        reviews_received = int(inputs.get("reviews_received", 3))
        recommendations_integrated = int(inputs.get("recommendations_integrated", 2))

        state["reviews_received"] += max(0, reviews_received)
        state["recommendations_integrated"] += max(0, recommendations_integrated)

        if reviewer_agreement >= 0.90 and replication_support >= 0.90:
            state["consensus_events"] += 1

        state["last_execution_utc"] = datetime.now(timezone.utc).isoformat()

        peer_review_validation_index = max(
            0.0,
            min(
                1.0,
                (
                    methodological_rigor
                    + reviewer_agreement
                    + recommendation_integration
                    + replication_support
                    + transparency_score
                ) / 5.0,
            ),
        )

        externally_validated = peer_review_validation_index >= 0.90

        self._save_state(state)

        return {
            "primitive": "CIVILIZATIONAL_PEER_REVIEW_INTERFACE",
            "cycles": state["cycles"],
            "reviews_received": state["reviews_received"],
            "recommendations_integrated": state["recommendations_integrated"],
            "consensus_events": state["consensus_events"],
            "methodological_rigor": methodological_rigor,
            "reviewer_agreement": reviewer_agreement,
            "recommendation_integration": recommendation_integration,
            "replication_support": replication_support,
            "transparency_score": transparency_score,
            "peer_review_validation_index": peer_review_validation_index,
            "externally_validated": externally_validated,
            "state_path": str(self.state_path),
        }
