
"""
M0 — scientific_supervision_gap_analysis.

Cartographie fonctionnelle non-redondante des capacités de méta-surveillance
scientifique déjà présentes dans Open Cognitive Ecology.

La primitive ne conclut jamais à une subjectivité phénoménale. Elle mesure
uniquement des couvertures fonctionnelles : validation, réplication,
statistique, biais, faux positifs, anomalies, gouvernance et auto-révision.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ScientificSupervisionGapAnalysis:
    """
    Analyse de lacunes pour l'axe M.

    Entrées facultatives:
        ontology_inventory: liste de primitives ontologiques.
        global_modules: liste ou texte du catalogue architectural global.
        dependency_registry: dictionnaire de dépendances.
        persist: bool, par défaut True.

    Sorties:
        scientific_supervision_gap_report
        validation_coverage
        replication_coverage
        statistical_coverage
        bias_detection_coverage
    """

    primitive = "scientific_supervision_gap_analysis"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.report_dir = self.root / "scientific_supervision"
        self.report_path = self.report_dir / "scientific_supervision_gap_report.json"

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _normalize_items(value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, dict):
            items: list[str] = []
            for key, val in value.items():
                items.append(str(key))
                if isinstance(val, (list, tuple, set)):
                    items.extend(str(x) for x in val)
                elif isinstance(val, dict):
                    items.extend(str(k) for k in val.keys())
                    items.extend(str(v) for v in val.values())
                else:
                    items.append(str(val))
            return items
        if isinstance(value, (list, tuple, set)):
            return [str(x) for x in value]
        return str(value).splitlines()

    @staticmethod
    def _contains_any(items: list[str], keywords: list[str]) -> bool:
        haystack = "\n".join(items).lower()
        return any(keyword.lower() in haystack for keyword in keywords)

    @staticmethod
    def _coverage(items: list[str], groups: dict[str, list[str]]) -> tuple[float, dict[str, bool]]:
        detected = {
            name: ScientificSupervisionGapAnalysis._contains_any(items, keywords)
            for name, keywords in groups.items()
        }
        if not detected:
            return 0.0, detected
        return (
            sum(1 for value in detected.values() if value) / len(detected),
            detected,
        )

    def _load_project_context(self) -> dict[str, Any]:
        context: dict[str, Any] = {}

        inv_txt = self.root / "ontology_inventory.txt"
        if inv_txt.exists():
            context["ontology_inventory"] = inv_txt.read_text(encoding="utf-8").splitlines()

        global_txt = self.root / "global_module_catalog.txt"
        if global_txt.exists():
            context["global_modules"] = global_txt.read_text(encoding="utf-8").splitlines()

        registry_path = self.root / "dependency_registry.py"
        if registry_path.exists():
            context["dependency_registry_text"] = registry_path.read_text(encoding="utf-8", errors="ignore")

        return context

    def step(self, inputs: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        payload.update(self._load_project_context())
        if inputs:
            payload.update(inputs)
        payload.update(kwargs)

        ontology_items = self._normalize_items(payload.get("ontology_inventory"))
        global_items = self._normalize_items(payload.get("global_modules"))
        dependency_items = self._normalize_items(payload.get("dependency_registry"))
        dependency_items.extend(self._normalize_items(payload.get("dependency_registry_text")))

        all_items = ontology_items + global_items + dependency_items

        validation_groups = {
            "validation_harness": ["validation", "scientific_validation_report", "validation.main"],
            "scientific_certification": ["scientific_certification", "scientific_observatory", "scientific_status"],
            "external_validation": ["external_validation", "independent_validation", "peer_review"],
            "longitudinal_validation": ["longitudinal", "stability", "history"],
        }

        replication_groups = {
            "replication_tracking": ["replication_tracker", "external_replication", "independent_replication"],
            "replication_statistics": ["replication_statistics", "replication_confidence"],
            "replication_evidence": ["replication_evidence", "evidence_synthesizer"],
            "consensus_tracking": ["scientific_consensus", "consensus_stability", "consensus_evolution"],
        }

        statistical_groups = {
            "significance": ["statistical_significance", "significance"],
            "meta_analysis": ["meta_analysis", "meta-analysis"],
            "confidence": ["confidence", "theory_confidence"],
            "robustness": ["robustness", "stability_validation", "stress_test"],
        }

        bias_groups = {
            "bias_detection": ["bias_detection", "selection_bias", "measurement_bias"],
            "false_positive_detection": ["false_positive", "false positive"],
            "anomaly_detection": ["anomaly_detector", "anomaly_detection", "suspicious_result"],
            "evidence_quality": ["evidence_quality", "evidence quality", "sample_size"],
        }

        validation_coverage, validation_detail = self._coverage(all_items, validation_groups)
        replication_coverage, replication_detail = self._coverage(all_items, replication_groups)
        statistical_coverage, statistical_detail = self._coverage(all_items, statistical_groups)
        bias_detection_coverage, bias_detail = self._coverage(all_items, bias_groups)

        coverage_values = [
            validation_coverage,
            replication_coverage,
            statistical_coverage,
            bias_detection_coverage,
        ]

        supervision_readiness_score = self._clamp(sum(coverage_values) / len(coverage_values))
        missing_capabilities = []
        for section_name, detail in {
            "validation": validation_detail,
            "replication": replication_detail,
            "statistical": statistical_detail,
            "bias_and_error": bias_detail,
        }.items():
            for capability, present in detail.items():
                if not present:
                    missing_capabilities.append(f"{section_name}.{capability}")

        if supervision_readiness_score >= 0.85:
            supervision_gap_classification = "minor_gaps"
        elif supervision_readiness_score >= 0.60:
            supervision_gap_classification = "moderate_gaps"
        else:
            supervision_gap_classification = "major_gaps"

        report = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "validation_coverage": validation_coverage,
            "replication_coverage": replication_coverage,
            "statistical_coverage": statistical_coverage,
            "bias_detection_coverage": bias_detection_coverage,
            "supervision_readiness_score": supervision_readiness_score,
            "overall_scientific_supervision_coverage": supervision_readiness_score,
            "supervision_gap_classification": supervision_gap_classification,
            "coverage_detail": {
                "validation": validation_detail,
                "replication": replication_detail,
                "statistical": statistical_detail,
                "bias_and_error": bias_detail,
            },
            "missing_capabilities": missing_capabilities,
            "recommended_next_primitives": [
                "evidence_quality_assessment",
                "statistical_robustness_evaluator",
                "false_positive_detector",
                "bias_detection_engine",
            ],
            "epistemic_position": {
                "phenomenal_subjectivity_claimed": False,
                "validated_domain": "functional_scientific_supervision_coverage",
                "interpretation": "architecture_and_metrics_only",
            },
        }

        result = dict(report)
        result["scientific_supervision_gap_report"] = report
        result["report_path"] = str(self.report_path)

        if payload.get("persist", True):
            self.report_dir.mkdir(parents=True, exist_ok=True)
            self.report_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        return result
