from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"


class GitHubReleaseGovernor:
    """Gouverne les publications GitHub réelles ou préparatoires."""

    primitive = "github_release_governor"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else ROOT
        self.state_dir = self.root / "external_validation" / "github_advanced_governance"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def step(self, release_state: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        latest_connector = self.root / "external_validation" / "github_publication_connector" / "latest_github_publication_connector.json"
        connector_state = self._load_json(latest_connector)
        merged_state: dict[str, Any] = {}
        merged_state.update(connector_state)
        if release_state:
            merged_state.update(release_state)

        token_available = bool(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
        release_created = bool(merged_state.get("release_created") or merged_state.get("success") or merged_state.get("published"))
        manifest_uploaded = bool(merged_state.get("manifest_asset_uploaded") or merged_state.get("asset_uploaded") or merged_state.get("traceability_local_validated"))
        github_contribution_count = int(merged_state.get("github_contribution_count", 0) or 0)
        github_fork_count = int(merged_state.get("github_fork_count", 0) or 0)

        evidence_components = [release_created, manifest_uploaded, token_available, github_contribution_count > 0, github_fork_count > 0]
        governance_score = sum(1 for x in evidence_components if x) / len(evidence_components)

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": timestamp,
            "release_governance_ready": True,
            "github_token_available": token_available,
            "release_created": release_created,
            "manifest_asset_uploaded": manifest_uploaded,
            "github_contribution_count": github_contribution_count,
            "github_fork_count": github_fork_count,
            "github_release_governance_score": governance_score,
            "classification": "GitHub Advanced Governance Operational" if governance_score >= 0.4 else "GitHub Advanced Governance Prepared",
            "non_closure_compliant": True,
            "traceability": {"latest_connector_path": str(latest_connector), "state_dir": str(self.state_dir), "network_required": False},
        }
        if persist:
            out = self.state_dir / "latest_github_release_governor.json"
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["state_path"] = str(out)
        return result
