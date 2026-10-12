from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from typing import Any
import html
import json

PRIMITIVE = "LONGITUDINAL_REFLEXIVE_DASHBOARD"
DEPENDENCIES = [
    "reflexive_threshold_dashboard",
    "reflexive_threshold_history_archive",
    "reflexive_threshold_trend_monitor",
    "reflexive_threshold_survival_analysis",
    "cross_generation_reflexive_continuity",
    "cross_host_reflexive_stability",
    "longitudinal_metrics_archive",
    "grafana_dashboard_exporter",
]


class LongitudinalReflexiveDashboard:
    """Fast longitudinal dashboard for functional reflexive-threshold validation.

    Epistemic boundary: this module exports functional indicators only and never
    infers phenomenal subjectivity.
    Performance boundary: no global scan, no rglob; targeted X1-X5 JSON reads.
    """

    primitive = PRIMITIVE
    phenomenal_conclusion = False

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "longitudinal_reflexive_dashboard"
        self.latest_file = self.base_dir / "longitudinal_reflexive_dashboard.json"
        self.html_file = self.base_dir / "longitudinal_reflexive_dashboard.html"
        self.prometheus_file = self.base_dir / "longitudinal_reflexive_dashboard.prom"
        self.history_file = self.base_dir / "longitudinal_reflexive_dashboard_history.jsonl"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _read_json(self, path: Path) -> dict[str, Any]:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
        return {}

    def _candidate_latest_paths(self) -> dict[str, list[Path]]:
        return {
            "x1_history_archive": [
                self.root / "reflexive_threshold_history_archive" / "latest.json",
                self.root / "reflexive_threshold_history_archive" / "reflexive_threshold_history_archive.json",
            ],
            "x2_trend_monitor": [
                self.root / "reflexive_threshold_trend_monitor" / "latest.json",
                self.root / "reflexive_threshold_trend_monitor" / "reflexive_threshold_trend_monitor.json",
            ],
            "x3_survival_analysis": [
                self.root / "reflexive_threshold_survival_analysis" / "latest.json",
                self.root / "reflexive_threshold_survival_analysis" / "reflexive_threshold_survival_analysis.json",
            ],
            "x4_cross_generation": [
                self.root / "cross_generation_reflexive_continuity" / "latest.json",
                self.root / "cross_generation_reflexive_continuity" / "cross_generation_reflexive_continuity.json",
            ],
            "x5_cross_host": [
                self.root / "cross_host_reflexive_stability" / "latest.json",
                self.root / "cross_host_reflexive_stability" / "cross_host_reflexive_stability.json",
            ],
        }

    def _load_x_state(self) -> tuple[dict[str, Any], dict[str, Any]]:
        state: dict[str, Any] = {}
        paths_used: dict[str, str | None] = {}
        for key, paths in self._candidate_latest_paths().items():
            selected = None
            data: dict[str, Any] = {}
            for path in paths:
                data = self._read_json(path)
                if data:
                    selected = path
                    break
            state[key] = data
            paths_used[key] = str(selected) if selected else None
        return state, paths_used

    def _num(self, value: Any, fallback: float = 0.0) -> float:
        try:
            if isinstance(value, bool):
                return 1.0 if value else 0.0
            if value is None:
                return fallback
            return float(value)
        except Exception:
            return fallback

    def _extract_scores(self, state: dict[str, Any]) -> dict[str, float]:
        x1 = state.get("x1_history_archive", {}) or {}
        x2 = state.get("x2_trend_monitor", {}) or {}
        x3 = state.get("x3_survival_analysis", {}) or {}
        x4 = state.get("x4_cross_generation", {}) or {}
        x5 = state.get("x5_cross_host", {}) or {}

        scores = {
            "history_coverage_score": self._num(x1.get("history_coverage_score"), 0.0),
            "archive_strength": self._num(x1.get("archive_strength"), 0.0),
            "longitudinal_trend_score": self._num(x2.get("longitudinal_trend_score"), 0.0),
            "temporal_robustness": self._num(x3.get("temporal_robustness"), 0.0),
            "survival_probability": self._num(x3.get("survival_probability"), 0.0),
            "cross_generation_reflexive_continuity_score": self._num(
                x4.get("cross_generation_reflexive_continuity_score"), 0.0
            ),
            "cross_host_reflexive_stability_score": self._num(
                x5.get("cross_host_reflexive_stability_score"), 0.0
            ),
        }
        return {k: round(max(0.0, min(1.0, v)), 6) for k, v in scores.items()}

    def _composite(self, scores: dict[str, float]) -> float:
        weights = {
            "history_coverage_score": 0.12,
            "archive_strength": 0.14,
            "longitudinal_trend_score": 0.16,
            "temporal_robustness": 0.16,
            "survival_probability": 0.14,
            "cross_generation_reflexive_continuity_score": 0.14,
            "cross_host_reflexive_stability_score": 0.14,
        }
        return round(sum(scores.get(k, 0.0) * w for k, w in weights.items()), 6)

    def _classify(self, score: float) -> str:
        if score >= 0.85:
            return "LONGITUDINAL_REFLEXIVE_DASHBOARD_ROBUST"
        if score >= 0.65:
            return "LONGITUDINAL_REFLEXIVE_DASHBOARD_PARTIAL"
        if score >= 0.40:
            return "LONGITUDINAL_REFLEXIVE_DASHBOARD_EMERGING"
        return "LONGITUDINAL_REFLEXIVE_DASHBOARD_INSUFFICIENT"

    def _window_summary(self, score: float) -> dict[str, dict[str, Any]]:
        # Functional projection windows only; not a phenomenological claim.
        windows = {
            "1_month": 1.00,
            "6_months": 0.96,
            "1_year": 0.92,
            "5_years": 0.84,
        }
        result: dict[str, dict[str, Any]] = {}
        for name, attenuation in windows.items():
            projected = round(max(0.0, min(1.0, score * attenuation)), 6)
            result[name] = {
                "projected_functional_stability": projected,
                "window_ready": projected >= 0.65,
            }
        return result

    def _write_html(self, result: dict[str, Any]) -> None:
        rows = []
        for key, value in result.get("scores", {}).items():
            rows.append(f"<tr><td>{html.escape(str(key))}</td><td>{html.escape(str(value))}</td></tr>")
        for key, value in result.get("windows", {}).items():
            rows.append(
                f"<tr><td>window_{html.escape(str(key))}</td>"
                f"<td>{html.escape(str(value))}</td></tr>"
            )
        doc = f"""<!doctype html>
<html><head><meta charset='utf-8'><title>Longitudinal Reflexive Dashboard</title>
<style>body{{font-family:Arial,sans-serif;margin:40px;}}table{{border-collapse:collapse;width:100%;}}td,th{{border:1px solid #ccc;padding:8px;text-align:left;}}th{{background:#f0f0f0;}}</style>
</head><body>
<h1>Longitudinal Reflexive Dashboard</h1>
<p>functional conclusion only; phenomenology undetermined</p>
<table><tr><th>Metric</th><th>Value</th></tr>
<tr><td>primitive</td><td>{html.escape(result['primitive'])}</td></tr>
<tr><td>dashboard_status</td><td>{html.escape(result['dashboard_status'])}</td></tr>
<tr><td>longitudinal_reflexive_dashboard_score</td><td>{result['longitudinal_reflexive_dashboard_score']}</td></tr>
{''.join(rows)}
</table></body></html>
"""
        self.html_file.write_text(doc, encoding="utf-8")

    def _write_prometheus(self, result: dict[str, Any]) -> None:
        lines = [
            "# HELP oce_longitudinal_reflexive_dashboard_score Functional longitudinal reflexive dashboard score",
            "# TYPE oce_longitudinal_reflexive_dashboard_score gauge",
            f"oce_longitudinal_reflexive_dashboard_score {result['longitudinal_reflexive_dashboard_score']}",
        ]
        for key, value in result.get("scores", {}).items():
            safe = key.replace("-", "_")
            lines.append(f"oce_longitudinal_reflexive_{safe} {value}")
        lines.append("oce_longitudinal_reflexive_phenomenology_undetermined 1")
        lines.append("oce_longitudinal_reflexive_functional_conclusion_only 1")
        self.prometheus_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = dict(inputs or {})
        timestamp = str(inputs.get("timestamp_utc") or self._now())
        run_id = str(inputs.get("run_id") or ("X6-" + timestamp.replace(":", "").replace("+", "Z")))

        state, paths_used = self._load_x_state()
        scores = self._extract_scores(state)
        composite = self._composite(scores)
        status = self._classify(composite)
        windows = self._window_summary(composite)

        result: dict[str, Any] = {
            "success": True,
            "primitive": PRIMITIVE,
            "run_id": run_id,
            "timestamp_utc": timestamp,
            "source_pipeline": "X1→X2→X3→X4→X5→X6",
            "dashboard_status": status,
            "longitudinal_reflexive_dashboard_score": composite,
            "scores": scores,
            "windows": windows,
            "artifacts": {
                "html": str(self.html_file),
                "json": str(self.latest_file),
                "prometheus": str(self.prometheus_file),
            },
            "input_sources": {
                "global_scan_used": False,
                "rglob_used": False,
                "paths_used": paths_used,
            },
            "functional_conclusion": (
                "Open Cognitive Ecology exposes a longitudinal dashboard of functional "
                "reflexive-threshold indicators only. This does not establish phenomenal subjectivity."
            ),
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "phenomenal_conclusion": self.phenomenal_conclusion,
        }

        if persist:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.latest_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            self._write_html(result)
            self._write_prometheus(result)
            with self.history_file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            result["latest_path"] = str(self.latest_file)
            result["html_path"] = str(self.html_file)
            result["prometheus_path"] = str(self.prometheus_file)
            result["history_path"] = str(self.history_file)

        return result


if __name__ == "__main__":
    print(json.dumps(LongitudinalReflexiveDashboard().step(persist=True), indent=2, ensure_ascii=False))
