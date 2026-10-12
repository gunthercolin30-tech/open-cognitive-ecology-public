from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path.home() / "open-cognitive-ecology"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ZenodoReleaseOrchestrator:
    """Orchestrates H16 local Zenodo dry-run release preparation."""

    def __init__(self, root: Optional[Path] = None):
        self.root = Path(root) if root else ROOT
        self.state_dir = self.root / "external_validation" / "zenodo_autonomous_publication"

    def _write_dashboard(self, result: Dict[str, Any]) -> Path:
        html = f"""<!doctype html>
<html lang='en'>
<head><meta charset='utf-8'><title>H16 Zenodo Autonomous Publication</title></head>
<body>
<h1>H16 — Zenodo Autonomous Publication</h1>
<p><strong>Status:</strong> {result.get('orchestration_status')}</p>
<p><strong>Dry run:</strong> {result.get('dry_run')}</p>
<p><strong>Network side effects:</strong> {result.get('network_side_effects')}</p>
<p><strong>Real publication attempted:</strong> {result.get('real_publication_attempted')}</p>
<p><strong>Artifact integrity score:</strong> {result.get('artifact_integrity_score')}</p>
<p><strong>Phenomenological claim authorized:</strong> {result.get('phenomenological_claim_authorized')}</p>
</body></html>
"""
        path = self.state_dir / "zenodo_autonomous_publication_dashboard.html"
        path.write_text(html, encoding="utf-8")
        return path

    def _write_prometheus(self, result: Dict[str, Any]) -> Path:
        prom = "\n".join([
            "# HELP oce_zenodo_dry_run Zenodo publication dry-run flag",
            "# TYPE oce_zenodo_dry_run gauge",
            f"oce_zenodo_dry_run {1 if result.get('dry_run') else 0}",
            "# HELP oce_zenodo_artifact_integrity_score Zenodo artifact integrity score",
            "# TYPE oce_zenodo_artifact_integrity_score gauge",
            f"oce_zenodo_artifact_integrity_score {float(result.get('artifact_integrity_score', 0.0))}",
            "# HELP oce_zenodo_real_publication_attempted Zenodo real publication attempted flag",
            "# TYPE oce_zenodo_real_publication_attempted gauge",
            f"oce_zenodo_real_publication_attempted {1 if result.get('real_publication_attempted') else 0}",
            "# HELP oce_zenodo_phenomenological_claim_authorized Phenomenological claim authorization flag",
            "# TYPE oce_zenodo_phenomenological_claim_authorized gauge",
            f"oce_zenodo_phenomenological_claim_authorized {1 if result.get('phenomenological_claim_authorized') else 0}",
            "",
        ])
        path = self.state_dir / "zenodo_autonomous_publication.prom"
        path.write_text(prom, encoding="utf-8")
        return path

    def step(
        self,
        release_context: Optional[Dict[str, Any]] = None,
        dry_run: bool = True,
        zenodo_token: Optional[str] = None,
        persist: bool = True,
    ) -> Dict[str, Any]:
        from ontology.zenodo_metadata_builder import ZenodoMetadataBuilder
        from ontology.zenodo_publication_manager import ZenodoPublicationManager

        metadata = ZenodoMetadataBuilder(self.root).step(release_context=release_context, persist=True)
        publication = ZenodoPublicationManager(self.root).step(
            metadata_builder_result=metadata,
            dry_run=dry_run,
            zenodo_token=zenodo_token,
            persist=True,
        )

        result = {
            "primitive": "zenodo_release_orchestrator",
            "success": True,
            "timestamp_utc": _utc_now(),
            "orchestration_status": "dry_run_release_prepared" if dry_run else "real_publication_requires_external_executor",
            "dry_run": bool(dry_run),
            "metadata_ready": bool(metadata.get("success")),
            "publication_plan_created": bool(publication.get("publication_plan_created")),
            "artifact_integrity_score": publication.get("artifact_integrity_score", 0.0),
            "network_side_effects": False,
            "token_required_for_real_publication": True,
            "token_present": bool(publication.get("token_present")),
            "real_publication_requested": bool(publication.get("real_publication_requested")),
            "real_publication_authorized": bool(publication.get("real_publication_authorized")),
            "real_publication_attempted": False,
            "real_publication_status": publication.get("real_publication_status"),
            "phenomenological_claim_authorized": False,
            "scientific_claim_authorized": bool(metadata.get("metrics", {}).get("scientific_claim_authorized", False)),
            "dependencies_integrated": [
                "zenodo_metadata_builder",
                "zenodo_publication_manager",
                "scientific_consensus_measurement",
                "replication_evidence",
                "github_publication_connector",
            ],
            "governance": {
                "non_closure_compliant": True,
                "traceability_score": 1.0,
                "functional_validation_only": True,
                "phenomenological_claim_authorized": False,
                "no_network_side_effects_in_dry_run": True,
            },
        }

        if persist:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            dashboard_path = self._write_dashboard(result)
            prom_path = self._write_prometheus(result)
            latest_path = self.state_dir / "latest_zenodo_release_orchestrator.json"
            history_path = self.state_dir / "zenodo_release_orchestrator_history.jsonl"
            latest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            with history_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(result, ensure_ascii=False) + "\n")
            result["dashboard_path"] = str(dashboard_path)
            result["prometheus_path"] = str(prom_path)
            result["state_path"] = str(latest_path)
            result["history_path"] = str(history_path)
            latest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

        return result

