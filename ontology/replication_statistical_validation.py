from __future__ import annotations
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "external_validation" / "replication_statistical_validation"
H7_STATE_PATH = ROOT / "external_validation" / "independent_replication_tracker" / "latest_independent_replication_tracker.json"
H8_STATE_PATH = ROOT / "external_validation" / "scientific_consensus_engine" / "latest_scientific_consensus_engine.json"
H9_STATE_PATH = ROOT / "external_validation" / "external_replication_evidence_aggregator" / "latest_external_replication_evidence_aggregator.json"
H9_HISTORY_PATH = ROOT / "external_validation" / "external_replication_evidence_aggregator" / "external_replication_evidence_history.jsonl"


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


def _safe_read_jsonl(path: Path, limit: int = 200) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        if path.exists():
            lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
            for line in lines[-limit:]:
                try:
                    item = json.loads(line)
                    if isinstance(item, dict):
                        records.append(item)
                except Exception:
                    continue
    except Exception:
        pass
    return records


def _mean(values: list[float], default: float = 0.0) -> float:
    clean = [_clamp(v) for v in values]
    if not clean:
        return default
    return _clamp(mean(clean))


def _stability(values: list[float]) -> float:
    clean = [_clamp(v) for v in values]
    if len(clean) < 2:
        return 0.82 if clean else 0.0
    return _clamp(1.0 - pstdev(clean))


def _confidence_interval_width(values: list[float]) -> float:
    clean = [_clamp(v) for v in values]
    if len(clean) < 2:
        return 0.18 if clean else 1.0
    sd = pstdev(clean)
    width = 2.0 * 1.96 * sd / math.sqrt(len(clean))
    return _clamp(width)


class ReplicationStatisticalValidation:
    def __init__(self, output_dir: str | Path | None = None) -> None:
        self.output_dir = Path(output_dir) if output_dir is not None else OUTPUT_DIR
        self.state_path = self.output_dir / "latest_replication_statistical_validation.json"
        self.history_path = self.output_dir / "replication_statistical_validation_history.jsonl"
        self.dashboard_path = self.output_dir / "replication_statistical_validation_dashboard.html"
        self.prometheus_path = self.output_dir / "replication_statistical_validation.prom"
        self.registry_path = self.output_dir / "replication_statistical_validation_registry.json"

    def _merge_context(self, statistical_context: dict[str, Any] | None) -> dict[str, Any]:
        h7 = _safe_read_json(H7_STATE_PATH)
        h8 = _safe_read_json(H8_STATE_PATH)
        h9 = _safe_read_json(H9_STATE_PATH)
        h9_history = _safe_read_jsonl(H9_HISTORY_PATH, limit=100)

        evidence_values = [
            _clamp(x.get("replication_evidence_score", 0.0))
            for x in h9_history
            if "replication_evidence_score" in x
        ]
        validation_strength_values = [
            _clamp(x.get("external_validation_strength", 0.0))
            for x in h9_history
            if "external_validation_strength" in x
        ]

        context: dict[str, Any] = {
            "h7_success": bool(h7.get("success", False)),
            "h8_success": bool(h8.get("success", False)),
            "h9_success": bool(h9.get("success", False)),
            "replication_tracking_score": _clamp(h7.get("replication_tracking_score", 0.0)),
            "external_replication_count": int(h7.get("external_replication_count", 0) or 0),
            "successful_replication_count": int(h7.get("successful_replication_count", 0) or 0),
            "scientific_consensus": _clamp(h8.get("scientific_consensus", 0.0)),
            "consensus_confidence_index": _clamp(h8.get("consensus_confidence_index", 0.0)),
            "disagreement_ratio": _clamp(h8.get("disagreement_ratio", 1.0)),
            "validation_quality_score": _clamp(h8.get("validation_quality_score", 0.0)),
            "replication_evidence_score": _clamp(h9.get("replication_evidence_score", 0.0)),
            "external_validation_strength": _clamp(h9.get("external_validation_strength", 0.0)),
            "independent_reproduction_rate": _clamp(h9.get("independent_reproduction_rate", 0.0)),
            "cross_site_consistency_index": _clamp(h9.get("cross_site_consistency_index", 0.0)),
            "evidence_aggregation_quality": _clamp(h9.get("evidence_aggregation_quality", 0.0)),
            "evidence_values": evidence_values,
            "validation_strength_values": validation_strength_values,
            "history_sample_count": len(h9_history),
            "override_used": False,
        }
        if statistical_context:
            context.update(statistical_context)
            context["override_used"] = True
        return context

    def _compute(self, context: dict[str, Any]) -> dict[str, Any]:
        evidence_values = [_clamp(v) for v in context.get("evidence_values", [])]
        strength_values = [_clamp(v) for v in context.get("validation_strength_values", [])]
        combined_values = evidence_values + strength_values
        if not combined_values:
            combined_values = [
                _clamp(context.get("replication_evidence_score", 0.0)),
                _clamp(context.get("external_validation_strength", 0.0)),
                _clamp(context.get("scientific_consensus", 0.0)),
                _clamp(context.get("validation_quality_score", 0.0)),
            ]

        confidence_interval_width = _confidence_interval_width(combined_values)
        longitudinal_stability_score = _stability(combined_values)
        descriptive_statistical_score = _mean(combined_values)
        sample_adequacy_score = _clamp(min(1.0, max(1, int(context.get("history_sample_count", 0) or 0)) / 8.0))
        disagreement_penalty = _clamp(1.0 - _clamp(context.get("disagreement_ratio", 1.0)))

        replication_significance_score = _clamp(
            0.30 * _clamp(context.get("replication_evidence_score", 0.0))
            + 0.22 * _clamp(context.get("external_validation_strength", 0.0))
            + 0.16 * _clamp(context.get("scientific_consensus", 0.0))
            + 0.12 * longitudinal_stability_score
            + 0.10 * disagreement_penalty
            + 0.10 * (1.0 - confidence_interval_width)
        )
        statistical_validation_score = _clamp(
            0.34 * replication_significance_score
            + 0.18 * descriptive_statistical_score
            + 0.16 * _clamp(context.get("validation_quality_score", 0.0))
            + 0.14 * _clamp(context.get("cross_site_consistency_index", 0.0))
            + 0.10 * sample_adequacy_score
            + 0.08 * _clamp(context.get("replication_tracking_score", 0.0))
        )
        statistical_power_proxy = _clamp(
            0.40 * sample_adequacy_score
            + 0.30 * longitudinal_stability_score
            + 0.30 * (1.0 - confidence_interval_width)
        )

        component_scores = {
            "descriptive_statistical_score": round(descriptive_statistical_score, 6),
            "longitudinal_stability_score": round(longitudinal_stability_score, 6),
            "sample_adequacy_score": round(sample_adequacy_score, 6),
            "statistical_power_proxy": round(statistical_power_proxy, 6),
            "confidence_interval_narrowness": round(1.0 - confidence_interval_width, 6),
            "consensus_support": round(_clamp(context.get("scientific_consensus", 0.0)), 6),
            "evidence_support": round(_clamp(context.get("replication_evidence_score", 0.0)), 6),
        }

        success = bool(
            context.get("h7_success", False)
            and context.get("h8_success", False)
            and context.get("h9_success", False)
            and replication_significance_score >= 0.70
            and statistical_validation_score >= 0.70
            and confidence_interval_width <= 0.35
        )

        warnings: list[str] = []
        if not context.get("h7_success", False):
            warnings.append("missing_h7_independent_replication_tracking_success")
        if not context.get("h8_success", False):
            warnings.append("missing_h8_scientific_consensus_success")
        if not context.get("h9_success", False):
            warnings.append("missing_h9_evidence_aggregation_success")
        if confidence_interval_width > 0.35:
            warnings.append("wide_confidence_interval")
        if sample_adequacy_score < 0.30:
            warnings.append("limited_replication_sample_size")
        if replication_significance_score < 0.70:
            warnings.append("low_replication_significance_score")

        return {
            "primitive": "replication_statistical_validation",
            "refinement": "H10-R1",
            "timestamp_utc": _utc_now(),
            "success": success,
            "replication_significance_score": round(replication_significance_score, 6),
            "statistical_validation_score": round(statistical_validation_score, 6),
            "confidence_interval_width": round(confidence_interval_width, 6),
            "longitudinal_stability_score": round(longitudinal_stability_score, 6),
            "descriptive_statistical_score": round(descriptive_statistical_score, 6),
            "statistical_power_proxy": round(statistical_power_proxy, 6),
            "sample_count": int(context.get("history_sample_count", 0) or len(combined_values)),
            "external_replication_count": int(context.get("external_replication_count", 0) or 0),
            "successful_replication_count": int(context.get("successful_replication_count", 0) or 0),
            "independent_reproduction_rate": _clamp(context.get("independent_reproduction_rate", 0.0)),
            "replication_evidence_score": _clamp(context.get("replication_evidence_score", 0.0)),
            "external_validation_strength": _clamp(context.get("external_validation_strength", 0.0)),
            "scientific_consensus": _clamp(context.get("scientific_consensus", 0.0)),
            "disagreement_ratio": _clamp(context.get("disagreement_ratio", 1.0)),
            "component_scores": component_scores,
            "diagnostics": {
                "context_override_used": bool(context.get("override_used", False)),
                "warnings": warnings,
                "real_external_replication_campaign_required_later": True,
                "statistical_claim_limited_to_functional_indicators": True,
            },
            "governance": {
                "non_closure_compliant": True,
                "traceability_enabled": True,
                "reversibility_enabled": True,
                "no_credentials_required": True,
                "no_network_side_effects": True,
                "offline_statistical_validation_only": True,
                "phenomenal_subjectivity_not_asserted": True,
                "closure_pressure_increase": 0.0,
            },
        }

    def _write_json(self, path: Path, data: dict[str, Any], fs_context: GovernedFilesystemEffectContext | None = None) -> None:
        if fs_context is None:
            raise PermissionError("persisted JSON write requires preissued filesystem effect context")
        payload = json.dumps(data, indent=2, sort_keys=True).encode("utf-8")
        fs_context.execute_path("json_parent_create", "FS_CREATE_DIR", path.parent)
        fs_context.execute_path("json_write", "FS_WRITE_BYTES", path, payload)

    def _append_jsonl(
        self,
        path: Path,
        data: dict[str, Any],
        fs_context: GovernedFilesystemEffectContext | None = None,
    ) -> None:
        if fs_context is None:
            raise PermissionError("JSONL append requires preissued filesystem effect context")
        payload = (json.dumps(data, sort_keys=True) + "\n").encode("utf-8")
        remaining = fs_context.remaining()
        if remaining.get("history_parent_create") != 1 or remaining.get("history_append") != 1:
            raise RuntimeError("JSONL append requires exactly one preissued handle in each required slot")
        fs_context.execute_path("history_parent_create", "FS_CREATE_DIRS", path.parent)
        fs_context.execute_path("history_append", "FS_APPEND_BYTES", path, payload)

    def _write_registry(self, result: dict[str, Any], fs_context: GovernedFilesystemEffectContext | None = None) -> None:
        registry = {
            "primitive": "replication_statistical_validation",
            "refinement": "H10-R1",
            "updated_at_utc": result["timestamp_utc"],
            "statistical_indicators": {
                "replication_significance_score": result["replication_significance_score"],
                "statistical_validation_score": result["statistical_validation_score"],
                "confidence_interval_width": result["confidence_interval_width"],
                "longitudinal_stability_score": result["longitudinal_stability_score"],
                "statistical_power_proxy": result["statistical_power_proxy"],
            },
            "inputs": {
                "h7_state_path": str(H7_STATE_PATH),
                "h8_state_path": str(H8_STATE_PATH),
                "h9_state_path": str(H9_STATE_PATH),
                "h9_history_path": str(H9_HISTORY_PATH),
            },
            "governance": result["governance"],
        }
        self._write_json(self.registry_path, registry, fs_context)

    def _write_dashboard(self, result: dict[str, Any]) -> None:
        rows = "\n".join(
            f"<tr><td>{key}</td><td>{value}</td></tr>"
            for key, value in result.items()
            if isinstance(value, (str, int, float, bool))
        )
        html = f"""<!doctype html>
<html><head><meta charset='utf-8'><title>Replication Statistical Validation</title>
<style>body{{font-family:Arial,sans-serif;margin:40px;}}table{{border-collapse:collapse;width:100%;}}td,th{{border:1px solid #ccc;padding:8px;text-align:left;}}th{{background:#f0f0f0;}}</style></head>
<body><h1>Replication Statistical Validation</h1><p>H10 offline statistical validation of external replication evidence.</p>
<table><tr><th>Metric</th><th>Value</th></tr>{rows}</table></body></html>"""
        self.dashboard_path.write_text(html, encoding="utf-8")

    def _write_prometheus(self, result: dict[str, Any]) -> None:
        metrics = {
            "oce_replication_significance_score": result["replication_significance_score"],
            "oce_statistical_validation_score": result["statistical_validation_score"],
            "oce_confidence_interval_width": result["confidence_interval_width"],
            "oce_longitudinal_stability_score": result["longitudinal_stability_score"],
            "oce_descriptive_statistical_score": result["descriptive_statistical_score"],
            "oce_statistical_power_proxy": result["statistical_power_proxy"],
            "oce_replication_statistical_sample_count": float(result["sample_count"]),
            "oce_external_replication_count": float(result["external_replication_count"]),
            "oce_successful_replication_count": float(result["successful_replication_count"]),
        }
        lines: list[str] = []
        for name, value in metrics.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {float(value)}")
        self.prometheus_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def step(self, statistical_context: dict[str, Any] | None = None, persist: bool = True, fs_context: GovernedFilesystemEffectContext | None = None) -> dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        context = self._merge_context(statistical_context)
        result = self._compute(context)
        result.update({
            "state_path": str(self.state_path),
            "history_path": str(self.history_path),
            "registry_path": str(self.registry_path),
            "dashboard_path": str(self.dashboard_path),
            "prometheus_path": str(self.prometheus_path),
        })
        if persist:
            self._write_json(self.state_path, result, fs_context)
            self._append_jsonl(self.history_path, result, fs_context=fs_context)
            self._write_registry(result, fs_context)
            self._write_dashboard(result)
            self._write_prometheus(result)
        return result
