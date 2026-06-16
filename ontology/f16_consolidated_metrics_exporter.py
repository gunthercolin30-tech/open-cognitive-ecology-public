from __future__ import annotations

import datetime as _dt
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PRIMITIVE = "f16_consolidated_metrics_exporter"

DEPENDENCIES = [
    "real_cloud_node_deployment_validator",
    "real_community_node_certification",
    "civilizational_continuity_guardian",
    "failure_recovery_orchestrator",
    "distributed_civilizational_continuity_certification",
    "long_duration_distributed_continuity_certification",
    "distributed_continuity_certification_dashboard",
    "prometheus_metrics_exporter",
    "grafana_dashboard_exporter",
    "metrics_history_recorder",
    "metrics_aggregation_engine",
    "civilizational_metrics_synthesizer",
]

ROOT = Path.home() / "open-cognitive-ecology"

_PROM_LINE_RE = re.compile(
    r"^[a-zA-Z_:][a-zA-Z0-9_:]*(\{[^}]*\})?\s+"
    r"[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?$"
)


def _utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ssd_root() -> Optional[Path]:
    root = Path(os.environ.get("OCE_SSD_ROOT", "/Volumes/OCE_SSD"))
    return root if root.exists() else None


def _continuity_root() -> Path:
    ssd = _ssd_root()
    if ssd is not None:
        return Path(os.environ.get("OCE_CONTINUITY", str(ssd / "OCE_CIVILIZATIONAL_CONTINUITY")))
    return ROOT


def _metrics_root() -> Path:
    ssd = _ssd_root()
    if ssd is not None:
        return Path(os.environ.get("OCE_METRICS", str(ssd / "OCE_METRICS")))
    return ROOT / "metrics"


def _dashboard_root() -> Path:
    ssd = _ssd_root()
    if ssd is not None:
        return Path(os.environ.get("OCE_DASHBOARDS", str(ssd / "OCE_DASHBOARDS")))
    return ROOT / "dashboards"


def _safe_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    try:
        out = float(value)
    except Exception:
        return default
    if not math.isfinite(out):
        return default
    return out


def _clamp(value: Any, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, _safe_float(value, lo)))


def _safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    if isinstance(value, str):
        return value.strip().lower() in {
            "1", "true", "yes", "ok", "validated", "certified", "success"
        }
    return bool(value)


def _load_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
    return default


def _read_jsonl(path: Path, limit: int = 500) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return []
    for raw in lines[-limit:]:
        line = raw.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def _latest(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return rows[-1] if rows else {}


def _weighted_score(candidates: List[Tuple[Any, float]]) -> float:
    usable: List[Tuple[float, float]] = []
    for value, weight in candidates:
        if value is None:
            continue
        usable.append((_clamp(value), float(weight)))
    if not usable:
        return 0.0
    total_weight = sum(weight for _, weight in usable)
    if total_weight <= 0:
        return 0.0
    return sum(value * weight for value, weight in usable) / total_weight


def _metric_name(name: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9_:]", "_", str(name).strip().lower())
    text = re.sub(r"_+", "_", text).strip("_") or "unknown_metric"
    if text[0].isdigit():
        text = "metric_" + text
    if not text.startswith("oce_"):
        text = "oce_" + text
    return text


def _prom_line(metric: str, value: Any, help_text: str = "") -> List[str]:
    v = _safe_float(value, 0.0)
    name = _metric_name(metric)
    help_clean = str(help_text or name).replace("\\", "\\\\").replace("\n", " ")
    return [
        f"# HELP {name} {help_clean}",
        f"# TYPE {name} gauge",
        f"{name} {v:.9g}",
    ]


def _validate_prometheus(text: str) -> Dict[str, Any]:
    bad: List[str] = []
    count = 0
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        count += 1
        if not _PROM_LINE_RE.match(line):
            bad.append(line)
    return {
        "metric_line_count": count,
        "bad_line_count": len(bad),
        "prometheus_syntax_valid": len(bad) == 0,
        "bad_lines_preview": bad[:10],
    }


class F16ConsolidatedMetricsExporter:
    """F16.9-R2 consolidated JSON and Prometheus exporter.

    This exporter consolidates measurable functional evidence for F16.1-F16.8.
    It does not claim phenomenal subjectivity; it exposes only functional,
    traceable, bounded metrics for distributed civilizational continuity.
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else ROOT
        self.continuity_root = _continuity_root()
        self.cert_root = self.continuity_root / "certifications"
        self.metrics_root = _metrics_root()
        self.dashboard_root = _dashboard_root()
        self.export_root = self.metrics_root / "f16"
        self.prometheus_root = self.metrics_root / "prometheus"
        self.export_root.mkdir(parents=True, exist_ok=True)
        self.prometheus_root.mkdir(parents=True, exist_ok=True)
        self.json_path = self.export_root / "f16_consolidated_metrics.json"
        self.history_path = self.export_root / "f16_consolidated_metrics_history.jsonl"
        self.prometheus_path = self.prometheus_root / "f16_consolidated_metrics.prom"
        self.state_path = self.export_root / "f16_consolidated_metrics_exporter_state.json"

    def _source_paths(self) -> Dict[str, Path]:
        return {
            "f16_1_cloud": self.cert_root / "real_cloud_node_deployment_validator_history.jsonl",
            "f16_2_community": self.cert_root / "real_community_node_certification_history.jsonl",
            "f16_3_founder_loss": self.cert_root / "civilizational_continuity_history.jsonl",
            "f16_4_snapshot_recovery": self.cert_root / "failure_recovery_history.jsonl",
            "f16_5_cross_node_recovery": self.cert_root / "failure_recovery_history.jsonl",
            "f16_6_distributed_certification": self.cert_root / "distributed_civilizational_continuity_certification_history.jsonl",
            "f16_7_long_duration": self.cert_root / "long_duration_distributed_continuity_certification_history.jsonl",
            "f16_8_dashboard": self.dashboard_root / "distributed_continuity_certification_dashboard_registry.json",
        }

    def _dependency_readiness(self) -> Dict[str, Any]:
        available: List[str] = []
        missing: List[str] = []
        for dep in DEPENDENCIES:
            if (self.root / "ontology" / f"{dep}.py").exists():
                available.append(dep)
            else:
                missing.append(dep)
        return {
            "available_dependencies": available,
            "missing_dependencies": missing,
            "dependency_readiness": round(len(available) / max(1, len(DEPENDENCIES)), 6),
        }

    def _load_sources(self, history_limit: int) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, Any]]:
        paths = self._source_paths()
        histories: Dict[str, List[Dict[str, Any]]] = {}
        latest: Dict[str, Any] = {}
        for key, path in paths.items():
            if path.suffix == ".json":
                obj = _load_json(path, {})
                rows = [obj] if isinstance(obj, dict) and obj else []
            else:
                rows = _read_jsonl(path, history_limit)
            histories[key] = rows
            latest[key] = _latest(rows)
        return histories, latest

    def _extract_metrics(
        self,
        latest: Dict[str, Any],
        histories: Dict[str, List[Dict[str, Any]]],
        deps: Dict[str, Any],
    ) -> Dict[str, float]:
        cloud = latest.get("f16_1_cloud", {})
        community = latest.get("f16_2_community", {})
        founder = latest.get("f16_3_founder_loss", {})
        recovery = latest.get("f16_4_snapshot_recovery", {})
        cert = latest.get("f16_6_distributed_certification", {})
        long = latest.get("f16_7_long_duration", {})
        dash = latest.get("f16_8_dashboard", {})

        source_presence = {key: 1.0 if rows else 0.0 for key, rows in histories.items()}
        evidence_coverage = sum(source_presence.values()) / max(1, len(source_presence))

        cloud_score = max(
            _weighted_score([
                (cloud.get("multi_site_resilience_index"), 0.40),
                (cloud.get("cloud_identity_consistency"), 0.10),
                (cloud.get("cloud_node_reachability"), 0.10),
                (cloud.get("cloud_persistence_score"), 0.10),
                (cloud.get("cloud_replication_score"), 0.10),
                (cloud.get("cloud_transport_success"), 0.08),
                (cloud.get("distributed_attention_cloud_score"), 0.04),
                (cloud.get("distributed_governance_cloud_score"), 0.04),
                (cloud.get("distributed_memory_cloud_score"), 0.04),
            ]),
            _clamp(cloud.get("multi_site_resilience_index")),
            1.0 if _safe_bool(cloud.get("validation_passed")) else 0.0,
        )

        community_score = max(
            _clamp(community.get("community_node_certification_index")),
            _clamp(community.get("community_node_readiness")),
            _clamp(community.get("community_certification_score")),
            _clamp(community.get("real_community_node_score")),
            _clamp(community.get("certification_score")),
            1.0 if _safe_bool(community.get("real_community_node_certified")) else 0.0,
            1.0 if _safe_bool(community.get("validation_passed")) else 0.0,
            1.0 if _safe_bool(community.get("success")) and _safe_bool(community.get("community_node_certified")) else 0.0,
        )

        founder_score = max(
            _weighted_score([
                (founder.get("founder_loss_readiness_index"), 0.45),
                (founder.get("civilizational_continuity_score"), 0.25),
                (founder.get("trajectory_continuity_score"), 0.15),
                (founder.get("historical_compatibility_score"), 0.075),
                (founder.get("intergenerational_compatibility_score"), 0.075),
            ]),
            _clamp(founder.get("founder_loss_readiness_index")),
            _clamp(founder.get("civilizational_continuity_score")),
            1.0 if _safe_bool(founder.get("founder_independence_validated")) else 0.0,
        )

        snapshot_score = max(
            _clamp(recovery.get("distributed_snapshot_recovery_index")),
            _weighted_score([
                (recovery.get("distributed_snapshot_recovery_index"), 0.50),
                (recovery.get("recovery_integrity_score"), 0.20),
                (recovery.get("recovery_success_rate"), 0.15),
                (recovery.get("civilizational_survival_ratio"), 0.15),
            ]),
            1.0 if _safe_bool(recovery.get("snapshot_recovery_validated")) else 0.0,
            1.0 if _safe_bool(recovery.get("snapshot_restored_continuity_validated")) else 0.0,
        )

        cross_node_score = max(
            _weighted_score([
                (recovery.get("recovery_success_rate"), 0.35),
                (recovery.get("civilizational_survival_ratio"), 0.30),
                (recovery.get("recovery_integrity_score"), 0.20),
                (recovery.get("recovery_strategy_efficiency"), 0.15),
            ]),
            _clamp(recovery.get("recovery_success_rate")),
            _clamp(recovery.get("civilizational_survival_ratio")),
            1.0 if _safe_bool(recovery.get("recovery_validated")) else 0.0,
        )

        distributed_score = max(
            _clamp(cert.get("continuity_certification_index")),
            _clamp(cert.get("distributed_continuity_score")),
            _clamp(cert.get("distributed_certification_score")),
            _clamp(cert.get("global_distributed_continuity_index")),
            1.0 if _safe_bool(cert.get("distributed_civilization_certified")) else 0.0,
            1.0 if _safe_bool(cert.get("certified")) else 0.0,
            1.0 if _safe_bool(cert.get("success")) else 0.0,
        )

        long_duration_score = max(
            _clamp(long.get("long_duration_certification_index")),
            _clamp(long.get("rolling_continuity_index")),
            _clamp(long.get("longitudinal_certification_score")),
            _clamp(long.get("long_duration_distributed_continuity_index")),
            1.0 if _safe_bool(long.get("long_duration_distributed_continuity_certified")) else 0.0,
            1.0 if _safe_bool(long.get("certified")) else 0.0,
        )

        dashboard_score = max(
            _clamp(dash.get("dashboard_readiness")),
            _clamp(dash.get("dependency_readiness")),
            _clamp(dash.get("dashboard_score")),
            1.0 if _safe_bool(dash.get("success")) or _safe_bool(dash.get("dashboard_generated")) else 0.0,
            1.0 if (self.dashboard_root / "distributed_continuity_certification_dashboard.html").exists() else 0.0,
        )

        stage_scores = [
            cloud_score,
            community_score,
            founder_score,
            snapshot_score,
            cross_node_score,
            distributed_score,
            long_duration_score,
            dashboard_score,
        ]
        consolidated_index = sum(stage_scores) / len(stage_scores)
        certified_stage_count = sum(1 for score in stage_scores if score >= 0.9)
        min_stage_score = min(stage_scores)

        metrics: Dict[str, float] = {
            "f16_1_cloud_validation_score": round(cloud_score, 6),
            "f16_2_community_validation_score": round(community_score, 6),
            "f16_3_founder_loss_survivability_score": round(founder_score, 6),
            "f16_4_snapshot_recovery_score": round(snapshot_score, 6),
            "f16_5_cross_node_recovery_score": round(cross_node_score, 6),
            "f16_6_distributed_certification_score": round(distributed_score, 6),
            "f16_7_long_duration_certification_score": round(long_duration_score, 6),
            "f16_8_dashboard_readiness_score": round(dashboard_score, 6),
            "f16_evidence_coverage_ratio": round(evidence_coverage, 6),
            "f16_dependency_readiness": round(_clamp(deps.get("dependency_readiness")), 6),
            "f16_certified_stage_count": float(certified_stage_count),
            "f16_total_stage_count": float(len(stage_scores)),
            "f16_min_stage_score": round(min_stage_score, 6),
            "f16_consolidated_continuity_index": round(consolidated_index, 6),
            "f16_export_ready": 1.0 if consolidated_index >= 0.9 and evidence_coverage >= 0.75 else 0.0,
            "f16_json_export_present": 1.0 if self.json_path.exists() else 0.0,
            "f16_prometheus_export_present": 1.0 if self.prometheus_path.exists() else 0.0,
        }
        for key, value in source_presence.items():
            metrics[f"{key}_source_present"] = value
        return metrics

    def _render_prometheus(self, metrics: Dict[str, float], source_paths: Dict[str, Path]) -> str:
        lines: List[str] = [
            "# Open Cognitive Ecology F16 consolidated metrics",
            f"# Generated at {_utc()}",
            "# Epistemic boundary: functional distributed-continuity metrics only.",
        ]
        for key in sorted(metrics):
            lines.extend(_prom_line(key, metrics[key], f"F16 consolidated metric: {key}"))
        for key, path in sorted(source_paths.items()):
            present = 1.0 if path.exists() else 0.0
            lines.extend(_prom_line(
                f"f16_source_file_present{{source=\"{key}\"}}",
                present,
                f"F16 source file presence for {key}",
            ))
        return "\n".join(lines) + "\n"

    def step(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        inputs = inputs or {}
        history_limit = int(inputs.get("history_limit", 500))
        persist = bool(inputs.get("persist", True))

        histories, latest = self._load_sources(history_limit)
        deps = self._dependency_readiness()
        metrics = self._extract_metrics(latest, histories, deps)
        source_paths = self._source_paths()
        prometheus_text = self._render_prometheus(metrics, source_paths)
        prometheus_validation = _validate_prometheus(prometheus_text)

        missing_sources = [key for key, rows in histories.items() if not rows]
        result: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "refinement": "F16.9-R2",
            "timestamp_utc": _utc(),
            "epistemic_boundary": "functional_metrics_only_no_phenomenal_subjectivity_claim",
            "json_export_ready": True,
            "prometheus_export_ready": bool(prometheus_validation.get("prometheus_syntax_valid")),
            "grafana_compatible": bool(prometheus_validation.get("prometheus_syntax_valid")),
            "history_recorded": persist,
            "metrics": metrics,
            "source_paths": {key: str(path) for key, path in source_paths.items()},
            "missing_sources": missing_sources,
            "source_count": len(source_paths),
            "sources_available": len(source_paths) - len(missing_sources),
            "dependency_diagnostics": deps,
            "prometheus_validation": prometheus_validation,
            "json_path": str(self.json_path),
            "prometheus_path": str(self.prometheus_path),
            "history_path": str(self.history_path),
            "state_path": str(self.state_path),
            "classification": (
                "F16 Consolidated Metrics Export Certified"
                if metrics.get("f16_export_ready", 0.0) >= 1.0
                and prometheus_validation.get("prometheus_syntax_valid")
                else "F16 Consolidated Metrics Export Operational"
            ),
        }

        if persist:
            self.export_root.mkdir(parents=True, exist_ok=True)
            self.prometheus_root.mkdir(parents=True, exist_ok=True)
            self.json_path.write_text(
                json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            self.prometheus_path.write_text(prometheus_text, encoding="utf-8")
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
            self.state_path.write_text(
                json.dumps({
                    "primitive": PRIMITIVE,
                    "last_run_utc": result["timestamp_utc"],
                    "json_path": str(self.json_path),
                    "prometheus_path": str(self.prometheus_path),
                    "history_path": str(self.history_path),
                    "f16_consolidated_continuity_index": metrics.get("f16_consolidated_continuity_index", 0.0),
                    "prometheus_syntax_valid": prometheus_validation.get("prometheus_syntax_valid"),
                    "refinement": "F16.9-R2",
                }, indent=2, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )

        return result


def step(inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return F16ConsolidatedMetricsExporter().step(inputs)


if __name__ == "__main__":
    print(json.dumps(step(), indent=2, ensure_ascii=False, sort_keys=True))
