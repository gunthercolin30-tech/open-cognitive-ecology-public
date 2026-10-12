
"""
M2 — statistical_robustness_evaluator.

Évalue la robustesse statistique fonctionnelle des résultats produits ou
agrégés par Open Cognitive Ecology. Cette primitive reste strictement métrique:
elle ne formule aucune assertion de subjectivité phénoménale et ne valide que
des propriétés observables de confiance, d'effet, de stabilité et de fragilité.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


class StatisticalRobustnessEvaluator:
    """
    M2 — évaluation de robustesse statistique.

    Mesures principales:
        confidence_score
        effect_size_score
        variance_stability
        statistical_robustness_score

    Détection:
        fragile_results
    """

    primitive = "statistical_robustness_evaluator"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.report_dir = self.root / "scientific_supervision"
        self.report_path = self.report_dir / "statistical_robustness_evaluator_report.json"

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
            for key in (
                "results",
                "result_series",
                "measurements",
                "observations",
                "evidence_items",
                "records",
            ):
                if isinstance(value.get(key), list):
                    return StatisticalRobustnessEvaluator._normalize_records(value[key])
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
    def _extract_numeric_series(records: list[dict[str, Any]]) -> list[float]:
        keys = (
            "value",
            "score",
            "metric",
            "result",
            "success_rate",
            "confidence",
            "confidence_score",
            "effect_size",
            "validation_score",
            "replication_score",
            "consensus_score",
            "evidence_quality_score",
            "statistical_robustness_score",
        )
        series: list[float] = []
        for record in records:
            for key in keys:
                if key in record:
                    value = StatisticalRobustnessEvaluator._as_float(record.get(key), default=None)  # type: ignore[arg-type]
                    if value is not None:
                        series.append(StatisticalRobustnessEvaluator._clamp(value))
                        break
        return series

    @staticmethod
    def _extract_first(records: list[dict[str, Any]], keys: tuple[str, ...], default: float = -1.0) -> float:
        for record in records:
            for key in keys:
                if key in record:
                    value = StatisticalRobustnessEvaluator._as_float(record.get(key), default=default)
                    if value >= 0.0:
                        return StatisticalRobustnessEvaluator._clamp(value)
        return default

    def _load_default_context(self) -> dict[str, Any]:
        context: dict[str, Any] = {}
        candidates = [
            self.root / "runtime_experiments" / "scientific_meta_analysis",
            self.root / "runtime_experiments" / "scientific_consensus",
            self.root / "runtime_experiments" / "scientific_theory_confidence",
            self.root / "external_validation" / "replication_statistical_validation",
            self.root / "external_validation" / "scientific_consensus_measurement",
        ]

        records: list[dict[str, Any]] = []
        for directory in candidates:
            if not directory.exists():
                continue
            for path in sorted(directory.rglob("*.json"))[:80]:
                try:
                    data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
                    if isinstance(data, dict):
                        data.setdefault("source_path", str(path.relative_to(self.root)))
                        records.append(data)
                    elif isinstance(data, list):
                        for item in data[:20]:
                            if isinstance(item, dict):
                                item = dict(item)
                                item.setdefault("source_path", str(path.relative_to(self.root)))
                                records.append(item)
                except Exception:
                    continue

        # JSONL sampling for longitudinal robustness without loading large archives.
        for path in [
            self.root / "runtime_experiments" / "a3_longitudinal_validation_20260617T150745Z.jsonl",
        ]:
            if not path.exists():
                continue
            try:
                for idx, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines()):
                    if idx >= 200:
                        break
                    try:
                        item = json.loads(line)
                    except Exception:
                        continue
                    if isinstance(item, dict):
                        item.setdefault("source_path", str(path.relative_to(self.root)))
                        records.append(item)
            except Exception:
                continue

        if records:
            context["results"] = records
        return context

    def _confidence_score(self, records: list[dict[str, Any]], explicit: Any = None) -> float:
        explicit_value = self._as_float(explicit, default=-1.0)
        if explicit_value >= 0.0:
            return self._clamp(explicit_value)

        found = self._extract_first(
            records,
            (
                "confidence_score",
                "confidence",
                "theory_confidence",
                "scientific_confidence",
                "replication_confidence",
                "consensus_score",
            ),
        )
        if found >= 0.0:
            return found

        series = self._extract_numeric_series(records)
        if series:
            return self._clamp(mean(series))
        return 0.0

    def _effect_size_score(self, records: list[dict[str, Any]], explicit: Any = None) -> float:
        explicit_value = self._as_float(explicit, default=-1.0)
        if explicit_value >= 0.0:
            return self._clamp(explicit_value)

        found = self._extract_first(
            records,
            (
                "effect_size_score",
                "effect_size",
                "delta",
                "improvement_delta",
                "mean_effect",
            ),
        )
        if found >= 0.0:
            return found

        series = self._extract_numeric_series(records)
        if len(series) >= 2:
            baseline = min(series)
            peak = max(series)
            return self._clamp(peak - baseline)
        if len(series) == 1:
            return self._clamp(series[0] * 0.5)
        return 0.0

    def _variance_stability(self, records: list[dict[str, Any]], explicit: Any = None) -> float:
        explicit_value = self._as_float(explicit, default=-1.0)
        if explicit_value >= 0.0:
            return self._clamp(explicit_value)

        variance_value = self._extract_first(records, ("variance", "score_variance", "result_variance"))
        if variance_value >= 0.0:
            return self._clamp(1.0 - variance_value)

        series = self._extract_numeric_series(records)
        if len(series) >= 2:
            return self._clamp(1.0 - pstdev(series))
        if len(series) == 1:
            return 0.75
        return 0.0

    def step(self, inputs: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        payload.update(self._load_default_context())
        if inputs:
            payload.update(inputs)
        payload.update(kwargs)

        records = self._normalize_records(
            payload.get(
                "results",
                payload.get(
                    "result_series",
                    payload.get("measurements", payload.get("records")),
                ),
            )
        )
        if not records and "evidence_items" in payload:
            records = self._normalize_records(payload.get("evidence_items"))

        series = self._extract_numeric_series(records)
        sample_count = int(max(len(series), len(records), self._as_float(payload.get("sample_size"), default=0.0)))

        confidence_score = self._confidence_score(records, payload.get("confidence_score"))
        effect_size_score = self._effect_size_score(records, payload.get("effect_size_score"))
        variance_stability = self._variance_stability(records, payload.get("variance_stability"))

        sample_adequacy = self._clamp(sample_count / 10.0)
        replication_support = self._clamp(self._as_float(payload.get("replication_support"), default=-1.0))
        if replication_support < 0.0:
            replication_support = 0.0
            if records:
                hits = 0
                for record in records:
                    text = json.dumps(record, ensure_ascii=False, default=str).lower()
                    if "replication" in text or "replicated" in text:
                        hits += 1
                replication_support = self._clamp(hits / max(1, len(records)))

        statistical_robustness_score = self._clamp(
            0.30 * confidence_score
            + 0.25 * effect_size_score
            + 0.25 * variance_stability
            + 0.10 * sample_adequacy
            + 0.10 * replication_support
        )

        fragile_reasons: list[str] = []
        if confidence_score < 0.50:
            fragile_reasons.append("low_confidence")
        if effect_size_score < 0.20:
            fragile_reasons.append("weak_effect_size")
        if variance_stability < 0.50:
            fragile_reasons.append("unstable_variance")
        if sample_adequacy < 0.30:
            fragile_reasons.append("small_sample")
        if statistical_robustness_score < 0.45:
            fragile_reasons.append("low_statistical_robustness")

        fragile_results = bool(fragile_reasons)
        if statistical_robustness_score >= 0.75 and not fragile_results:
            robustness_decision = "robust_results"
        elif statistical_robustness_score >= 0.45:
            robustness_decision = "review_recommended"
        else:
            robustness_decision = "fragile_results"

        report = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "sample_count": sample_count,
            "confidence_score": confidence_score,
            "effect_size_score": effect_size_score,
            "variance_stability": variance_stability,
            "sample_adequacy": sample_adequacy,
            "replication_support": replication_support,
            "statistical_robustness_score": statistical_robustness_score,
            "fragile_results": fragile_results,
            "fragile_result_reasons": sorted(set(fragile_reasons)),
            "robustness_decision": robustness_decision,
            "diagnostics": {
                "weights": {
                    "confidence_score": 0.30,
                    "effect_size_score": 0.25,
                    "variance_stability": 0.25,
                    "sample_adequacy": 0.10,
                    "replication_support": 0.10,
                },
                "input_series_length": len(series),
                "input_record_count": len(records),
                "input_mode": "project_context_plus_optional_payload",
            },
            "epistemic_position": {
                "phenomenal_subjectivity_claimed": False,
                "validated_domain": "functional_statistical_robustness_assessment",
                "interpretation": "statistical_metrics_only",
            },
        }

        result = dict(report)
        result["statistical_robustness_evaluator_report"] = report
        result["report_path"] = str(self.report_path)

        if payload.get("persist", True):
            self.report_dir.mkdir(parents=True, exist_ok=True)
            self.report_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        return result
