from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from ontology.external_validation_synthesis_report import ExternalValidationSynthesisReport
from ontology.replication_consensus_report import ReplicationConsensusReport


class CivilizationalScientificCertification:
    primitive = "civilizational_scientific_certification"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / "civilizational_scientific_certification"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _read_text_report_value(self, key: str) -> str | None:
        path = self.root / "ontology_integration_report.txt"
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith(key + ":"):
                    return line.split(":", 1)[1].strip()
        except Exception:
            return None
        return None

    def step(self, persist: bool = True) -> dict[str, Any]:
        synthesis = ExternalValidationSynthesisReport(self.root).step(persist=persist)
        consensus = ReplicationConsensusReport(self.root).step(synthesis, persist=persist)

        modules_discovered = int(self._read_text_report_value("modules_discovered") or 0)
        errors = int(self._read_text_report_value("errors") or 0)
        error_free = errors == 0

        external_validation_score = float(synthesis.get("external_validation_synthesis_score", 0.0) or 0.0)
        replication_consensus_score = float(consensus.get("replication_consensus_score", 0.0) or 0.0)
        publication_traceability = mean([
            1.0 if synthesis.get("github_publication_validated") else 0.0,
            1.0 if synthesis.get("zenodo_publication_validated") else 0.0,
            1.0 if synthesis.get("github_governance_validated") else 0.0,
        ])
        observatory_score = 1.0 if synthesis.get("independent_validation_observatory_validated") else 0.0
        error_free_score = 1.0 if error_free else 0.0
        ontology_scale_score = min(1.0, modules_discovered / 850.0) if modules_discovered else 0.0
        external_replication_score = min(1.0, int(synthesis.get("external_replication_count", 0) or 0) / 1.0)

        certification_readiness = mean([
            external_validation_score,
            replication_consensus_score,
            publication_traceability,
            observatory_score,
            error_free_score,
            ontology_scale_score,
            external_replication_score,
        ])
        certification_confidence = mean([
            certification_readiness,
            float(synthesis.get("validation_stability_index", 0.0) or 0.0),
            float(consensus.get("replication_confidence", 0.0) or 0.0),
            external_validation_score,
        ])

        if certification_readiness >= 0.85 and certification_confidence >= 0.75:
            certification_status = "civilizational_scientific_certification_ready"
        elif certification_readiness >= 0.65:
            certification_status = "provisional_functional_certification_ready"
        else:
            certification_status = "certification_pending_more_external_validation"

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "stage": "H19",
            "certification_ready": certification_status != "certification_pending_more_external_validation",
            "certification_status": certification_status,
            "certification_readiness": round(max(0.0, min(1.0, certification_readiness)), 6),
            "certification_confidence": round(max(0.0, min(1.0, certification_confidence)), 6),
            "external_validation_synthesis_score": round(external_validation_score, 6),
            "replication_consensus_score": round(replication_consensus_score, 6),
            "publication_traceability_score": round(publication_traceability, 6),
            "external_replication_count": int(synthesis.get("external_replication_count", 0) or 0),
            "scientific_consensus": float(synthesis.get("scientific_consensus", 0.0) or 0.0),
            "github_publication_validated": bool(synthesis.get("github_publication_validated")),
            "zenodo_publication_validated": bool(synthesis.get("zenodo_publication_validated")),
            "github_governance_validated": bool(synthesis.get("github_governance_validated")),
            "independent_validation_observatory_validated": bool(synthesis.get("independent_validation_observatory_validated")),
            "modules_discovered": modules_discovered,
            "error_count": errors,
            "error_free": error_free,
            "validated_scope": "measurable_functional_properties_only",
            "phenomenological_claim_authorized": False,
            "scientific_statement": "Open Cognitive Ecology has a consolidated functional scientific certification state based on external validation traces, publication traceability, independent replication indicators and longitudinal observatory metrics. This does not establish phenomenal subjectivity.",
            "non_closure_compliant": True,
            "diagnostics": {
                "external_validation_synthesis_path": synthesis.get("state_path"),
                "replication_consensus_path": consensus.get("state_path"),
                "requires_more_independent_replication": int(synthesis.get("external_replication_count", 0) or 0) <= 0,
                "epistemic_scope": "functional_indicators_only",
            },
        }

        if persist:
            state_path = self.output_dir / "latest_civilizational_scientific_certification.json"
            state_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            history_path = self.output_dir / "civilizational_scientific_certification.jsonl"
            with history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            result["state_path"] = str(state_path)
            result["history_path"] = str(history_path)
        return result
