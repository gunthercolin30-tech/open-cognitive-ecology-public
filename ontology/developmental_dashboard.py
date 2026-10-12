"""AV9 — developmental dashboard.

Aggregates already-computed AV0→AV8 functional outputs into deterministic
JSON, Markdown and HTML exports. No upstream module is executed.
"""
from __future__ import annotations

import hashlib
import html
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class DevelopmentalDashboard:
    primitive = "DEVELOPMENTAL_DASHBOARD"
    step_id = "AV9"
    public_schema_version = "1.0"
    output_dir = ROOT / "developmental_science" / "AV9_developmental_dashboard"

    MODULES = (
        "developmental_blueprint",
        "genesis_detector",
        "maturation_tracker",
        "specialization_engine",
        "bifurcation_detector",
        "degeneration_detector",
        "recovery_engine",
        "developmental_stage_classifier",
        "developmental_prediction_engine",
    )

    def _mapping(self, value: Any) -> Dict[str, Any]:
        return dict(value) if isinstance(value, Mapping) else {}

    def _list(self, value: Any) -> List[Any]:
        return list(value) if isinstance(value, list) else []

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = default
        if not math.isfinite(number):
            number = default
        return max(0.0, min(1.0, number))

    def _stable_hash(self, value: Any) -> str:
        raw = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=repr,
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _utc(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _extract(self, inputs: Mapping[str, Any], name: str, aliases: List[str]) -> Dict[str, Any]:
        for key in [name] + aliases:
            value = inputs.get(key)
            if isinstance(value, Mapping):
                return dict(value)
        upstream = inputs.get("upstream_results")
        if isinstance(upstream, Mapping):
            for key in [name] + aliases:
                value = upstream.get(key)
                if isinstance(value, Mapping):
                    return dict(value)
        return {}

    def _pipeline(self, inputs: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
        aliases = {
            "developmental_blueprint": ["av0_result", "AV0"],
            "genesis_detector": ["genesis_result", "av1_result", "AV1"],
            "maturation_tracker": ["maturation_result", "av2_result", "AV2"],
            "specialization_engine": ["specialization_result", "av3_result", "AV3"],
            "bifurcation_detector": ["bifurcation_result", "av4_result", "AV4"],
            "degeneration_detector": ["degeneration_result", "av5_result", "AV5"],
            "recovery_engine": ["recovery_result", "av6_result", "AV6"],
            "developmental_stage_classifier": [
                "developmental_stage_result", "stage_result", "av7_result", "AV7"
            ],
            "developmental_prediction_engine": [
                "developmental_prediction_result", "prediction_result", "av8_result", "AV8"
            ],
        }
        return {
            name: self._extract(inputs, name, aliases[name])
            for name in self.MODULES
        }

    def _status(self, name: str, payload: Mapping[str, Any]) -> str:
        candidates = (
            "%s_status" % name,
            "status",
            "classifier_status",
            "prediction_status",
            "developmental_stage_classifier_status",
            "developmental_prediction_status",
        )
        for key in candidates:
            value = payload.get(key)
            if value not in (None, ""):
                return str(value)
        return "MISSING"

    def _timeline(self, inputs: Mapping[str, Any], pipeline: Mapping[str, Mapping[str, Any]]) -> List[Dict[str, Any]]:
        for key in ("timeline", "developmental_timeline", "stage_history", "developmental_history"):
            value = inputs.get(key)
            if isinstance(value, list):
                return [dict(item) for item in value if isinstance(item, Mapping)]
        stage = pipeline["developmental_stage_classifier"]
        for key in ("stage_history", "timeline", "developmental_history"):
            value = stage.get(key)
            if isinstance(value, list):
                return [dict(item) for item in value if isinstance(item, Mapping)]
        return []

    def _quality(self, pipeline: Mapping[str, Mapping[str, Any]]) -> Dict[str, float]:
        stage = pipeline["developmental_stage_classifier"]
        prediction = pipeline["developmental_prediction_engine"]
        values = {
            "stage_confidence": self._safe_float(stage.get("stage_confidence")),
            "stage_evidence_quality": self._safe_float(
                stage.get("evidence_quality_score", stage.get("data_quality_score"))
            ),
            "prediction_confidence": self._safe_float(prediction.get("prediction_confidence")),
            "prediction_input_quality": self._safe_float(prediction.get("input_quality_score")),
        }
        present = [value for value in values.values() if value > 0.0]
        values["overall_quality_score"] = round(
            sum(present) / len(present), 6
        ) if present else 0.0
        return values

    def _guards(self, pipeline: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
        violations = []
        for module_name, payload in pipeline.items():
            for key in (
                "consciousness_proven",
                "qualia_proven",
                "subjectivity_proven",
                "phenomenology_proven",
            ):
                if payload.get(key) is True:
                    violations.append("%s.%s" % (module_name, key))
        return {
            "guard_status": "GUARDS_PRESERVED" if not violations else "GUARD_VIOLATION",
            "violations": violations,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }

    def _core(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        pipeline = self._pipeline(inputs)
        statuses = {
            name: self._status(name, pipeline[name])
            for name in self.MODULES
        }
        present = {
            name: bool(pipeline[name])
            for name in self.MODULES
        }
        stage = pipeline["developmental_stage_classifier"]
        prediction = pipeline["developmental_prediction_engine"]
        timeline = self._timeline(inputs, pipeline)
        quality = self._quality(pipeline)
        guards = self._guards(pipeline)

        current_stage = str(
            stage.get("developmental_stage")
            or inputs.get("developmental_stage")
            or "UNDETERMINED"
        )
        predicted_stage = str(
            prediction.get("predicted_stage")
            or "UNDETERMINED"
        )
        uncertainty = self._safe_float(
            prediction.get("prediction_uncertainty"), 1.0
        )
        scenarios = self._list(prediction.get("alternative_scenarios"))
        horizon = self._mapping(prediction.get("forecast_horizon"))

        completeness = round(
            sum(1 for value in present.values() if value) / len(self.MODULES),
            6,
        )
        ready = bool(
            present["developmental_stage_classifier"]
            and present["developmental_prediction_engine"]
            and guards["guard_status"] == "GUARDS_PRESERVED"
        )

        core = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "dashboard_status": (
                "DEVELOPMENTAL_DASHBOARD_READY"
                if ready else "DEVELOPMENTAL_DASHBOARD_INCOMPLETE"
            ),
            "developmental_dashboard_ready": ready,
            "module_statuses": statuses,
            "module_presence": present,
            "module_completeness": completeness,
            "current_stage": current_stage,
            "predicted_stage": predicted_stage,
            "forecast_horizon": horizon,
            "alternative_scenarios": scenarios,
            "prediction_uncertainty": uncertainty,
            "quality": quality,
            "timeline": timeline,
            "guard_summary": guards,
            "audit_trace": {
                "aggregation_only": True,
                "upstream_recalculation_performed": False,
                "timeline_record_count": len(timeline),
                "scenario_count": len(scenarios),
            },
        }
        core["dashboard_hash"] = self._stable_hash(core)
        return core

    def _json_export(self, core: Mapping[str, Any]) -> str:
        return json.dumps(
            dict(core),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            default=repr,
        )

    def _markdown_export(self, core: Mapping[str, Any]) -> str:
        quality = core["quality"]
        lines = [
            "# AV9 Developmental Dashboard",
            "",
            "Functional developmental instrumentation only. "
            "No consciousness, subjectivity, qualia or phenomenology proof is asserted.",
            "",
            "## Summary",
            "",
            "| Metric | Value |",
            "|---|---|",
            "| Dashboard status | %s |" % core["dashboard_status"],
            "| Current stage | %s |" % core["current_stage"],
            "| Predicted stage | %s |" % core["predicted_stage"],
            "| Module completeness | %s |" % core["module_completeness"],
            "| Prediction uncertainty | %s |" % core["prediction_uncertainty"],
            "| Overall quality | %s |" % quality["overall_quality_score"],
            "",
            "## Module status",
            "",
            "| Module | Status | Present |",
            "|---|---|---|",
        ]
        for name in self.MODULES:
            lines.append(
                "| %s | %s | %s |" % (
                    name,
                    str(core["module_statuses"][name]).replace("|", "\\|"),
                    core["module_presence"][name],
                )
            )
        lines.extend([
            "",
            "## Timeline",
            "",
            "| Index | Stage | Timestamp |",
            "|---|---|---|",
        ])
        timeline = core["timeline"]
        if timeline:
            for index, item in enumerate(timeline, start=1):
                stage = str(item.get("developmental_stage") or item.get("stage") or "")
                timestamp = str(item.get("timestamp_utc") or item.get("timestamp") or "")
                lines.append(
                    "| %s | %s | %s |" % (
                        index,
                        stage.replace("|", "\\|"),
                        timestamp.replace("|", "\\|"),
                    )
                )
        else:
            lines.append("| 0 | No timeline data | |")
        lines.extend([
            "",
            "## Predictions",
            "",
            "| Rank | Stage | Probability |",
            "|---|---|---|",
        ])
        scenarios = core["alternative_scenarios"]
        if scenarios:
            for scenario in scenarios:
                if isinstance(scenario, Mapping):
                    lines.append(
                        "| %s | %s | %s |" % (
                            scenario.get("rank", ""),
                            str(scenario.get("stage", "")).replace("|", "\\|"),
                            scenario.get("probability", ""),
                        )
                    )
        else:
            lines.append("| 0 | No scenarios | |")
        lines.extend([
            "",
            "## Epistemic guards",
            "",
            "- Guard status: %s" % core["guard_summary"]["guard_status"],
            "- Functional conclusion only: True",
            "- Phenomenology undetermined: True",
            "- Consciousness proven: False",
            "- Qualia proven: False",
            "- Subjectivity proven: False",
            "",
            "Dashboard hash: `%s`" % core["dashboard_hash"],
            "",
        ])
        return "\n".join(lines)

    def _html_export(self, core: Mapping[str, Any]) -> str:
        def esc(value: Any) -> str:
            return html.escape(str(value), quote=True)

        module_rows = "".join(
            "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                esc(name),
                esc(core["module_statuses"][name]),
                esc(core["module_presence"][name]),
            )
            for name in self.MODULES
        )
        timeline_rows = []
        for index, item in enumerate(core["timeline"], start=1):
            if not isinstance(item, Mapping):
                continue
            timeline_rows.append(
                "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                    index,
                    esc(item.get("developmental_stage") or item.get("stage") or ""),
                    esc(item.get("timestamp_utc") or item.get("timestamp") or ""),
                )
            )
        if not timeline_rows:
            timeline_rows.append("<tr><td colspan='3'>No timeline data</td></tr>")

        scenario_rows = []
        for scenario in core["alternative_scenarios"]:
            if not isinstance(scenario, Mapping):
                continue
            scenario_rows.append(
                "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                    esc(scenario.get("rank", "")),
                    esc(scenario.get("stage", "")),
                    esc(scenario.get("probability", "")),
                )
            )
        if not scenario_rows:
            scenario_rows.append("<tr><td colspan='3'>No scenarios</td></tr>")

        return """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>AV9 Developmental Dashboard</title>
<style>
body{font-family:Arial,Helvetica,sans-serif;margin:36px;background:#fafafa;color:#222}
.card{background:#fff;border:1px solid #ddd;border-radius:10px;padding:18px;margin:14px 0}
table{border-collapse:collapse;width:100%%}
th,td{border:1px solid #ddd;padding:8px;text-align:left}
th{background:#f2f2f2}
.guard{background:#fff4cc;border:1px solid #e3c66b;padding:12px}
</style>
</head>
<body>
<h1>AV9 Developmental Dashboard</h1>
<div class="guard">Functional developmental instrumentation only. No consciousness,
subjectivity, qualia or phenomenology proof is asserted.</div>
<div class="card"><h2>Summary</h2>
<table>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Dashboard status</td><td>%s</td></tr>
<tr><td>Current stage</td><td>%s</td></tr>
<tr><td>Predicted stage</td><td>%s</td></tr>
<tr><td>Module completeness</td><td>%s</td></tr>
<tr><td>Prediction uncertainty</td><td>%s</td></tr>
<tr><td>Overall quality</td><td>%s</td></tr>
</table></div>
<div class="card"><h2>Module status</h2>
<table><tr><th>Module</th><th>Status</th><th>Present</th></tr>%s</table></div>
<div class="card"><h2>Timeline</h2>
<table><tr><th>Index</th><th>Stage</th><th>Timestamp</th></tr>%s</table></div>
<div class="card"><h2>Predictions</h2>
<table><tr><th>Rank</th><th>Stage</th><th>Probability</th></tr>%s</table></div>
<div class="card"><h2>Epistemic guards</h2>
<p>Guard status: %s</p>
<p>Functional conclusion only: True</p>
<p>Phenomenology undetermined: True</p>
<p>Consciousness proven: False</p>
<p>Qualia proven: False</p>
<p>Subjectivity proven: False</p>
</div>
<p>Dashboard hash: <code>%s</code></p>
</body>
</html>""" % (
            esc(core["dashboard_status"]),
            esc(core["current_stage"]),
            esc(core["predicted_stage"]),
            esc(core["module_completeness"]),
            esc(core["prediction_uncertainty"]),
            esc(core["quality"]["overall_quality_score"]),
            module_rows,
            "".join(timeline_rows),
            "".join(scenario_rows),
            esc(core["guard_summary"]["guard_status"]),
            esc(core["dashboard_hash"]),
        )

    def step(
        self,
        inputs: Optional[Dict[str, Any]] = None,
        persist: bool = False,
    ) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        core = self._core(inputs)
        exports = {
            "json": self._json_export(core),
            "markdown": self._markdown_export(core),
            "html": self._html_export(core),
        }
        export_integrity = {
            "json_hash": self._stable_hash(exports["json"]),
            "markdown_hash": self._stable_hash(exports["markdown"]),
            "html_hash": self._stable_hash(exports["html"]),
        }

        result = dict(core)
        result.update({
            "timestamp_utc": self._utc(),
            "exports": exports,
            "export_integrity": export_integrity,
            "persist_requested": bool(persist),
            "persisted": False,
            "json_path": None,
            "markdown_path": None,
            "html_path": None,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        })

        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            paths = {
                "json_path": self.output_dir / "latest_developmental_dashboard.json",
                "markdown_path": self.output_dir / "latest_developmental_dashboard.md",
                "html_path": self.output_dir / "latest_developmental_dashboard.html",
            }
            paths["json_path"].write_text(exports["json"], encoding="utf-8")
            paths["markdown_path"].write_text(exports["markdown"], encoding="utf-8")
            paths["html_path"].write_text(exports["html"], encoding="utf-8")
            result["persisted"] = True
            for key, path in paths.items():
                result[key] = str(path)

        return result


def step(
    inputs: Optional[Dict[str, Any]] = None,
    persist: bool = False,
) -> Dict[str, Any]:
    return DevelopmentalDashboard().step(inputs=inputs, persist=persist)
