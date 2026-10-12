
"""
M1 — evidence_quality_assessment.

Évalue la qualité fonctionnelle des preuves produites ou agrégées par Open
Cognitive Ecology. Cette primitive reste strictement épistémique et métrique :
elle n'infère aucune subjectivité phénoménale et ne valide que des propriétés
fonctionnelles observables.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


class EvidenceQualityAssessment:
    """
    M1 — évaluation de la qualité des preuves.

    Mesures principales:
        sample_size_score
        replication_support
        evidence_consistency
        evidence_quality_score

    Décisions:
        weak_evidence
        moderate_evidence
        strong_evidence
    """

    primitive = "evidence_quality_assessment"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.report_dir = self.root / "scientific_supervision"
        self.report_path = self.report_dir / "evidence_quality_assessment_report.json"

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _as_float(value: Any, default: float = 0.0) -> float:
        try:
            if value is None or isinstance(value, bool):
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _normalize_records(value: Any) -> list[dict[str, Any]]:
        if value is None:
            return []
        if isinstance(value, dict):
            if isinstance(value.get("evidence_items"), list):
                return EvidenceQualityAssessment._normalize_records(value["evidence_items"])
            if isinstance(value.get("records"), list):
                return EvidenceQualityAssessment._normalize_records(value["records"])
            return [value]
        if isinstance(value, (list, tuple, set)):
            records: list[dict[str, Any]] = []
            for item in value:
                if isinstance(item, dict):
                    records.append(item)
                else:
                    records.append({"value": item})
            return records
        return [{"value": value}]

    @staticmethod
    def _extract_scores(records: list[dict[str, Any]]) -> list[float]:
        score_keys = (
            "score",
            "success_rate",
            "confidence",
            "confidence_score",
            "validation_score",
            "replication_score",
            "consensus_score",
            "evidence_score",
            "quality_score",
            "statistical_support",
        )
        scores: list[float] = []
        for record in records:
            for key in score_keys:
                if key in record:
                    value = EvidenceQualityAssessment._as_float(record.get(key), default=-1.0)
                    if value >= 0.0:
                        scores.append(EvidenceQualityAssessment._clamp(value))
                        break
        return scores

    @staticmethod
    def _count_positive(records: list[dict[str, Any]], keys: tuple[str, ...]) -> int:
        count = 0
        for record in records:
            text = json.dumps(record, ensure_ascii=False, default=str).lower()
            if any(key.lower() in text for key in keys):
                count += 1
        return count

    def _load_default_context(self) -> dict[str, Any]:
        context: dict[str, Any] = {}

        # Lightweight project-derived context. The module does not scan full archives;
        # it only samples canonical report directories when present.
        candidates = [
            self.root / "runtime_experiments" / "scientific_meta_analysis",
            self.root / "runtime_experiments" / "scientific_consensus",
            self.root / "runtime_experiments" / "scientific_theory_confidence",
            self.root / "external_validation" / "replication_evidence",
            self.root / "external_validation" / "replication_statistical_validation",
            self.root / "external_validation" / "scientific_consensus_measurement",
        ]

        evidence_items: list[dict[str, Any]] = []
        for directory in candidates:
            if not directory.exists():
                continue
            for path in sorted(directory.rglob("*.json"))[:50]:
                try:
                    data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
                    if isinstance(data, dict):
                        data.setdefault("source_path", str(path.relative_to(self.root)))
                        evidence_items.append(data)
                    elif isinstance(data, list):
                        for item in data[:20]:
                            if isinstance(item, dict):
                                item = dict(item)
                                item.setdefault("source_path", str(path.relative_to(self.root)))
                                evidence_items.append(item)
                except Exception:
                    continue

        if evidence_items:
            context["evidence_items"] = evidence_items
        return context

    def _sample_size_score(self, records: list[dict[str, Any]], explicit_sample_size: Any = None) -> float:
        sample_size = int(max(0, self._as_float(explicit_sample_size, default=0.0)))
        if sample_size <= 0:
            sample_size = len(records)
        if sample_size <= 0:
            return 0.0
        # Saturating scale: 1 -> .10, 5 -> .50, 10+ -> 1.0.
        return self._clamp(sample_size / 10.0)

    def _replication_support(self, records: list[dict[str, Any]], explicit_replications: Any = None) -> float:
        replication_count = int(max(0, self._as_float(explicit_replications, default=0.0)))
        if replication_count <= 0:
            replication_count = self._count_positive(
                records,
                (
                    "replication",
                    "replicated",
                    "independent_replication",
                    "external_replication",
                    "replication_success",
                ),
            )
        if replication_count <= 0:
            return 0.0
        # 4 independent replication signals are enough for full local support.
        return self._clamp(replication_count / 4.0)

    def _evidence_consistency(self, records: list[dict[str, Any]], explicit_consistency: Any = None) -> float:
        explicit = self._as_float(explicit_consistency, default=-1.0)
        if explicit >= 0.0:
            return self._clamp(explicit)

        scores = self._extract_scores(records)
        if len(scores) >= 2:
            dispersion = pstdev(scores)
            mean_support = mean(scores)
            return self._clamp((1.0 - dispersion) * 0.6 + mean_support * 0.4)
        if len(scores) == 1:
            return self._clamp(scores[0] * 0.8)

        consistency_signals = self._count_positive(
            records,
            ("consistent", "consensus", "stable", "validated", "success"),
        )
        if records:
            return self._clamp(consistency_signals / len(records))
        return 0.0

    def step(self, inputs: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        payload.update(self._load_default_context())
        if inputs:
            payload.update(inputs)
        payload.update(kwargs)

        records = self._normalize_records(
            payload.get("evidence_items", payload.get("evidence_records", payload.get("records")))
        )

        sample_size_score = self._sample_size_score(records, payload.get("sample_size"))
        replication_support = self._replication_support(records, payload.get("replication_count"))
        evidence_consistency = self._evidence_consistency(records, payload.get("evidence_consistency"))

        methodological_transparency = self._clamp(
            self._as_float(payload.get("methodological_transparency"), default=0.0)
        )
        if methodological_transparency == 0.0 and records:
            transparency_hits = self._count_positive(
                records,
                ("method", "protocol", "source", "trace", "path", "timestamp"),
            )
            methodological_transparency = self._clamp(transparency_hits / len(records))

        anomaly_penalty = self._clamp(self._as_float(payload.get("anomaly_penalty"), default=0.0))
        bias_penalty = self._clamp(self._as_float(payload.get("bias_penalty"), default=0.0))

        raw_quality = (
            0.30 * sample_size_score
            + 0.30 * replication_support
            + 0.30 * evidence_consistency
            + 0.10 * methodological_transparency
        )
        evidence_quality_score = self._clamp(raw_quality * (1.0 - 0.5 * anomaly_penalty) * (1.0 - 0.5 * bias_penalty))

        if evidence_quality_score >= 0.75:
            evidence_decision = "strong_evidence"
        elif evidence_quality_score >= 0.45:
            evidence_decision = "moderate_evidence"
        else:
            evidence_decision = "weak_evidence"

        report = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "evidence_item_count": len(records),
            "sample_size_score": sample_size_score,
            "replication_support": replication_support,
            "evidence_consistency": evidence_consistency,
            "methodological_transparency": methodological_transparency,
            "anomaly_penalty": anomaly_penalty,
            "bias_penalty": bias_penalty,
            "evidence_quality_score": evidence_quality_score,
            "evidence_decision": evidence_decision,
            "weak_evidence": evidence_decision == "weak_evidence",
            "moderate_evidence": evidence_decision == "moderate_evidence",
            "strong_evidence": evidence_decision == "strong_evidence",
            "diagnostics": {
                "weights": {
                    "sample_size_score": 0.30,
                    "replication_support": 0.30,
                    "evidence_consistency": 0.30,
                    "methodological_transparency": 0.10,
                },
                "penalty_model": "quality * (1 - .5*anomaly_penalty) * (1 - .5*bias_penalty)",
                "input_mode": "project_context_plus_optional_payload",
            },
            "epistemic_position": {
                "phenomenal_subjectivity_claimed": False,
                "validated_domain": "functional_evidence_quality_assessment",
                "interpretation": "evidence_metrics_only",
            },
        }

        result = dict(report)
        result["evidence_quality_assessment_report"] = report
        result["report_path"] = str(self.report_path)

        if payload.get("persist", True):
            self.report_dir.mkdir(parents=True, exist_ok=True)
            self.report_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        return result
