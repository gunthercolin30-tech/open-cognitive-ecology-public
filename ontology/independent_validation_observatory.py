from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from ontology.validation_history_archive import ValidationHistoryArchive
from ontology.replication_statistics_engine import ReplicationStatisticsEngine


class IndependentValidationObservatory:
    primitive = "independent_validation_observatory"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / "independent_validation_observatory"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _read_json(self, path: Path) -> dict[str, Any]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def step(self, persist: bool = True) -> dict[str, Any]:
        archive = ValidationHistoryArchive(self.root).step(persist=persist)
        stats = ReplicationStatisticsEngine(self.root).step(archive, persist=persist)

        github_real = self._read_json(self.root / "external_validation" / "github_publication_connector" / "latest_github_publication_connector.json")
        zenodo_real = self._read_json(self.root / "external_validation" / "zenodo_real_publication" / "latest_zenodo_publication.json")
        consensus = self._read_json(self.root / "external_validation" / "scientific_consensus_measurement" / "latest_scientific_consensus_analysis.json")

        github_publication_validated = bool(github_real.get("success") and (github_real.get("release_created") or github_real.get("real_publication_status") in {"attempted", "published"}))
        zenodo_publication_validated = bool(zenodo_real.get("success") and zenodo_real.get("submitted"))
        consensus_score = float(consensus.get("scientific_consensus_score", consensus.get("consensus_score", 0.0)) or 0.0)

        external_replication_count = int(stats.get("external_replication_count", 0) or 0)
        validation_growth_rate = float(stats.get("validation_growth_rate", 0.0) or 0.0)
        validation_stability_index = float(stats.get("validation_stability_index", 0.0) or 0.0)
        publication_traceability_score = mean([1.0 if github_publication_validated else 0.0, 1.0 if zenodo_publication_validated else 0.0])
        observatory_readiness = mean([
            min(1.0, float(archive.get("record_count", 0) or 0) / 10.0),
            validation_stability_index,
            publication_traceability_score,
            min(1.0, consensus_score),
        ])

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "stage": "H18",
            "observatory_ready": True,
            "external_replication_count": external_replication_count,
            "validation_growth_rate": round(validation_growth_rate, 6),
            "validation_stability_index": round(validation_stability_index, 6),
            "scientific_consensus": round(consensus_score, 6),
            "github_publication_validated": github_publication_validated,
            "zenodo_publication_validated": zenodo_publication_validated,
            "publication_traceability_score": round(publication_traceability_score, 6),
            "observatory_readiness": round(observatory_readiness, 6),
            "validation_claim": "longitudinal_observatory_active",
            "scientific_claim_authorized": external_replication_count > 0,
            "phenomenological_claim_authorized": False,
            "epistemic_scope": "functional_indicators_only",
            "archive_state_path": archive.get("state_path"),
            "statistics_state_path": stats.get("state_path"),
            "diagnostics": {
                "record_count": archive.get("record_count", 0),
                "successful_record_count": archive.get("successful_record_count", 0),
                "pending_independent_replication": external_replication_count == 0,
                "h18_role": "measure_longitudinal_external_validation_without_overclaiming",
                "non_closure_compliant": True,
            },
        }
        if persist:
            state_path = self.output_dir / "latest_independent_validation_observatory.json"
            state_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            history_path = self.output_dir / "independent_validation_observatory.jsonl"
            with history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\\n")
            result["state_path"] = str(state_path)
            result["history_path"] = str(history_path)
        return result
