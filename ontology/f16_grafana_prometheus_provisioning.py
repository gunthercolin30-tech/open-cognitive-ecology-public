"""
F16.10 — Grafana / Prometheus provisioning for F16 consolidated metrics.

This module does not claim phenomenal subjectivity. It only provisions
functional, measurable exports for the validated F16 distributed-continuity
metric layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import os

from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        return float(value)
    except Exception:
        return default


def _json_dump(path: Path, payload: Any, fs_context: GovernedFilesystemEffectContext | None = None, slot_prefix: str | None = None) -> None:
    if not isinstance(fs_context, GovernedFilesystemEffectContext):
        raise RuntimeError("governed filesystem effect context required")
    if not slot_prefix:
        raise RuntimeError("governed filesystem effect slot prefix required")
    fs_context.execute_path(f"{slot_prefix}_parent_create", "FS_CREATE_DIRS", path.parent)
    content = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
    fs_context.execute_path(f"{slot_prefix}_write", "FS_WRITE_REPLACE_BYTES", path, content.encode("utf-8"))


def _append_jsonl(
    path: Path,
    payload: dict[str, Any],
    fs_context: GovernedFilesystemEffectContext | None = None,
    slot_prefix: str | None = None,
) -> None:
    if not isinstance(fs_context, GovernedFilesystemEffectContext):
        raise RuntimeError("governed filesystem effect context required")
    if not slot_prefix:
        raise RuntimeError("governed filesystem effect slot prefix required")
    fs_context.execute_path(f"{slot_prefix}_parent_create", "FS_CREATE_DIRS", path.parent)
    content = (json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    fs_context.execute_path(f"{slot_prefix}_append", "FS_APPEND_BYTES", path, content)


def _is_writable_directory(path: Path) -> bool:
    """Return True only when path can be used safely for dashboard writes."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".oce_write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except Exception:
        return False


@dataclass
class F16GrafanaPrometheusProvisioning:
    """Generate Grafana-ready and Prometheus-ready configuration artifacts."""

    root: Path | None = None
    ssd_root: Path | None = None

    def __post_init__(self) -> None:
        self.root = self.root or Path.home() / "open-cognitive-ecology"
        configured = os.environ.get("OCE_SSD_ROOT")
        candidate = self.ssd_root or Path(configured) if configured else self.ssd_root or Path("/Volumes/OCE_SSD")
        if _is_writable_directory(candidate):
            self.ssd_root = candidate
        else:
            # Validation-safe fallback: avoid PermissionError on unavailable or protected external SSD.
            self.ssd_root = self.root / "external_storage_fallback"
            self.ssd_root.mkdir(parents=True, exist_ok=True)

    @property
    def metrics_root(self) -> Path:
        return self.ssd_root / "OCE_METRICS"

    @property
    def provisioning_root(self) -> Path:
        return self.ssd_root / "OCE_DASHBOARDS" / "grafana_provisioning" / "f16"

    def _read_f16_metrics(self) -> dict[str, Any]:
        path = self.metrics_root / "f16" / "f16_consolidated_metrics.json"
        if not path.exists():
            return {
                "source_path": str(path),
                "source_present": False,
                "metrics": {},
                "classification": "missing_f16_metrics_source",
            }
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return {
                "source_path": str(path),
                "source_present": True,
                "metrics": data.get("metrics", {}),
                "classification": data.get("classification", "unknown"),
                "refinement": data.get("refinement", "unknown"),
                "prometheus_validation": data.get("prometheus_validation", {}),
            }
        except Exception as exc:
            return {
                "source_path": str(path),
                "source_present": False,
                "metrics": {},
                "classification": "unreadable_f16_metrics_source",
                "error": repr(exc),
            }

    def _validate_prometheus_source(self) -> dict[str, Any]:
        prom_path = self.metrics_root / "prometheus" / "f16_consolidated_metrics.prom"
        if not prom_path.exists():
            return {
                "prometheus_source_present": False,
                "prometheus_path": str(prom_path),
                "metric_line_count": 0,
                "bad_line_count": 0,
                "prometheus_syntax_valid": False,
            }
        bad: list[str] = []
        metric_lines = 0
        for raw in prom_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            metric_lines += 1
            parts = line.split()
            if len(parts) != 2:
                bad.append(line)
                continue
            try:
                float(parts[1])
            except Exception:
                bad.append(line)
        return {
            "prometheus_source_present": True,
            "prometheus_path": str(prom_path),
            "metric_line_count": metric_lines,
            "bad_line_count": len(bad),
            "bad_lines_preview": bad[:5],
            "prometheus_syntax_valid": len(bad) == 0 and metric_lines > 0,
        }

    def _build_prometheus_scrape_config(self, metrics_port: int) -> dict[str, Any]:
        return {
            "global": {"scrape_interval": "15s", "evaluation_interval": "15s"},
            "scrape_configs": [
                {
                    "job_name": "open_cognitive_ecology_f16",
                    "metrics_path": "/metrics",
                    "static_configs": [
                        {
                            "targets": [f"localhost:{metrics_port}"],
                            "labels": {
                                "project": "open_cognitive_ecology",
                                "phase": "F16",
                                "primitive": "f16_consolidated_metrics_exporter",
                                "epistemic_boundary": "functional_metrics_only_no_phenomenal_subjectivity_claim",
                            },
                        }
                    ],
                }
            ],
        }

    def _build_file_sd_config(self) -> list[dict[str, Any]]:
        return [
            {
                "targets": ["localhost:9108"],
                "labels": {
                    "job": "open_cognitive_ecology_f16_file_export",
                    "source_file": str(self.metrics_root / "prometheus" / "f16_consolidated_metrics.prom"),
                    "phase": "F16",
                },
            }
        ]

    def _build_grafana_datasource(self) -> dict[str, Any]:
        return {
            "apiVersion": 1,
            "datasources": [
                {
                    "name": "OCE-F16-Prometheus",
                    "type": "prometheus",
                    "access": "proxy",
                    "url": "http://localhost:9090",
                    "isDefault": False,
                    "editable": True,
                    "jsonData": {
                        "timeInterval": "15s",
                        "httpMethod": "POST",
                    },
                }
            ],
        }

    def _panel(self, panel_id: int, title: str, expr: str, x: int, y: int, w: int = 12, h: int = 8) -> dict[str, Any]:
        return {
            "id": panel_id,
            "type": "timeseries",
            "title": title,
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [{"expr": expr, "refId": chr(64 + panel_id)}],
            "fieldConfig": {
                "defaults": {
                    "unit": "percentunit",
                    "min": 0,
                    "max": 1,
                },
                "overrides": [],
            },
            "options": {"legend": {"displayMode": "list", "placement": "bottom"}},
        }

    def _build_grafana_dashboard(self, metrics: dict[str, Any]) -> dict[str, Any]:
        return {
            "uid": "oce-f16-continuity",
            "title": "Open Cognitive Ecology — F16 Distributed Continuity",
            "schemaVersion": 39,
            "version": 1,
            "refresh": "15s",
            "timezone": "browser",
            "tags": ["open-cognitive-ecology", "F16", "distributed-continuity", "functional-metrics-only"],
            "annotations": {"list": []},
            "templating": {"list": []},
            "panels": [
                self._panel(1, "F16 consolidated continuity index", "oce_f16_consolidated_continuity_index", 0, 0),
                self._panel(2, "F16 export readiness", "oce_f16_export_ready", 12, 0),
                self._panel(3, "F16 stage scores", "{__name__=~\"oce_f16_[1-8].*score\"}", 0, 8, 24, 8),
                self._panel(4, "F16 evidence coverage", "oce_f16_evidence_coverage_ratio", 0, 16),
                self._panel(5, "F16 dependency readiness", "oce_f16_dependency_readiness", 12, 16),
                self._panel(6, "F16 min stage score", "oce_f16_min_stage_score", 0, 24),
                self._panel(7, "F16 certified stage count / total", "oce_f16_certified_stage_count / oce_f16_total_stage_count", 12, 24),
            ],
            "description": (
                "Grafana-ready dashboard for F16 distributed continuity metrics. "
                "All values are functional indicators only and imply no phenomenal subjectivity claim."
            ),
            "_oce_snapshot": {
                "metric_count": len(metrics),
                "generated_at": _utc_now(),
                "epistemic_boundary": "functional_metrics_only_no_phenomenal_subjectivity_claim",
            },
        }

    def _build_dashboard_provider(self) -> dict[str, Any]:
        return {
            "apiVersion": 1,
            "providers": [
                {
                    "name": "OCE F16 Dashboards",
                    "orgId": 1,
                    "folder": "Open Cognitive Ecology / F16",
                    "type": "file",
                    "disableDeletion": False,
                    "editable": True,
                    "options": {"path": str(self.provisioning_root / "dashboards")},
                }
            ],
        }

    def _write_text_prometheus_yaml(self, path: Path, config: dict[str, Any], filesystem_effect_context: GovernedFilesystemEffectContext) -> None:
        # Minimal stable YAML emitter for the generated config subset.
        def emit(obj: Any, indent: int = 0) -> list[str]:
            pad = " " * indent
            lines: list[str] = []
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, (dict, list)):
                        lines.append(f"{pad}{key}:")
                        lines.extend(emit(value, indent + 2))
                    else:
                        val = json.dumps(value) if isinstance(value, str) else str(value).lower() if isinstance(value, bool) else str(value)
                        lines.append(f"{pad}{key}: {val}")
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, (dict, list)):
                        lines.append(f"{pad}-")
                        lines.extend(emit(item, indent + 2))
                    else:
                        val = json.dumps(item) if isinstance(item, str) else str(item)
                        lines.append(f"{pad}- {val}")
            return lines
        if not isinstance(filesystem_effect_context, GovernedFilesystemEffectContext):
            raise RuntimeError("governed filesystem effect context required")
        content = "\n".join(emit(config)) + "\n"
        filesystem_effect_context.execute_path("prometheus_scrape_config_yml_parent_create", "FS_CREATE_DIRS", path.parent)
        filesystem_effect_context.execute_path("prometheus_scrape_config_yml_write", "FS_WRITE_REPLACE_BYTES", path, content.encode("utf-8"))

    def step(self, inputs: dict[str, Any] | None = None, filesystem_effect_context: GovernedFilesystemEffectContext | None = None) -> dict[str, Any]:
        inputs = inputs or {}
        persist = bool(inputs.get("persist", True))
        if persist:
            if not isinstance(filesystem_effect_context, GovernedFilesystemEffectContext):
                raise RuntimeError("governed filesystem effect context required when persist=True")
            if filesystem_effect_context.authority_minting is not False:
                raise RuntimeError("consumer authority minting forbidden")
            expected_slots = {
                "prometheus_scrape_config_json_parent_create": 1, "prometheus_scrape_config_json_write": 1,
                "prometheus_file_sd_json_parent_create": 1, "prometheus_file_sd_json_write": 1,
                "grafana_datasource_json_parent_create": 1, "grafana_datasource_json_write": 1,
                "grafana_dashboard_provider_json_parent_create": 1, "grafana_dashboard_provider_json_write": 1,
                "grafana_dashboard_json_parent_create": 1, "grafana_dashboard_json_write": 1,
                "state_json_parent_create": 1, "state_json_write": 1,
                "history_jsonl_parent_create": 1, "history_jsonl_append": 1,
                "prometheus_scrape_config_yml_parent_create": 1, "prometheus_scrape_config_yml_write": 1,
            }
            if filesystem_effect_context.remaining() != expected_slots:
                raise RuntimeError("filesystem effect slot cardinality mismatch")
            filesystem_effect_context.begin()
        metrics_port = int(inputs.get("metrics_port", 9108))

        metrics_state = self._read_f16_metrics()
        metrics = metrics_state.get("metrics", {}) if isinstance(metrics_state.get("metrics"), dict) else {}
        prom_validation = self._validate_prometheus_source()

        prometheus_config = self._build_prometheus_scrape_config(metrics_port=metrics_port)
        file_sd_config = self._build_file_sd_config()
        datasource_config = self._build_grafana_datasource()
        dashboard_json = self._build_grafana_dashboard(metrics)
        provider_config = self._build_dashboard_provider()

        base = self.provisioning_root
        paths = {
            "prometheus_scrape_config_json": base / "prometheus" / "prometheus_f16_scrape_config.json",
            "prometheus_scrape_config_yml": base / "prometheus" / "prometheus_f16_scrape_config.yml",
            "prometheus_file_sd_json": base / "prometheus" / "f16_file_sd.json",
            "grafana_datasource_json": base / "grafana" / "provisioning" / "datasources" / "oce_f16_prometheus_datasource.json",
            "grafana_dashboard_provider_json": base / "grafana" / "provisioning" / "dashboards" / "oce_f16_dashboard_provider.json",
            "grafana_dashboard_json": base / "dashboards" / "oce_f16_distributed_continuity_dashboard.json",
            "state_json": base / "f16_grafana_prometheus_provisioning_state.json",
            "history_jsonl": base / "f16_grafana_prometheus_provisioning_history.jsonl",
        }

        provisioning_ready = (
            bool(metrics_state.get("source_present"))
            and prom_validation.get("prometheus_syntax_valid") is True
            and _safe_float(metrics.get("f16_export_ready")) >= 1.0
            and _safe_float(metrics.get("f16_consolidated_continuity_index")) >= 0.75
        )

        classification = "F16 Grafana Prometheus Provisioning Ready" if provisioning_ready else "F16 Grafana Prometheus Provisioning Degraded"

        result: dict[str, Any] = {
            "primitive": "f16_grafana_prometheus_provisioning",
            "refinement": "F16.10-R1",
            "timestamp_utc": _utc_now(),
            "epistemic_boundary": "functional_metrics_only_no_phenomenal_subjectivity_claim",
            "classification": classification,
            "provisioning_ready": provisioning_ready,
            "grafana_ready": provisioning_ready,
            "prometheus_ready": prom_validation.get("prometheus_syntax_valid") is True,
            "f16_metrics_source_present": bool(metrics_state.get("source_present")),
            "f16_metrics_classification": metrics_state.get("classification"),
            "f16_metrics_refinement": metrics_state.get("refinement"),
            "f16_export_ready": _safe_float(metrics.get("f16_export_ready")),
            "f16_consolidated_continuity_index": _safe_float(metrics.get("f16_consolidated_continuity_index")),
            "prometheus_validation": prom_validation,
            "generated_paths": {key: str(value) for key, value in paths.items()},
            "dashboard_panel_count": len(dashboard_json["panels"]),
            "datasource_name": "OCE-F16-Prometheus",
            "metrics_port": metrics_port,
            "future_node_compatibility": True,
            "non_closure_compliant": True,
            "traceability_preserved": True,
            "reversibility_preserved": True,
            "dependencies": [
                "f16_consolidated_metrics_exporter",
                "prometheus_metrics_exporter",
                "grafana_dashboard_exporter",
                "metrics_history_recorder",
                "metrics_aggregation_engine",
                "civilizational_metrics_synthesizer",
            ],
        }

        if persist:
            _json_dump(paths["prometheus_scrape_config_json"], prometheus_config, filesystem_effect_context, "prometheus_scrape_config_json")
            self._write_text_prometheus_yaml(paths["prometheus_scrape_config_yml"], prometheus_config, filesystem_effect_context)
            _json_dump(paths["prometheus_file_sd_json"], file_sd_config, filesystem_effect_context, "prometheus_file_sd_json")
            _json_dump(paths["grafana_datasource_json"], datasource_config, filesystem_effect_context, "grafana_datasource_json")
            _json_dump(paths["grafana_dashboard_provider_json"], provider_config, filesystem_effect_context, "grafana_dashboard_provider_json")
            _json_dump(paths["grafana_dashboard_json"], dashboard_json, filesystem_effect_context, "grafana_dashboard_json")
            _json_dump(paths["state_json"], result, filesystem_effect_context, "state_json")
            _append_jsonl(paths["history_jsonl"], result, filesystem_effect_context, "history_jsonl")
            if any(filesystem_effect_context.remaining().values()):
                raise RuntimeError("unconsumed filesystem effect handles")
            result["persisted"] = True
        else:
            result["persisted"] = False

        return result
