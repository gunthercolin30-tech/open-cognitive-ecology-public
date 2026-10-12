from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "external_validation" / "external_replication_evidence_aggregator"
H7_STATE_PATH = ROOT / "external_validation" / "independent_replication_tracker" / "latest_independent_replication_tracker.json"
H7_HISTORY_PATH = ROOT / "external_validation" / "independent_replication_tracker" / "replication_campaign_history.jsonl"
H8_STATE_PATH = ROOT / "external_validation" / "scientific_consensus_engine" / "latest_scientific_consensus_engine.json"
H8_HISTORY_PATH = ROOT / "external_validation" / "scientific_consensus_engine" / "scientific_consensus_history.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _clamp(value: Any, low: float = 0.0, high: float = 1.0) -> float:
    try:
        value = float(value)
    except Exception:
        value = 0.0
    if value < low:
        return low
    if value > high:
        return high
    return value


def _safe_read_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def _safe_read_jsonl(path: Path, limit: int = 50) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        if not path.exists():
            return records
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        for line in lines[-limit:]:
            try:
                data = json.loads(line)
                if isinstance(data, dict):
                    records.append(data)
            except Exception:
                continue
    except Exception:
        return records
    return records


def _mean_metric(records: list[dict[str, Any]], key: str, default: float = 0.0) -> float:
    values = [_clamp(record.get(key, default)) for record in records if key in record]
    if not values:
        return _clamp(default)
    return _clamp(mean(values))


def _stability(values: list[float]) -> float:
    values = [_clamp(v) for v in values]
    if len(values) < 2:
        return 0.90 if values else 0.50
    return _clamp(1.0 - min(1.0, pstdev(values)))


class ExternalReplicationEvidenceAggregator:
    primitive = "external_replication_evidence_aggregator"
    refinement = "H9-R1"

    def __init__(self, output_dir: str | Path | None = None) -> None:
        self.output_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
        self.state_path = self.output_dir / "latest_external_replication_evidence_aggregator.json"
        self.history_path = self.output_dir / "external_replication_evidence_history.jsonl"
        self.evidence_registry_path = self.output_dir / "external_replication_evidence_registry.json"
        self.dashboard_path = self.output_dir / "external_replication_evidence_dashboard.html"
        self.prometheus_path = self.output_dir / "external_replication_evidence.prom"

    def _load_observed_context(self) -> dict[str, Any]:
        h7 = _safe_read_json(H7_STATE_PATH)
        h8 = _safe_read_json(H8_STATE_PATH)
        h7_history = _safe_read_jsonl(H7_HISTORY_PATH)
        h8_history = _safe_read_jsonl(H8_HISTORY_PATH)

        h7_scores = [_clamp(r.get("replication_tracking_score")) for r in h7_history if "replication_tracking_score" in r]
        h8_scores = [_clamp(r.get("scientific_consensus")) for r in h8_history if "scientific_consensus" in r]

        return {
            "h7_success": bool(h7.get("success", False)),
            "h8_success": bool(h8.get("success", False)),
            "replication_tracking_score": _clamp(h7.get("replication_tracking_score", 0.0)),
            "scientific_consensus": _clamp(h8.get("scientific_consensus", 0.0)),
            "consensus_confidence_index": _clamp(h8.get("consensus_confidence_index", 0.0)),
            "validation_quality_score": _clamp(h8.get("validation_quality_score", 0.0)),
            "disagreement_ratio": _clamp(h8.get("disagreement_ratio", 0.0)),
            "external_replication_count": int(h7.get("external_replication_count", 0) or 0),
            "successful_replication_count": int(h7.get("successful_replication_count", 0) or 0),
            "failed_replication_count": int(h7.get("failed_replication_count", 0) or 0),
            "replicator_count": int(h7.get("replicator_count", 0) or 0),
            "campaign_count": int(h7.get("campaign_count", 0) or 0),
            "independent_validation_count": int(h7.get("independent_validation_count", 0) or 0),
            "independent_reproduction_rate": _clamp(h7.get("independent_reproduction_rate", 0.0)),
            "replication_success_rate": _clamp(h7.get("replication_success_rate", 0.0)),
            "h7_history_length": len(h7_history),
            "h8_history_length": len(h8_history),
            "h7_longitudinal_stability": _stability(h7_scores),
            "h8_longitudinal_stability": _stability(h8_scores),
            "h7_history_mean_score": _mean_metric(h7_history, "replication_tracking_score", h7.get("replication_tracking_score", 0.0)),
            "h8_history_mean_consensus": _mean_metric(h8_history, "scientific_consensus", h8.get("scientific_consensus", 0.0)),
        }

    def _merge_context(self, override: dict[str, Any] | None) -> dict[str, Any]:
        context = self._load_observed_context()
        if isinstance(override, dict):
            context.update(override)
            context["context_override_used"] = True
        else:
            context["context_override_used"] = False
        return context

    def _compute(self, context: dict[str, Any]) -> dict[str, Any]:
        replication_tracking_score = _clamp(context.get("replication_tracking_score", 0.0))
        scientific_consensus = _clamp(context.get("scientific_consensus", 0.0))
        consensus_confidence_index = _clamp(context.get("consensus_confidence_index", 0.0))
        validation_quality_score = _clamp(context.get("validation_quality_score", 0.0))
        disagreement_ratio = _clamp(context.get("disagreement_ratio", 0.0))
        h7_stability = _clamp(context.get("h7_longitudinal_stability", 0.0))
        h8_stability = _clamp(context.get("h8_longitudinal_stability", 0.0))
        h7_history_mean = _clamp(context.get("h7_history_mean_score", replication_tracking_score))
        h8_history_mean = _clamp(context.get("h8_history_mean_consensus", scientific_consensus))

        external_replication_count = int(context.get("external_replication_count", 0) or 0)
        successful_replication_count = int(context.get("successful_replication_count", 0) or 0)
        failed_replication_count = int(context.get("failed_replication_count", 0) or 0)
        replicator_count = int(context.get("replicator_count", 0) or 0)
        campaign_count = int(context.get("campaign_count", 0) or 0)
        independent_validation_count = int(context.get("independent_validation_count", 0) or 0)
        h7_history_length = int(context.get("h7_history_length", 0) or 0)
        h8_history_length = int(context.get("h8_history_length", 0) or 0)

        observed_reproduction_rate = _clamp(context.get("independent_reproduction_rate", 0.0))
        observed_success_rate = _clamp(context.get("replication_success_rate", 0.0))
        if external_replication_count > 0:
            computed_reproduction_rate = _clamp(successful_replication_count / max(1, external_replication_count))
        else:
            computed_reproduction_rate = observed_reproduction_rate
        independent_reproduction_rate = max(observed_reproduction_rate, computed_reproduction_rate, observed_success_rate)

        evidence_presence_score = _clamp(
            0.18 * bool(context.get("h7_success", False))
            + 0.18 * bool(context.get("h8_success", False))
            + 0.22 * replication_tracking_score
            + 0.18 * scientific_consensus
            + 0.12 * validation_quality_score
            + 0.07 * min(1.0, h7_history_length / 3.0)
            + 0.05 * min(1.0, h8_history_length / 3.0)
        )
        cross_site_consistency_index = _clamp(
            0.30 * h7_stability
            + 0.25 * h8_stability
            + 0.20 * (1.0 - disagreement_ratio)
            + 0.15 * consensus_confidence_index
            + 0.10 * ((h7_history_mean + h8_history_mean) / 2.0)
        )
        external_validation_strength = _clamp(
            0.30 * evidence_presence_score
            + 0.22 * scientific_consensus
            + 0.18 * validation_quality_score
            + 0.14 * consensus_confidence_index
            + 0.10 * cross_site_consistency_index
            + 0.06 * independent_reproduction_rate
        )
        replication_evidence_score = _clamp(
            0.32 * evidence_presence_score
            + 0.24 * external_validation_strength
            + 0.18 * cross_site_consistency_index
            + 0.12 * replication_tracking_score
            + 0.08 * (1.0 - disagreement_ratio)
            + 0.06 * validation_quality_score
        )
        evidence_aggregation_quality = _clamp(
            0.28 * replication_evidence_score
            + 0.24 * external_validation_strength
            + 0.20 * cross_site_consistency_index
            + 0.16 * validation_quality_score
            + 0.12 * (1.0 - disagreement_ratio)
        )

        real_replications_pending = external_replication_count == 0
        success = (
            replication_evidence_score >= 0.70
            and external_validation_strength >= 0.70
            and evidence_aggregation_quality >= 0.70
            and disagreement_ratio <= 0.35
            and bool(context.get("h7_success", False))
            and bool(context.get("h8_success", False))
        )

        warnings: list[str] = []
        if not context.get("h7_success", False):
            warnings.append("missing_h7_independent_replication_tracker_success")
        if not context.get("h8_success", False):
            warnings.append("missing_h8_scientific_consensus_engine_success")
        if disagreement_ratio > 0.35:
            warnings.append("high_disagreement_ratio")
        if real_replications_pending:
            warnings.append("no_real_external_replication_evidence_recorded_yet")
        if replication_evidence_score < 0.70:
            warnings.append("low_replication_evidence_score")

        return {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": _utc_now(),
            "success": success,
            "replication_evidence_score": round(replication_evidence_score, 6),
            "external_validation_strength": round(external_validation_strength, 6),
            "independent_reproduction_rate": round(independent_reproduction_rate, 6),
            "cross_site_consistency_index": round(cross_site_consistency_index, 6),
            "evidence_aggregation_quality": round(evidence_aggregation_quality, 6),
            "evidence_presence_score": round(evidence_presence_score, 6),
            "external_replication_count": external_replication_count,
            "successful_replication_count": successful_replication_count,
            "failed_replication_count": failed_replication_count,
            "replicator_count": replicator_count,
            "campaign_count": campaign_count,
            "independent_validation_count": independent_validation_count,
            "scientific_consensus": round(scientific_consensus, 6),
            "consensus_confidence_index": round(consensus_confidence_index, 6),
            "validation_quality_score": round(validation_quality_score, 6),
            "disagreement_ratio": round(disagreement_ratio, 6),
            "component_scores": {
                "h7_replication_tracking": round(replication_tracking_score, 6),
                "h8_scientific_consensus": round(scientific_consensus, 6),
                "h8_validation_quality": round(validation_quality_score, 6),
                "h7_longitudinal_stability": round(h7_stability, 6),
                "h8_longitudinal_stability": round(h8_stability, 6),
                "cross_site_consistency": round(cross_site_consistency_index, 6),
            },
            "diagnostics": {
                "context_override_used": bool(context.get("context_override_used", False)),
                "h7_history_length": h7_history_length,
                "h8_history_length": h8_history_length,
                "real_replications_pending": real_replications_pending,
                "h9_scope": "offline_structured_evidence_aggregation_without_external_side_effects",
                "warnings": warnings,
            },
            "governance": {
                "non_closure_compliant": True,
                "traceability_enabled": True,
                "reversibility_enabled": True,
                "offline_evidence_aggregation_only": True,
                "no_credentials_required": True,
                "no_network_side_effects": True,
                "no_github_action_performed": True,
                "no_zenodo_action_performed": True,
                "closure_pressure_increase": 0.0,
                "real_external_campaign_required_later": True,
            },
        }

    def _write_json(self, path: Path, data: dict[str, Any], fs_context: GovernedFilesystemEffectContext | None = None) -> None:
        if fs_context is None:
            raise PermissionError("external replication JSON write requires preissued filesystem effect context")
        payload = json.dumps(data, indent=2, sort_keys=True).encode("utf-8")
        fs_context.execute_path("external_replication_json_write", "FS_WRITE_REPLACE_BYTES", path, payload)

    def _append_jsonl(self, path: Path, data: dict[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(data, sort_keys=True) + "\n")

    def _write_registry(self, result: dict[str, Any], fs_context: GovernedFilesystemEffectContext | None = None) -> None:
        registry = {
            "primitive": self.primitive,
            "updated_at_utc": result["timestamp_utc"],
            "evidence_sources": [
                {
                    "source": "independent_replication_tracker",
                    "path": str(H7_STATE_PATH),
                    "available": H7_STATE_PATH.exists(),
                    "score_key": "replication_tracking_score",
                },
                {
                    "source": "scientific_consensus_engine",
                    "path": str(H8_STATE_PATH),
                    "available": H8_STATE_PATH.exists(),
                    "score_key": "scientific_consensus",
                },
                {
                    "source": "h7_history",
                    "path": str(H7_HISTORY_PATH),
                    "available": H7_HISTORY_PATH.exists(),
                    "record_count": result["diagnostics"].get("h7_history_length", 0),
                },
                {
                    "source": "h8_history",
                    "path": str(H8_HISTORY_PATH),
                    "available": H8_HISTORY_PATH.exists(),
                    "record_count": result["diagnostics"].get("h8_history_length", 0),
                },
            ],
            "latest_metrics": {
                "replication_evidence_score": result["replication_evidence_score"],
                "external_validation_strength": result["external_validation_strength"],
                "independent_reproduction_rate": result["independent_reproduction_rate"],
                "cross_site_consistency_index": result["cross_site_consistency_index"],
                "evidence_aggregation_quality": result["evidence_aggregation_quality"],
            },
            "governance": result["governance"],
        }
        self._write_json(self.evidence_registry_path, registry, fs_context=fs_context)

    def _write_dashboard(self, result: dict[str, Any]) -> None:
        rows = []
        keys = [
            "success",
            "replication_evidence_score",
            "external_validation_strength",
            "independent_reproduction_rate",
            "cross_site_consistency_index",
            "evidence_aggregation_quality",
            "external_replication_count",
            "successful_replication_count",
            "scientific_consensus",
            "disagreement_ratio",
        ]
        for key in keys:
            rows.append(f"<tr><td>{key}</td><td>{result.get(key)}</td></tr>")
        html = "\n".join([
            "<!doctype html>",
            "<html><head><meta charset='utf-8'>",
            "<title>External Replication Evidence Aggregator</title>",
            "<style>body{font-family:Arial,sans-serif;margin:40px;}table{border-collapse:collapse;width:100%;}td,th{border:1px solid #ccc;padding:8px;text-align:left;}th{background:#f0f0f0;}.ok{color:#167a16}.warn{color:#9a6700}</style>",
            "</head><body>",
            "<h1>External Replication Evidence Aggregator</h1>",
            f"<p>Generated at {result.get('timestamp_utc')}</p>",
            "<table><tr><th>Metric</th><th>Value</th></tr>",
            *rows,
            "</table>",
            "<h2>Governance</h2>",
            "<p>Offline evidence aggregation only; no credential use; no network side effects.</p>",
            "</body></html>",
        ])
        self.dashboard_path.write_text(html, encoding="utf-8")

    def _write_prometheus(self, result: dict[str, Any]) -> None:
        metrics = {
            "oce_replication_evidence_score": result["replication_evidence_score"],
            "oce_external_validation_strength": result["external_validation_strength"],
            "oce_independent_reproduction_rate": result["independent_reproduction_rate"],
            "oce_cross_site_consistency_index": result["cross_site_consistency_index"],
            "oce_evidence_aggregation_quality": result["evidence_aggregation_quality"],
            "oce_external_replication_count": float(result["external_replication_count"]),
            "oce_successful_replication_count": float(result["successful_replication_count"]),
            "oce_replicator_count": float(result["replicator_count"]),
            "oce_replication_campaign_count": float(result["campaign_count"]),
            "oce_scientific_consensus": result["scientific_consensus"],
            "oce_disagreement_ratio": result["disagreement_ratio"],
        }
        lines: list[str] = []
        for name, value in metrics.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {float(value)}")
        self.prometheus_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def step(self, evidence_context: dict[str, Any] | None = None, persist: bool = True, fs_context: GovernedFilesystemEffectContext | None = None) -> dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        context = self._merge_context(evidence_context)
        result = self._compute(context)
        result.update({
            "state_path": str(self.state_path),
            "history_path": str(self.history_path),
            "evidence_registry_path": str(self.evidence_registry_path),
            "dashboard_path": str(self.dashboard_path),
            "prometheus_path": str(self.prometheus_path),
        })
        if persist:
            self._write_json(self.state_path, result, fs_context=fs_context)
            self._append_jsonl(self.history_path, result)
            self._write_registry(result, fs_context=fs_context)
            self._write_dashboard(result)
            self._write_prometheus(result)
        return result
