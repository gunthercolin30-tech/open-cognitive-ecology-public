from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ReplicationParticipantTracker:
    """Tracks external replication participants and replication counts."""

    primitive = "replication_participant_tracker"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / "replication_participants"
        self.output_path = self.output_dir / "latest_replication_participants.json"

    def step(self, participants: list[dict[str, Any]] | None = None, persist: bool = True) -> dict[str, Any]:
        timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        if participants is None:
            participants = [
                {
                    "participant_id": "H13-PENDING-INDEPENDENT-REPLICATOR-001",
                    "status": "invited",
                    "independent": True,
                    "replication_validated": False,
                    "evidence_submitted": False,
                }
            ]
        active = [p for p in participants if p.get("status") in {"active", "running", "submitted"}]
        validated = [p for p in participants if p.get("replication_validated") is True]
        independent = [p for p in participants if p.get("independent") is True]
        evidence = [p for p in participants if p.get("evidence_submitted") is True]
        external_replication_count = len(validated)
        independence_ratio = len(independent) / len(participants) if participants else 1.0
        evidence_submission_rate = len(evidence) / len(participants) if participants else 0.0
        state: dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": timestamp,
            "participant_count": len(participants),
            "active_participant_count": len(active),
            "external_replication_count": external_replication_count,
            "validated_replications": len(validated),
            "independence_ratio": independence_ratio,
            "evidence_submission_rate": evidence_submission_rate,
            "governance_compliant": True,
            "non_closure_compliant": True,
            "phenomenological_claim_authorized": False,
            "participants": participants,
            "diagnostics": {
                "h_axis_step": "H13",
                "role": "replication_participant_tracking",
                "empty_input_tolerated": True,
            },
        }
        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.output_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
            state["state_path"] = str(self.output_path)
        return state
