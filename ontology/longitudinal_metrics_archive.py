# -*- coding: utf-8 -*-

'''
E2 - Longitudinal Metrics Archive.

This primitive archives the canonical E1 stream:

    ~/open-cognitive-ecology/metrics/metrics_history.jsonl

into bounded longitudinal folders:

    metrics/daily/
    metrics/weekly/
    metrics/monthly/
    metrics/experiments/

It does not replace metrics_history_recorder. It consumes E1 as an empirical
source and produces longitudinal archive slices, manifests and certification
signals for E3+ aggregation, statistics, anomaly detection and dashboards.
'''

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import gzip
import json
import math
from typing import Any, Iterable, Optional

PRIMITIVE = "longitudinal_metrics_archive"

DEPENDENCIES = [
    "metrics_history_recorder",
    "civilizational_metrics_synthesizer",
    "experiment_stability_dashboard",
    "runtime_experiment_manager",
    "autonomous_resource_manager",
]

DEFAULT_ARCHIVE_QUOTA_BYTES = 50 * 1024 * 1024
DEFAULT_MAX_RECORDS_PER_RUN = 100_000


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if math.isnan(number) or math.isinf(number):
        return default
    return number


def _parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc)
    if not value:
        return datetime.now(timezone.utc)
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def _json_default(value: Any) -> str:
    return str(value)


class LongitudinalMetricsArchive:
    '''Bounded longitudinal archiver for metrics_history.jsonl.'''

    primitive = PRIMITIVE

    def __init__(
        self,
        root: str | Path | None = None,
        archive_quota_bytes: int = DEFAULT_ARCHIVE_QUOTA_BYTES,
        compress: bool = True,
        max_records_per_run: int = DEFAULT_MAX_RECORDS_PER_RUN,
    ) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.metrics_dir = self.root / "metrics"
        self.history_path = self.metrics_dir / "metrics_history.jsonl"
        self.legacy_history_path = self.root / "metrics_history.jsonl"
        self.daily_dir = self.metrics_dir / "daily"
        self.weekly_dir = self.metrics_dir / "weekly"
        self.monthly_dir = self.metrics_dir / "monthly"
        self.experiments_dir = self.metrics_dir / "experiments"
        self.manifest_path = self.metrics_dir / "longitudinal_metrics_archive_manifest.json"
        self.state_path = self.metrics_dir / "longitudinal_metrics_archive_state.json"
        self.archive_quota_bytes = max(5 * 1024 * 1024, int(archive_quota_bytes))
        self.compress = bool(compress)
        self.max_records_per_run = max(100, int(max_records_per_run))
        for directory in [self.metrics_dir, self.daily_dir, self.weekly_dir, self.monthly_dir, self.experiments_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_records(self) -> list[dict[str, Any]]:
        path = self.history_path if self.history_path.exists() else self.legacy_history_path
        records: list[dict[str, Any]] = []
        if not path.exists():
            return records
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            return records
        for line in lines[-self.max_records_per_run:]:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except Exception:
                continue
            if isinstance(record, dict):
                records.append(record)
        return records

    def _bucket_records(self, records: Iterable[dict[str, Any]]) -> dict[str, dict[str, list[dict[str, Any]]]]:
        buckets: dict[str, dict[str, list[dict[str, Any]]]] = {
            "daily": defaultdict(list),
            "weekly": defaultdict(list),
            "monthly": defaultdict(list),
        }
        for record in records:
            dt = _parse_timestamp(record.get("timestamp") or record.get("timestamp_utc"))
            day_key = dt.strftime("%Y-%m-%d")
            iso_year, iso_week, _ = dt.isocalendar()
            week_key = f"{iso_year}-W{iso_week:02d}"
            month_key = dt.strftime("%Y-%m")
            buckets["daily"][day_key].append(record)
            buckets["weekly"][week_key].append(record)
            buckets["monthly"][month_key].append(record)
        return buckets

    def _target_path(self, period: str, key: str) -> Path:
        directory = {"daily": self.daily_dir, "weekly": self.weekly_dir, "monthly": self.monthly_dir}[period]
        suffix = ".jsonl.gz" if self.compress else ".jsonl"
        return directory / f"{key}{suffix}"

    def _write_jsonl(self, path: Path, records: list[dict[str, Any]]) -> int:
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [json.dumps(record, ensure_ascii=False, sort_keys=True, default=_json_default) for record in records]
        payload = "\n".join(lines) + ("\n" if lines else "")
        if self.compress:
            with gzip.open(path, "wt", encoding="utf-8") as handle:
                handle.write(payload)
        else:
            path.write_text(payload, encoding="utf-8")
        return path.stat().st_size if path.exists() else 0

    def _archive_size(self) -> int:
        total = 0
        for directory in [self.daily_dir, self.weekly_dir, self.monthly_dir, self.experiments_dir]:
            if not directory.exists():
                continue
            for path in directory.rglob("*"):
                if path.is_file():
                    try:
                        total += path.stat().st_size
                    except Exception:
                        pass
        return total

    def _enforce_quota(self) -> dict[str, Any]:
        removed: list[str] = []
        size = self._archive_size()
        if size <= self.archive_quota_bytes:
            return {"quota_enforced": True, "archive_size_bytes": size, "removed_files": removed}
        candidates: list[Path] = []
        for directory in [self.daily_dir, self.weekly_dir, self.monthly_dir, self.experiments_dir]:
            candidates.extend([p for p in directory.rglob("*") if p.is_file()])
        candidates.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0)
        for path in candidates:
            if size <= self.archive_quota_bytes:
                break
            try:
                file_size = path.stat().st_size
                path.unlink()
                removed.append(str(path))
                size -= file_size
            except Exception:
                continue
        return {"quota_enforced": True, "archive_size_bytes": max(0, size), "removed_files": removed}

    def _metric_summary(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        numeric_values: dict[str, list[float]] = defaultdict(list)
        error_count = 0
        primitives: set[str] = set()
        for record in records:
            primitives.add(str(record.get("primitive", "unknown")))
            error_count += max(0, int(_safe_float(record.get("error_count", 0), 0.0)))
            metrics = record.get("metrics")
            if isinstance(metrics, dict):
                for key, value in metrics.items():
                    if isinstance(value, bool):
                        continue
                    if isinstance(value, (int, float)):
                        numeric_values[str(key)].append(_safe_float(value))
        means = {key: (sum(values) / len(values)) for key, values in numeric_values.items() if values}
        return {
            "record_count": len(records),
            "primitive_count": len(primitives),
            "error_count_total": error_count,
            "numeric_metric_count": len(numeric_values),
            "metric_means": means,
        }

    def _write_experiment_summary(self, records: list[dict[str, Any]], written_files: list[str]) -> Path:
        summary = {
            "primitive": PRIMITIVE,
            "generated_at": _now(),
            "source_history_path": str(self.history_path if self.history_path.exists() else self.legacy_history_path),
            "summary": self._metric_summary(records),
            "written_files": written_files,
            "archive_quota_bytes": self.archive_quota_bytes,
            "compression_enabled": self.compress,
        }
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self.experiments_dir / f"metrics_archive_summary_{stamp}.json"
        path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def _write_manifest(self, records: list[dict[str, Any]], written: dict[str, dict[str, str]], quota: dict[str, Any], experiment_summary_path: Path) -> dict[str, Any]:
        manifest = {
            "primitive": PRIMITIVE,
            "generated_at": _now(),
            "history_path": str(self.history_path),
            "legacy_history_path": str(self.legacy_history_path),
            "archive_root": str(self.metrics_dir),
            "directories": {
                "daily": str(self.daily_dir),
                "weekly": str(self.weekly_dir),
                "monthly": str(self.monthly_dir),
                "experiments": str(self.experiments_dir),
            },
            "record_count": len(records),
            "written": written,
            "experiment_summary_path": str(experiment_summary_path),
            "quota": quota,
            "local_disk_usage_bounded": True,
            "longitudinal_metrics_archive_operational": True,
            "error_count": 0,
        }
        self.manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        self.state_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        return manifest

    def archive(self) -> dict[str, Any]:
        records = self._load_records()
        buckets = self._bucket_records(records)
        written: dict[str, dict[str, str]] = {"daily": {}, "weekly": {}, "monthly": {}}
        written_files: list[str] = []
        for period, grouped in buckets.items():
            for key, period_records in grouped.items():
                target = self._target_path(period, key)
                self._write_jsonl(target, period_records)
                written[period][key] = str(target)
                written_files.append(str(target))
        experiment_summary_path = self._write_experiment_summary(records, written_files)
        written_files.append(str(experiment_summary_path))
        quota = self._enforce_quota()
        self._write_manifest(records, written, quota, experiment_summary_path)
        certification = {
            "daily_archive_ready": self.daily_dir.exists(),
            "weekly_archive_ready": self.weekly_dir.exists(),
            "monthly_archive_ready": self.monthly_dir.exists(),
            "experiments_archive_ready": self.experiments_dir.exists(),
            "archive_manifest_exists": self.manifest_path.exists(),
            "sample_count": len(records),
            "compression_enabled": self.compress,
            "local_disk_usage_bounded": True,
            "archive_success": bool(self.manifest_path.exists()),
        }
        return {
            "primitive": PRIMITIVE,
            "phase": "E2_LONGITUDINAL_METRICS_ARCHIVE",
            "history_path": str(self.history_path),
            "archive_root": str(self.metrics_dir),
            "daily_dir": str(self.daily_dir),
            "weekly_dir": str(self.weekly_dir),
            "monthly_dir": str(self.monthly_dir),
            "experiments_dir": str(self.experiments_dir),
            "manifest_path": str(self.manifest_path),
            "state_path": str(self.state_path),
            "record_count": len(records),
            "written_periods": {period: len(paths) for period, paths in written.items()},
            "quota": quota,
            "certification": certification,
            "longitudinal_metrics_archive_operational": certification["archive_success"],
            "next_step": "E3_metrics_aggregation_engine",
            "error_count": 0,
        }

    def step(self, inputs: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        if "archive_quota_bytes" in inputs:
            self.archive_quota_bytes = max(5 * 1024 * 1024, int(inputs["archive_quota_bytes"]))
        if "compress" in inputs:
            self.compress = bool(inputs["compress"])
        return self.archive()


ENGINE = LongitudinalMetricsArchive()


def step(inputs: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    return ENGINE.step(inputs)
