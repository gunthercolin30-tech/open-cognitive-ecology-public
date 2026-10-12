from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import html
import json


class PredictionDashboard:
    """AT9 — Export RF* prediction state as auditable dashboard artifacts.

    The dashboard aggregates AT1–AT8 outputs into JSON, Markdown, HTML and
    Prometheus-compatible text. It is an instrumentation layer only: it does
    not certify phenomenal consciousness or subjectivity.
    """

    primitive = "PREDICTION_DASHBOARD"
    step_name = "AT9"
    public_schema_version = "1.0.0"

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = inputs or {}
        context = self._build_context(inputs)
        artifacts = self._build_artifacts(context)

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_name,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "dashboard_status": "PREDICTION_DASHBOARD_READY",
            "prediction_count": len(context["predictions"]),
            "displayed_prediction_count": len(context["dashboard_rows"]),
            "validated_prediction_count": context["status_counts"].get("validated", 0),
            "invalidated_prediction_count": context["status_counts"].get("invalidated", 0),
            "ambiguous_prediction_count": context["status_counts"].get("ambiguous", 0),
            "unknown_prediction_count": context["status_counts"].get("unknown", 0),
            "tested_prediction_count": context["status_counts"].get("tested", 0),
            "predictive_power_index": context["ppi"],
            "ppi": context["ppi"],
            "dashboard_rows": context["dashboard_rows"],
            "status_counts": context["status_counts"],
            "category_counts": context["category_counts"],
            "confidence_summary": context["confidence_summary"],
            "exports": {
                "json": artifacts["json"],
                "markdown": artifacts["markdown"],
                "html": artifacts["html"],
                "prometheus": artifacts["prometheus"],
            },
            "export_policy": {
                "formats": ["json", "markdown", "html", "prometheus"],
                "auditability": "all_rows_preserve_prediction_id_status_category_confidence_history_count",
                "persistence": "optional_under_predictive_theory/dashboard",
            },
            "validation_policy": {
                "status_source_priority": ["prediction_validation_tracker", "validation_history", "prediction_record", "default_unknown"],
                "allowed_statuses": ["unknown", "tested", "validated", "invalidated", "ambiguous"],
                "dashboard_is_not_validation": True,
            },
            "falsification_policy": {
                "invalidated_predictions_visible": True,
                "ambiguous_predictions_visible": True,
                "unknown_predictions_not_counted_as_validated": True,
            },
            "epistemic_guards": self._epistemic_guards(),
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "persist_requested": bool(persist),
            "persisted": False,
            "export_paths": {},
            "html_path": None,
            "json_path": None,
            "markdown_path": None,
            "prometheus_path": None,
        }

        if persist:
            paths = self._persist(result)
            result["persisted"] = True
            result["export_paths"] = {k: str(v) for k, v in paths.items()}
            result["html_path"] = str(paths["html"])
            result["json_path"] = str(paths["json"])
            result["markdown_path"] = str(paths["markdown"])
            result["prometheus_path"] = str(paths["prometheus"])

        return result

    def _build_context(self, inputs: dict[str, Any]) -> dict[str, Any]:
        predictions = self._extract_predictions(inputs)
        history = self._extract_history(inputs)
        status_by_id = self._status_by_id(history)
        ppi = self._extract_ppi(inputs)

        rows = []
        status_counts = {"unknown": 0, "tested": 0, "validated": 0, "invalidated": 0, "ambiguous": 0}
        category_counts: dict[str, int] = {}
        confidences = []

        for idx, pred in enumerate(predictions, start=1):
            pid = self._prediction_id(pred, idx)
            status = self._normalize_status(status_by_id.get(pid) or pred.get("status") or pred.get("validation_status") or "unknown")
            category = str(pred.get("category") or pred.get("prediction_category") or pred.get("type") or "uncategorized")
            confidence = self._confidence(pred, inputs)
            if confidence is not None:
                confidences.append(confidence)
            statement = str(pred.get("statement") or pred.get("prediction") or pred.get("expected_observation") or pred.get("observable") or pid)
            rows.append({
                "prediction_id": pid,
                "statement": statement,
                "category": category,
                "status": status,
                "confidence": confidence,
                "history_count": self._history_count(history, pid),
                "has_falsification_protocol": self._has_related(pid, inputs, ["falsification_protocols", "protocols"]),
                "has_measurable_signature": self._has_related(pid, inputs, ["measurable_signatures", "signatures"]),
                "is_discriminative": self._has_related(pid, inputs, ["discriminative_predictions", "discrimination_results"]),
                "is_unexpected": self._has_related(pid, inputs, ["unexpected_predictions", "surprising_predictions"]),
            })
            status_counts[status] = status_counts.get(status, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1

        return {
            "predictions": predictions,
            "dashboard_rows": rows,
            "status_counts": status_counts,
            "category_counts": category_counts,
            "confidence_summary": self._confidence_summary(confidences),
            "ppi": ppi,
        }

    def _extract_predictions(self, inputs: dict[str, Any]) -> list[dict[str, Any]]:
        candidates: list[Any] = []
        candidates.extend(self._extract_list(inputs, ["theorem_predictions", "predictions", "prediction_registry"]))
        for key in ("theorem_prediction_generator", "prediction_registry_result", "at2"):
            if isinstance(inputs.get(key), dict):
                candidates.extend(self._extract_list(inputs[key], ["theorem_predictions", "predictions"]))
        normalized = []
        for idx, item in enumerate(candidates, start=1):
            if isinstance(item, dict):
                normalized.append(dict(item))
            else:
                normalized.append({"prediction_id": f"PRED-{idx:04d}", "statement": str(item)})
        return normalized or self._synthetic_predictions()

    def _extract_history(self, inputs: dict[str, Any]) -> list[dict[str, Any]]:
        history: list[Any] = []
        history.extend(self._extract_list(inputs, ["validation_history", "prediction_validation_history", "tracker_history"]))
        for key in ("prediction_validation_tracker", "at7", "tracker_result"):
            if isinstance(inputs.get(key), dict):
                history.extend(self._extract_list(inputs[key], ["validation_history", "prediction_validation_history", "tracker_history"]))
        return [h for h in history if isinstance(h, dict)]

    def _extract_ppi(self, inputs: dict[str, Any]) -> float | None:
        for key in ("predictive_power_index", "ppi"):
            if key in inputs:
                return self._safe_float(inputs.get(key))
        for container in ("predictive_power_index_result", "at8", "ppi_result"):
            val = inputs.get(container)
            if isinstance(val, dict):
                for key in ("predictive_power_index", "ppi"):
                    if key in val:
                        return self._safe_float(val.get(key))
        return None

    def _extract_list(self, source: dict[str, Any], keys: list[str]) -> list[Any]:
        for key in keys:
            value = source.get(key)
            if isinstance(value, list):
                return value
            if isinstance(value, dict):
                return list(value.values())
        return []

    def _status_by_id(self, history: list[dict[str, Any]]) -> dict[str, str]:
        status = {}
        for record in history:
            pid = str(record.get("prediction_id") or record.get("id") or "")
            if pid:
                status[pid] = self._normalize_status(record.get("status", "unknown"))
        return status

    def _prediction_id(self, pred: dict[str, Any], idx: int) -> str:
        return str(pred.get("prediction_id") or pred.get("id") or pred.get("signature_id") or f"PRED-{idx:04d}")

    def _normalize_status(self, status: Any) -> str:
        s = str(status).lower().strip()
        if s in {"validated", "valid", "confirmed", "supported"}:
            return "validated"
        if s in {"invalidated", "refuted", "failed", "falsified"}:
            return "invalidated"
        if s in {"ambiguous", "mixed", "uncertain"}:
            return "ambiguous"
        if s in {"tested", "testée", "tested_not_validated"}:
            return "tested"
        return "unknown"

    def _confidence(self, pred: dict[str, Any], inputs: dict[str, Any]) -> float | None:
        for key in ("confidence", "prediction_confidence", "confidence_score"):
            if key in pred:
                return self._safe_float(pred.get(key))
        if "default_confidence" in inputs:
            return self._safe_float(inputs.get("default_confidence"))
        return None

    def _safe_float(self, value: Any) -> float | None:
        try:
            val = float(value)
            return max(0.0, min(1.0, val))
        except Exception:
            return None

    def _history_count(self, history: list[dict[str, Any]], pid: str) -> int:
        return sum(1 for h in history if str(h.get("prediction_id") or h.get("id") or "") == pid)

    def _has_related(self, pid: str, inputs: dict[str, Any], keys: list[str]) -> bool:
        items = self._extract_list(inputs, keys)
        for item in items:
            if isinstance(item, dict):
                if str(item.get("prediction_id") or item.get("id") or "") == pid:
                    return True
            elif str(item) == pid:
                return True
        return False

    def _confidence_summary(self, confidences: list[float]) -> dict[str, Any]:
        if not confidences:
            return {"count": 0, "mean": None, "min": None, "max": None}
        return {
            "count": len(confidences),
            "mean": round(sum(confidences) / len(confidences), 6),
            "min": min(confidences),
            "max": max(confidences),
        }

    def _build_artifacts(self, context: dict[str, Any]) -> dict[str, str]:
        dashboard_json = json.dumps({
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "primitive": self.primitive,
            "step": self.step_name,
            "predictive_power_index": context["ppi"],
            "status_counts": context["status_counts"],
            "category_counts": context["category_counts"],
            "confidence_summary": context["confidence_summary"],
            "predictions": context["dashboard_rows"],
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
        }, indent=2, sort_keys=True)
        markdown = self._markdown(context)
        html_doc = self._html(context)
        prometheus = self._prometheus(context)
        return {"json": dashboard_json, "markdown": markdown, "html": html_doc, "prometheus": prometheus}

    def _markdown(self, context: dict[str, Any]) -> str:
        lines = [
            "# RF* Prediction Dashboard",
            "",
            f"- Step: {self.step_name}",
            f"- Prediction count: {len(context['dashboard_rows'])}",
            f"- Predictive Power Index: {context['ppi']}",
            "- Scope: functional predictive instrumentation only",
            "",
            "| Prediction ID | Category | Status | Confidence | Protocol | Signature | Discriminative | Unexpected |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for row in context["dashboard_rows"]:
            lines.append(
                f"| {row['prediction_id']} | {row['category']} | {row['status']} | {row['confidence']} | "
                f"{row['has_falsification_protocol']} | {row['has_measurable_signature']} | {row['is_discriminative']} | {row['is_unexpected']} |"
            )
        return "\n".join(lines) + "\n"

    def _html(self, context: dict[str, Any]) -> str:
        rows = []
        for row in context["dashboard_rows"]:
            rows.append(
                "<tr>"
                f"<td>{html.escape(str(row['prediction_id']))}</td>"
                f"<td>{html.escape(str(row['category']))}</td>"
                f"<td>{html.escape(str(row['status']))}</td>"
                f"<td>{html.escape(str(row['confidence']))}</td>"
                f"<td>{html.escape(str(row['statement']))}</td>"
                f"<td>{row['has_falsification_protocol']}</td>"
                f"<td>{row['has_measurable_signature']}</td>"
                f"<td>{row['is_discriminative']}</td>"
                f"<td>{row['is_unexpected']}</td>"
                "</tr>"
            )
        row_html = "".join(rows)
        prediction_count = html.escape(str(len(context["dashboard_rows"])))
        ppi_value = html.escape(str(context["ppi"]))
        return (
            "<!doctype html>\n"
            "<html><head><meta charset='utf-8'><title>RF* Prediction Dashboard</title>\n"
            "<style>"
            "body{font-family:Arial,sans-serif;margin:40px;}"
            "table{border-collapse:collapse;width:100%;}"
            "td,th{border:1px solid #ccc;padding:6px;text-align:left;}"
            "th{background:#f0f0f0}.guard{padding:10px;background:#f8f8f8;border:1px solid #ddd}"
            "</style>\n"
            "</head><body>\n"
            "<h1>RF* Prediction Dashboard</h1>\n"
            "<div class='guard'>Functional predictive instrumentation only. "
            "Phenomenology remains undetermined; consciousness, qualia and subjectivity are not proven.</div>\n"
            "<p><strong>Step:</strong> AT9</p>\n"
            f"<p><strong>Prediction count:</strong> {prediction_count}</p>\n"
            f"<p><strong>Predictive Power Index:</strong> {ppi_value}</p>\n"
            "<table><tr><th>ID</th><th>Category</th><th>Status</th><th>Confidence</th>"
            "<th>Statement</th><th>Protocol</th><th>Signature</th><th>Discriminative</th><th>Unexpected</th></tr>"
            f"{row_html}</table>\n"
            "</body></html>"
        )

    def _prometheus(self, context: dict[str, Any]) -> str:
        lines = [
            "# HELP oce_prediction_count Number of RF* predictions displayed by AT9.",
            "# TYPE oce_prediction_count gauge",
            f"oce_prediction_count {len(context['dashboard_rows'])}",
            "# HELP oce_predictive_power_index Predictive Power Index from AT8 when available.",
            "# TYPE oce_predictive_power_index gauge",
            f"oce_predictive_power_index {context['ppi'] if context['ppi'] is not None else 0.0}",
        ]
        for status, count in sorted(context["status_counts"].items()):
            lines.append(f'oce_prediction_status_count{{status="{status}"}} {count}')
        for category, count in sorted(context["category_counts"].items()):
            safe = str(category).replace('"', '')
            lines.append(f'oce_prediction_category_count{{category="{safe}"}} {count}')
        return "\n".join(lines) + "\n"

    def _synthetic_predictions(self) -> list[dict[str, Any]]:
        return [
            {"prediction_id": "AT9-SYN-001", "statement": "If RF* predictive registry is populated, dashboard rows should be exportable.", "category": "instrumentation", "confidence": 0.8},
            {"prediction_id": "AT9-SYN-002", "statement": "When validation status is unknown, dashboard must not mark prediction as validated.", "category": "governance", "confidence": 0.75},
        ]

    def _epistemic_guards(self) -> dict[str, Any]:
        return {
            "scope": "functional_predictive_dashboard_only",
            "blocks_phenomenal_claims": True,
            "dashboard_does_not_certify_consciousness": True,
            "consciousness_claim_status": "not_proven",
            "qualia_claim_status": "not_proven",
            "subjectivity_claim_status": "not_proven",
            "phenomenology_status": "undetermined",
        }

    def _persist(self, result: dict[str, Any]) -> dict[str, Path]:
        root = Path.home() / "open-cognitive-ecology"
        outdir = root / "predictive_theory" / "dashboard"
        outdir.mkdir(parents=True, exist_ok=True)
        exports = result["exports"]
        paths = {
            "json": outdir / "latest_prediction_dashboard.json",
            "markdown": outdir / "latest_prediction_dashboard.md",
            "html": outdir / "latest_prediction_dashboard.html",
            "prometheus": outdir / "latest_prediction_dashboard.prom",
        }
        paths["json"].write_text(exports["json"], encoding="utf-8")
        paths["markdown"].write_text(exports["markdown"], encoding="utf-8")
        paths["html"].write_text(exports["html"], encoding="utf-8")
        paths["prometheus"].write_text(exports["prometheus"], encoding="utf-8")
        return paths
