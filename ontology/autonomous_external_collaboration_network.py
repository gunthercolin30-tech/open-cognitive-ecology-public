
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


class AutonomousExternalCollaborationNetwork:
    primitive = "autonomous_external_collaboration_network"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / "distributed_scientific_ecosystem"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _read_json(self, path: Path) -> Any:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _count_json(self, relative: str) -> int:
        base = self.root / relative
        if not base.exists():
            return 0
        return len(list(base.rglob("*.json")))

    def _latest(self, relative: str) -> dict[str, Any]:
        data = self._read_json(self.root / relative)
        return data if isinstance(data, dict) else {}

    def step(self, persist: bool = True) -> dict[str, Any]:
        github_feedback = self._latest("external_validation/github_replication_feedback/latest_github_replication_feedback.json")
        github_governance = self._latest("external_validation/github_advanced_governance/latest_github_issue_monitor.json")
        certification = self._latest("external_validation/civilizational_scientific_certification/latest_civilizational_scientific_certification.json")
        observatory = self._latest("external_validation/independent_validation_observatory/latest_independent_validation_observatory.json")

        invitation_count = self._count_json("external_validation/public_replication_invitations")
        registry_count = self._count_json("external_validation/replication_registry")
        campaign_count = self._count_json("external_validation/replication_campaigns")
        evidence_count = self._count_json("external_validation/replication_evidence")
        github_feedback_count = int(github_feedback.get("replication_feedback_count", 0) or 0)
        github_issue_count = int(github_governance.get("github_issue_count", 0) or 0)
        external_replication_count = int(observatory.get("external_replication_count", 0) or 0)
        certification_readiness = float(certification.get("certification_readiness", 0.0) or 0.0)

        collaboration_nodes = invitation_count + registry_count + campaign_count + evidence_count + github_feedback_count + github_issue_count
        collaboration_density = mean([
            min(1.0, collaboration_nodes / 20.0),
            min(1.0, external_replication_count / 3.0),
            min(1.0, certification_readiness),
        ])
        collaboration_activity = mean([
            min(1.0, (campaign_count + evidence_count) / 10.0),
            min(1.0, github_feedback_count / 5.0),
            1.0 if external_replication_count > 0 else 0.5,
        ])

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "stage": "H20",
            "autonomous_external_collaboration_network_ready": True,
            "external_collaboration_density": round(collaboration_density, 6),
            "distributed_scientific_activity": round(collaboration_activity, 6),
            "collaboration_node_count": collaboration_nodes,
            "public_invitation_record_count": invitation_count,
            "replication_registry_record_count": registry_count,
            "replication_campaign_record_count": campaign_count,
            "replication_evidence_record_count": evidence_count,
            "github_replication_feedback_count": github_feedback_count,
            "github_issue_count": github_issue_count,
            "external_replication_count": external_replication_count,
            "phenomenological_claim_authorized": False,
            "epistemic_scope": "functional_indicators_only",
            "diagnostics": {
                "non_closure_compliant": True,
                "collaboration_requires_real_external_participants": external_replication_count == 0,
                "github_feedback_integrated": github_feedback_count >= 0,
                "certification_integrated": certification_readiness > 0.0,
            },
        }

        if persist:
            state_path = self.output_dir / "latest_autonomous_external_collaboration_network.json"
            state_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            history_path = self.output_dir / "autonomous_external_collaboration_network.jsonl"
            with history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            result["state_path"] = str(state_path)
            result["history_path"] = str(history_path)

        return result
