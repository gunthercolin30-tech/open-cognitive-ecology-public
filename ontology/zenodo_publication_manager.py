from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
    return default


class ZenodoPublicationManager:
    """Governed Zenodo publication manager.

    Default behavior is dry-run only. It records the publication plan, required
    artifacts and authorization state but never performs network publication.
    """

    def __init__(self, root: Optional[Path] = None):
        self.root = Path(root) if root else ROOT
        self.state_dir = self.root / "external_validation" / "zenodo_autonomous_publication"

    def _artifact_manifest(self) -> List[Dict[str, Any]]:
        candidates = [
            "ontology_inventory.txt",
            "ontology_integration_report.txt",
            "scientific_validation_report.json",
            "external_validation/scientific_consensus_measurement/latest_scientific_consensus_analysis.json",
            "external_validation/scientific_consensus_measurement/latest_consensus_stability.json",
            "external_validation/replication_evidence/latest_replication_confidence_estimate.json",
            "external_validation/github_publication_connector/latest_github_publication_connector.json",
            ".zenodo.json",
            "CITATION.cff",
        ]
        artifacts = []
        for rel in candidates:
            path = self.root / rel
            artifacts.append({
                "relative_path": rel,
                "exists": path.exists(),
                "size_bytes": path.stat().st_size if path.exists() else 0,
            })
        return artifacts

    def step(
        self,
        metadata_builder_result: Optional[Dict[str, Any]] = None,
        dry_run: bool = True,
        zenodo_token: Optional[str] = None,
        persist: bool = True,
    ) -> Dict[str, Any]:
        if metadata_builder_result is None:
            try:
                from ontology.zenodo_metadata_builder import ZenodoMetadataBuilder
                metadata_builder_result = ZenodoMetadataBuilder(self.root).step(persist=True)
            except Exception as exc:
                metadata_builder_result = {"success": False, "error": repr(exc)}

        env_token_present = bool(os.environ.get("ZENODO_TOKEN") or os.environ.get("ZENODO_ACCESS_TOKEN"))
        explicit_token_present = bool(zenodo_token)
        token_present = explicit_token_present or env_token_present

        real_publication_requested = not bool(dry_run)
        real_publication_authorized = bool(real_publication_requested and token_present)

        artifacts = self._artifact_manifest()
        existing_count = sum(1 for a in artifacts if a["exists"])
        artifact_integrity_score = existing_count / len(artifacts) if artifacts else 0.0

        manifest = {
            "publication_id": "H16-ZENODO-DRY-RUN-001",
            "timestamp_utc": _utc_now(),
            "dry_run": bool(dry_run),
            "network_side_effects": False,
            "real_publication_requested": real_publication_requested,
            "token_present": token_present,
            "real_publication_authorized": real_publication_authorized,
            "real_publication_attempted": False,
            "metadata_ready": bool(metadata_builder_result.get("success")),
            "artifact_integrity_score": round(artifact_integrity_score, 6),
            "artifacts": artifacts,
            "governance": {
                "non_closure_compliant": True,
                "traceability_score": 1.0,
                "functional_validation_only": True,
                "phenomenological_claim_authorized": False,
                "requires_explicit_token_for_real_publication": True,
                "requires_separate_real_publication_step": True,
            },
        }

        result = {
            "primitive": "zenodo_publication_manager",
            "success": True,
            "timestamp_utc": _utc_now(),
            "dry_run": bool(dry_run),
            "publication_plan_created": True,
            "metadata_ready": bool(metadata_builder_result.get("success")),
            "artifact_integrity_score": round(artifact_integrity_score, 6),
            "network_side_effects": False,
            "token_required_for_real_publication": True,
            "token_present": token_present,
            "real_publication_requested": real_publication_requested,
            "real_publication_authorized": real_publication_authorized,
            "real_publication_attempted": False,
            "real_publication_status": "dry_run_only" if dry_run else "blocked_without_network_execution",
            "manifest": manifest,
            "governance": manifest["governance"],
            "epistemic_scope": "publication_traceability_only_no_phenomenological_claim",
        }

        if persist:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = self.state_dir / "zenodo_publication_manifest_dry_run.json"
            latest_path = self.state_dir / "latest_zenodo_publication_manager.json"
            manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
            latest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["manifest_path"] = str(manifest_path)
            result["state_path"] = str(latest_path)

        return result

