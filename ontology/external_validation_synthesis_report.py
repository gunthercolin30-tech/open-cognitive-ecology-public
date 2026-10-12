from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


class ExternalValidationSynthesisReport:
    primitive = "external_validation_synthesis_report"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / "civilizational_scientific_certification"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _read_json(self, path: Path) -> Any:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _as_dict(self, value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        if isinstance(value, list):
            dict_items = [x for x in value if isinstance(x, dict)]
            return {"items": dict_items, "item_count": len(dict_items), "success": any(bool(x.get("success", x.get("overall_success", False))) for x in dict_items)}
        return {}

    def _signal(self, relative: str) -> dict[str, Any]:
        return self._as_dict(self._read_json(self.root / relative))

    def step(self, persist: bool = True) -> dict[str, Any]:
        h18 = self._signal("external_validation/independent_validation_observatory/latest_independent_validation_observatory.json")
        archive = self._signal("external_validation/independent_validation_observatory/latest_validation_history_archive.json")
        github = self._signal("external_validation/github_publication_connector/latest_github_publication_connector.json")
        github_governance = self._signal("external_validation/github_advanced_governance/latest_github_release_governor.json")
        github_feedback = self._signal("external_validation/github_replication_feedback/latest_github_replication_feedback.json")
        zenodo = self._signal("external_validation/zenodo_real_publication/latest_zenodo_publication.json")
        consensus = self._signal("external_validation/scientific_consensus_measurement/latest_scientific_consensus_analysis.json")
        validation = self._signal("scientific_validation_report.json")

        github_publication_validated = bool(github.get("success") and (github.get("release_created") or github.get("real_publication_status") in {"attempted", "published"}))
        github_governance_validated = bool(github_governance.get("success"))
        zenodo_publication_validated = bool(zenodo.get("success") and zenodo.get("submitted"))
        h18_validated = bool(h18.get("success") and h18.get("observatory_ready"))
        validation_error_free = bool(validation.get("overall_success", False) or validation.get("diagnostics", {}).get("error_count") == 0)

        external_replication_count = int(h18.get("external_replication_count", 0) or 0)
        validation_growth_rate = float(h18.get("validation_growth_rate", 0.0) or 0.0)
        validation_stability_index = float(h18.get("validation_stability_index", 0.0) or 0.0)
        scientific_consensus = float(consensus.get("scientific_consensus_score", consensus.get("consensus_score", h18.get("scientific_consensus", 0.0))) or 0.0)
        record_count = int(archive.get("record_count", 0) or 0)
        successful_record_count = int(archive.get("successful_record_count", 0) or 0)
        replication_feedback_count = int(github_feedback.get("replication_feedback_count", 0) or 0)

        evidence_scores = [
            1.0 if github_publication_validated else 0.0,
            1.0 if github_governance_validated else 0.0,
            1.0 if zenodo_publication_validated else 0.0,
            1.0 if h18_validated else 0.0,
            1.0 if validation_error_free else 0.0,
            min(1.0, external_replication_count / 1.0),
            validation_stability_index,
            min(1.0, record_count / 100.0),
            min(1.0, successful_record_count / 50.0),
        ]
        external_validation_synthesis_score = mean(evidence_scores)

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "stage": "H19",
            "external_validation_synthesis_ready": True,
            "external_validation_synthesis_score": round(external_validation_synthesis_score, 6),
            "github_publication_validated": github_publication_validated,
            "github_governance_validated": github_governance_validated,
            "zenodo_publication_validated": zenodo_publication_validated,
            "independent_validation_observatory_validated": h18_validated,
            "validation_error_free": validation_error_free,
            "external_replication_count": external_replication_count,
            "validation_growth_rate": round(max(0.0, min(1.0, validation_growth_rate)), 6),
            "validation_stability_index": round(max(0.0, min(1.0, validation_stability_index)), 6),
            "scientific_consensus": round(max(0.0, min(1.0, scientific_consensus)), 6),
            "replication_feedback_count": replication_feedback_count,
            "record_count": record_count,
            "successful_record_count": successful_record_count,
            "evidence_sources": {
                "github_publication": "external_validation/github_publication_connector/latest_github_publication_connector.json",
                "github_governance": "external_validation/github_advanced_governance/latest_github_release_governor.json",
                "github_feedback": "external_validation/github_replication_feedback/latest_github_replication_feedback.json",
                "zenodo_real_publication": "external_validation/zenodo_real_publication/latest_zenodo_publication.json",
                "independent_validation_observatory": "external_validation/independent_validation_observatory/latest_independent_validation_observatory.json",
                "scientific_consensus": "external_validation/scientific_consensus_measurement/latest_scientific_consensus_analysis.json",
            },
            "phenomenological_claim_authorized": False,
            "epistemic_scope": "functional_indicators_only",
            "non_closure_compliant": True,
        }

        if persist:
            state_path = self.output_dir / "latest_external_validation_synthesis_report.json"
            state_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            history_path = self.output_dir / "external_validation_synthesis_report.jsonl"
            with history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            result["state_path"] = str(state_path)
            result["history_path"] = str(history_path)
        return result
