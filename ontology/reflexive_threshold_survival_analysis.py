from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json

PRIMITIVE = "reflexive_threshold_survival_analysis"

DEPENDENCIES = [
    "reflexive_threshold_history_archive",
    "reflexive_threshold_trend_monitor",
    "longitudinal_recovery_observer",
    "ninety_day_survival_projection",
    "long_horizon_stability_protocol",
    "reflexive_regression_detector",
    "reflexive_stability_monitor",
]


class ReflexiveThresholdSurvivalAnalysis:
    """X3 — fast reflexive threshold survival analysis.

    This primitive deliberately avoids global repository scans. It reads only
    the persisted outputs of X1 and X2 when available, then computes functional
    longitudinal survival indicators. No phenomenological claim is produced.
    """

    primitive = "REFLEXIVE_THRESHOLD_SURVIVAL_ANALYSIS"
    source_pipeline = "X1→X2→X3"
    phenomenal_conclusion = False

    def __init__(self, root: str | Path | None = None, max_history_records: int = 200):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.max_history_records = int(max(2, max_history_records))

        self.x1_latest = (
            self.root
            / "reflexive_threshold"
            / "reflexive_threshold_history_archive"
            / "latest_reflexive_threshold_history_archive.json"
        )
        self.x1_history = (
            self.root
            / "reflexive_threshold"
            / "reflexive_threshold_history_archive"
            / "reflexive_threshold_history_archive.jsonl"
        )
        self.x1_index = (
            self.root
            / "reflexive_threshold"
            / "reflexive_threshold_history_archive"
            / "reflexive_threshold_history_index.json"
        )

        self.x2_latest = (
            self.root
            / "reflexive_threshold_longitudinal_validation"
            / "x2_trend_monitor"
            / "latest_reflexive_threshold_trend.json"
        )
        self.x2_history = (
            self.root
            / "reflexive_threshold_longitudinal_validation"
            / "x2_trend_monitor"
            / "reflexive_threshold_trend_history.jsonl"
        )

        self.base_dir = (
            self.root
            / "reflexive_threshold_longitudinal_validation"
            / "x3_survival_analysis"
        )
        self.latest_file = self.base_dir / "latest_reflexive_threshold_survival.json"
        self.history_file = self.base_dir / "reflexive_threshold_survival_history.jsonl"
        self.report_file = self.base_dir / "reflexive_threshold_survival_analysis.md"

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _read_json(self, path: Path) -> dict[str, Any]:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
        return {}

    def _read_jsonl_tail(self, path: Path, limit: int | None = None) -> list[dict[str, Any]]:
        limit = int(limit or self.max_history_records)
        records: deque[dict[str, Any]] = deque(maxlen=limit)
        try:
            if not path.exists():
                return []
            with path.open("r", encoding="utf-8", errors="ignore") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if isinstance(data, dict):
                            records.append(data)
                    except Exception:
                        continue
        except Exception:
            return []
        return list(records)

    def _parse_time(self, value: Any) -> datetime | None:
        if not value:
            return None
        try:
            text = str(value).replace("Z", "+00:00")
            return datetime.fromisoformat(text)
        except Exception:
            return None

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except Exception:
            return float(default)

    def _clamp(self, value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, float(value)))

    def _extract_trend_records(self) -> list[dict[str, Any]]:
        records = self._read_jsonl_tail(self.x2_history, self.max_history_records)
        latest = self._read_json(self.x2_latest)
        if latest:
            latest_run_id = latest.get("run_id")
            if not records or records[-1].get("run_id") != latest_run_id:
                records.append(latest)
        return records[-self.max_history_records:]

    def _extract_history_records(self) -> list[dict[str, Any]]:
        records = self._read_jsonl_tail(self.x1_history, self.max_history_records)
        latest = self._read_json(self.x1_latest)
        if latest:
            latest_run_id = latest.get("run_id")
            if not records or records[-1].get("run_id") != latest_run_id:
                records.append(latest)
        return records[-self.max_history_records:]

    def _direction_for_record(self, record: dict[str, Any]) -> str:
        for key in ("trend_direction", "trajectory_direction", "trend_classification"):
            value = record.get(key)
            if value:
                return str(value).lower()
        return "unknown"

    def _is_regressive(self, record: dict[str, Any]) -> bool:
        direction = self._direction_for_record(record)
        if any(token in direction for token in ("regress", "degrad", "declin", "drift")):
            return True
        if bool(record.get("early_degradation_signal")):
            return True
        if bool(record.get("regression_detected")):
            return True
        trend_score = self._safe_float(record.get("longitudinal_trend_score"), 1.0)
        robustness = self._safe_float(record.get("temporal_robustness"), 1.0)
        return trend_score < 0.55 or robustness < 0.55

    def _time_span_days(self, records: list[dict[str, Any]]) -> float:
        times = [self._parse_time(r.get("timestamp_utc")) for r in records]
        times = [t for t in times if t is not None]
        if len(times) < 2:
            return 0.0
        return round(max(0.0, (max(times) - min(times)).total_seconds() / 86400.0), 6)

    def _first_regression_index(self, records: list[dict[str, Any]]) -> int | None:
        for idx, record in enumerate(records):
            if self._is_regressive(record):
                return idx
        return None

    def _first_recovery_index_after(self, records: list[dict[str, Any]], start: int | None) -> int | None:
        if start is None:
            return None
        for idx in range(start + 1, len(records)):
            if not self._is_regressive(records[idx]):
                trend_score = self._safe_float(records[idx].get("longitudinal_trend_score"), 0.0)
                stability = self._safe_float(records[idx].get("stability_index"), trend_score)
                if max(trend_score, stability) >= 0.65:
                    return idx
        return None

    def _estimate_survival(self, trend_records: list[dict[str, Any]], history_records: list[dict[str, Any]]) -> dict[str, Any]:
        all_records = trend_records or history_records
        sample_count = len(all_records)
        time_span_days = self._time_span_days(all_records)

        if not all_records:
            return {
                "sample_count": 0,
                "survival_duration_records": 0,
                "survival_duration_days": 0.0,
                "time_to_regression_records": None,
                "time_to_recovery_records": None,
                "regression_observed": False,
                "recovery_observed": False,
                "regression_rate": 0.0,
                "temporal_robustness": 0.0,
                "survival_probability": 0.0,
                "survival_classification": "insufficient_data",
            }

        regression_flags = [self._is_regressive(record) for record in all_records]
        regression_count = sum(1 for flag in regression_flags if flag)
        regression_rate = regression_count / sample_count if sample_count else 0.0
        first_reg = self._first_regression_index(all_records)
        first_rec = self._first_recovery_index_after(all_records, first_reg)

        if first_reg is None:
            survival_duration_records = sample_count
            time_to_regression_records = None
        else:
            survival_duration_records = first_reg
            time_to_regression_records = first_reg

        time_to_recovery_records = None if first_rec is None or first_reg is None else first_rec - first_reg

        trend_scores = [
            self._safe_float(r.get("longitudinal_trend_score"), None)
            for r in all_records
            if r.get("longitudinal_trend_score") is not None
        ]
        stability_scores = [
            self._safe_float(r.get("stability_index"), None)
            for r in all_records
            if r.get("stability_index") is not None
        ]
        archive_scores = [
            self._safe_float(r.get("archive_strength"), None)
            for r in history_records
            if r.get("archive_strength") is not None
        ]

        mean_trend = sum(trend_scores) / len(trend_scores) if trend_scores else 0.75
        mean_stability = sum(stability_scores) / len(stability_scores) if stability_scores else mean_trend
        mean_archive = sum(archive_scores) / len(archive_scores) if archive_scores else 0.75

        recovery_bonus = 0.08 if first_rec is not None else 0.0
        small_sample_penalty = 0.15 if sample_count < 3 else 0.0
        temporal_robustness = self._clamp(
            (0.35 * mean_trend)
            + (0.30 * mean_stability)
            + (0.20 * mean_archive)
            + (0.15 * (1.0 - regression_rate))
            + recovery_bonus
            - small_sample_penalty
        )
        survival_probability = self._clamp((0.60 * temporal_robustness) + (0.40 * (1.0 - regression_rate)))

        if sample_count < 2:
            classification = "insufficient_history"
        elif regression_rate >= 0.50:
            classification = "temporally_unstable"
        elif first_reg is not None and first_rec is None:
            classification = "regression_without_recovery"
        elif temporal_robustness >= 0.85 and regression_rate == 0:
            classification = "robust_survival"
        elif temporal_robustness >= 0.65:
            classification = "provisionally_stable"
        else:
            classification = "fragile_survival"

        return {
            "sample_count": sample_count,
            "survival_duration_records": survival_duration_records,
            "survival_duration_days": time_span_days,
            "time_to_regression_records": time_to_regression_records,
            "time_to_recovery_records": time_to_recovery_records,
            "regression_observed": first_reg is not None,
            "recovery_observed": first_rec is not None,
            "regression_rate": round(regression_rate, 6),
            "mean_trend_score": round(mean_trend, 6),
            "mean_stability_score": round(mean_stability, 6),
            "mean_archive_strength": round(mean_archive, 6),
            "temporal_robustness": round(temporal_robustness, 6),
            "survival_probability": round(survival_probability, 6),
            "survival_classification": classification,
        }

    def _write_report(self, result: dict[str, Any]) -> None:
        lines = [
            "# X3 — Reflexive Threshold Survival Analysis",
            "",
            "## Epistemic boundary",
            "",
            "- functional conclusion only",
            "- phenomenology undetermined",
            "- phenomenal_conclusion: false",
            "",
            "## Summary",
            "",
            f"- run_id: {result['run_id']}",
            f"- sample_count: {result['sample_count']}",
            f"- survival_duration_records: {result['survival_duration_records']}",
            f"- time_to_regression_records: {result['time_to_regression_records']}",
            f"- time_to_recovery_records: {result['time_to_recovery_records']}",
            f"- temporal_robustness: {result['temporal_robustness']}",
            f"- survival_probability: {result['survival_probability']}",
            f"- survival_classification: {result['survival_classification']}",
            "",
            "## Functional conclusion",
            "",
            result["functional_conclusion"],
            "",
        ]
        self.report_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = dict(inputs or {})
        timestamp = str(inputs.get("timestamp_utc") or self._now())
        run_id = str(inputs.get("run_id") or ("X3-" + timestamp.replace(":", "").replace("+", "Z")))

        supplied_trend_records = inputs.get("trend_records")
        supplied_history_records = inputs.get("history_records")
        trend_records = list(supplied_trend_records) if isinstance(supplied_trend_records, list) else self._extract_trend_records()
        history_records = list(supplied_history_records) if isinstance(supplied_history_records, list) else self._extract_history_records()

        survival = self._estimate_survival(trend_records, history_records)

        functional_conclusion = (
            "Open Cognitive Ecology has a functional survival-analysis record for reflexive-threshold indicators. "
            "This conclusion is restricted to measurable temporal stability, regression and recovery indicators. "
            "It does not establish phenomenological subjectivity."
        )

        result = {
            "primitive": self.primitive,
            "success": True,
            "run_id": run_id,
            "timestamp_utc": timestamp,
            "source_pipeline": self.source_pipeline,
            "x1_latest_path": str(self.x1_latest),
            "x2_latest_path": str(self.x2_latest),
            "input_sources": {
                "trend_records": len(trend_records),
                "history_records": len(history_records),
                "global_scan_used": False,
                "rglob_used": False,
                "max_history_records": self.max_history_records,
            },
            **survival,
            "functional_conclusion": functional_conclusion,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "phenomenal_conclusion": self.phenomenal_conclusion,
        }

        if persist:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.latest_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            with self.history_file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            self._write_report(result)
            result["latest_path"] = str(self.latest_file)
            result["history_path"] = str(self.history_file)
            result["report_path"] = str(self.report_file)

        return result


if __name__ == "__main__":
    print(json.dumps(ReflexiveThresholdSurvivalAnalysis().step(persist=True), indent=2, ensure_ascii=False))
