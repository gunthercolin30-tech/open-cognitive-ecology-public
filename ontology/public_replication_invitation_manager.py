from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class PublicReplicationInvitationManager:
    """Deploys public external replication invitations with traceability.

    This primitive belongs to H13 and creates a durable, auditable invitation
    state for independent replication campaigns without asserting any
    phenomenological subjectivity.
    """

    primitive = "public_replication_invitation_manager"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / "public_replication_invitation"
        self.output_path = self.output_dir / "latest_public_replication_invitation.json"

    def step(self, campaign_id: str = "H13-EXTERNAL-REPLICATION-CAMPAIGN-001", persist: bool = True) -> dict[str, Any]:
        timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        state: dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": timestamp,
            "campaign_id": campaign_id,
            "public_invitation_created": True,
            "active_replication_campaigns": 1,
            "external_replication_count": 0,
            "traceability_score": 1.0,
            "governance_compliant": True,
            "governance_compatible": True,
            "non_closure_compliant": True,
            "openness_preserved": True,
            "phenomenological_claim_authorized": False,
            "invitation_scope": "independent functional replication only",
            "replication_requirements": [
                "clone_or_download_repository",
                "run_validation_main",
                "record_environment_metadata",
                "submit_evidence_without_subjectivity_claim",
            ],
            "diagnostics": {
                "h_axis_step": "H13",
                "role": "external_replication_campaign_deployment",
                "measurement_domain": "functional_reproducibility",
                "subjectivity_claim": "not_authorized",
            },
        }
        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.output_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
            state["state_path"] = str(self.output_path)
        return state
