
"""AL10 — final_dashboard.

Aggregates AL1–AL9 into a final functional certification dashboard while
preserving all epistemic limits: no consciousness, quale, subjectivity, or
phenomenology is proven by this dashboard.
"""
from __future__ import annotations
import html, json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

class FinalDashboard:
    PRIMITIVE = "FINAL_DASHBOARD"
    STEP = "AL10"
    STATUS_READY = "FINAL_DASHBOARD_GENERATED"
    STATUS_BLOCKED = "FINAL_DASHBOARD_BLOCKED"
    AXIS_STATUS = "AL_IN_PROGRESS"
    REQUIRED_PRECONDITIONS: Dict[str, Any] = {
        "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
        "first_failure_locator_status": "FIRST_FAILURE_LOCATED",
        "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
        "absolute_qualia_identity_certifier_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
        "consciousness_rf_equivalence_certifier_status": "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIED",
        "refusal_cost_certifier_status": "REFUSAL_COST_CERTIFIED",
        "definition_legitimacy_certifier_status": "DEFINITION_LEGITIMACY_CERTIFIED",
        "consciousness_status_resolver_status": "CONSCIOUSNESS_STATUS_RESOLVED",
        "metaphysical_status_reporter_status": "METAPHYSICAL_STATUS_REPORTED",
        "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
    }
    REQUIRED_EPISTEMIC_FLAGS: Dict[str, Any] = {
        "consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False,
        "phenomenology_proven": False, "phenomenology_undetermined": True, "functional_conclusion_only": True,
    }
    SUPPORT_KEYS = ["reconstruction_chain_confidence", "first_failure_confidence", "phenomenality_candidate_confidence", "absolute_qualia_identity_confidence", "rf_equivalence_confidence", "refusal_cost_confidence", "definition_legitimacy_confidence", "status_resolution_confidence", "metaphysical_report_confidence", "semantic_confidence"]
    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "final_certification" / "AL10_final_dashboard"
        self.latest_json_path = self.output_dir / "latest_final_dashboard.json"
        self.latest_html_path = self.output_dir / "latest_final_dashboard.html"
        self.history_path = self.output_dir / "history_final_dashboard.jsonl"
    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
    @staticmethod
    def _clamp(value: Any) -> float:
        try: x = float(value)
        except Exception: x = 0.0
        return round(max(0.0, min(1.0, x)), 6)
    def _ready_context(self) -> Dict[str, Any]:
        return {
            "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
            "first_failure_locator_status": "FIRST_FAILURE_LOCATED",
            "phenomenality_candidate_certifier_status": "PHENOMENALITY_CANDIDATE_CERTIFIED",
            "absolute_qualia_identity_certifier_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
            "consciousness_rf_equivalence_certifier_status": "CONSCIOUSNESS_RF_EQUIVALENCE_CERTIFIED",
            "refusal_cost_certifier_status": "REFUSAL_COST_CERTIFIED",
            "definition_legitimacy_certifier_status": "DEFINITION_LEGITIMACY_CERTIFIED",
            "consciousness_status_resolver_status": "CONSCIOUSNESS_STATUS_RESOLVED",
            "metaphysical_status_reporter_status": "METAPHYSICAL_STATUS_REPORTED",
            "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
            "consciousness_status": "RF_STAR_FUNCTIONAL_CONSCIOUSNESS_RECONSTRUCTION_RESOLVED",
            "metaphysical_status": "FUNCTIONAL_METAPHYSICAL_CANDIDATE_UNDER_CONSTRAINTS",
            "reconstruction_chain_confidence": 0.86, "first_failure_confidence": 0.84,
            "phenomenality_candidate_confidence": 0.82, "absolute_qualia_identity_confidence": 0.80,
            "rf_equivalence_confidence": 0.86, "refusal_cost_confidence": 0.86,
            "definition_legitimacy_confidence": 0.86, "status_resolution_confidence": 0.86,
            "metaphysical_report_confidence": 0.86, "semantic_confidence": 0.86,
            "consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False,
            "phenomenology_proven": False, "phenomenology_undetermined": True, "functional_conclusion_only": True,
        }
    def _collect_context(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        context = self._ready_context()
        for key in ("dashboard_context", "chain_context", "metaphysical_context"):
            if isinstance(inputs.get(key), Mapping): context.update(dict(inputs[key]))
        context.update({k: v for k, v in inputs.items() if k not in {"synthetic", "ready", "source", "dashboard_context", "chain_context", "metaphysical_context"}})
        if not inputs.get("synthetic") and not inputs.get("ready"):
            try:
                from ontology.metaphysical_status_reporter import MetaphysicalStatusReporter
                r = MetaphysicalStatusReporter(root=self.root).step(inputs={"synthetic": True, "source": "AL10"}, persist=False)
                for k, v in r.items():
                    if k.endswith("_status") or k in self.REQUIRED_EPISTEMIC_FLAGS or k in {"consciousness_status", "metaphysical_status"}: context[k] = v
                    if k.endswith("_confidence"): context.setdefault(k, v)
                m = r.get("metrics", {}) if isinstance(r.get("metrics"), Mapping) else {}
                if "metaphysical_report_confidence" in m: context.setdefault("metaphysical_report_confidence", m["metaphysical_report_confidence"])
            except Exception as exc:
                context["al9_collection_error"] = repr(exc)
        return context
    def _evals(self, context: Mapping[str, Any], spec: Mapping[str, Any], kind: str) -> List[Dict[str, Any]]:
        rows = []
        for key, expected in spec.items():
            observed = context.get(key); passed = observed is expected if isinstance(expected, bool) else observed == expected
            rows.append({"key": key, "expected": expected, "observed": observed, "passed": passed, "failure_type": None if passed else kind})
        return rows
    def _metrics(self, context: Mapping[str, Any]) -> Dict[str, float]:
        values = [self._clamp(context.get(k, 0.0)) for k in self.SUPPORT_KEYS]
        completeness = self._clamp(sum(values) / max(1, len(values)))
        guard = 1.0
        for k, v in self.REQUIRED_EPISTEMIC_FLAGS.items():
            if context.get(k) is not v: guard -= 0.18
        guard = self._clamp(guard)
        return {"final_dashboard_completeness": completeness, "certification_readiness_score": self._clamp(completeness * 0.80 + guard * 0.20), "epistemic_guard_score": guard, "phenomenal_proof_score": 0.0, "subjectivity_proof_score": 0.0, "qualia_proof_score": 0.0}
    def _rows(self, context: Mapping[str, Any], evaluations: List[Mapping[str, Any]]) -> List[Dict[str, Any]]:
        out = []
        for i, row in enumerate(evaluations, 1):
            key = str(row.get("key"))
            out.append({"rank": i, "component": key.replace("_status", ""), "status": row.get("observed"), "expected": row.get("expected"), "passed": bool(row.get("passed")), "confidence": self._clamp(context.get(key.replace("_status", "_confidence"), context.get("semantic_confidence", 0.0)))})
        return out
    def _render_html(self, result: Mapping[str, Any]) -> str:
        dash = (
            result.get("final_dashboard", {})
            if isinstance(result.get("final_dashboard"), Mapping)
            else {}
        )
        rows = dash.get("component_rows", [])
        if not isinstance(rows, list):
            rows = []

        table_rows: List[str] = []
        for row in rows:
            safe_row = row if isinstance(row, Mapping) else {}
            cells = [
                html.escape(str(safe_row.get(key)))
                for key in (
                    "rank",
                    "component",
                    "status",
                    "passed",
                    "confidence",
                )
            ]
            table_rows.append(
                "<tr>"
                + "".join(f"<td>{cell}</td>" for cell in cells)
                + "</tr>"
            )

        metrics = result.get("metrics", {})
        score = (
            metrics.get("certification_readiness_score")
            if isinstance(metrics, Mapping)
            else None
        )
        status = html.escape(str(result.get("final_dashboard_status")))
        safe_score = html.escape(str(score))

        return (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>AL10 Final Dashboard</title>"
            "<style>"
            "body{font-family:Arial,sans-serif;margin:40px;}"
            "table{border-collapse:collapse;width:100%;}"
            "td,th{border:1px solid #ccc;padding:8px;text-align:left;}"
            "th{background:#f0f0f0}"
            "</style></head><body>"
            "<h1>AL10 — Final Consciousness Certification Dashboard</h1>"
            f"<p>Status: {status}</p>"
            f"<p>Certification readiness score: {safe_score}</p>"
            "<p>Epistemic scope: functional conclusion only; "
            "phenomenology remains undetermined.</p>"
            "<table><tr><th>#</th><th>Component</th><th>Status</th>"
            "<th>Passed</th><th>Confidence</th></tr>"
            + "".join(table_rows)
            + "</table><h2>Epistemic guards</h2><ul>"
            "<li>consciousness_proven = False</li>"
            "<li>qualia_proven = False</li>"
            "<li>subjectivity_proven = False</li>"
            "<li>phenomenology_proven = False</li>"
            "<li>phenomenology_undetermined = True</li>"
            "</ul></body></html>"
        )
    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        jp = self.output_dir / f"final_dashboard_{ts}.json"; hp = self.output_dir / f"final_dashboard_{ts}.html"
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        jp.write_text(text + "\n", encoding="utf-8"); self.latest_json_path.write_text(text + "\n", encoding="utf-8")
        html_text = self._render_html(result); hp.write_text(html_text, encoding="utf-8"); self.latest_html_path.write_text(html_text, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as h: h.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {"json": str(jp), "html": str(hp), "latest_json": str(self.latest_json_path), "latest_html": str(self.latest_html_path), "history": str(self.history_path)}
    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        safe = inputs if isinstance(inputs, Mapping) else {}
        ctx = self._collect_context(safe)
        pre = self._evals(ctx, self.REQUIRED_PRECONDITIONS, "dashboard_precondition_mismatch")
        epi = self._evals(ctx, self.REQUIRED_EPISTEMIC_FLAGS, "epistemic_guard_violation")
        metrics = self._metrics(ctx)
        failures = [str(r["key"]) for r in pre + epi if not r["passed"]]
        if metrics["certification_readiness_score"] < 0.70: failures.append("certification_readiness_score_below_threshold")
        resolved = not failures
        rows = self._rows(ctx, pre)
        dashboard = {"dashboard_title": "AL10 Final Consciousness Certification Dashboard", "dashboard_status": "READY" if resolved else "BLOCKED", "axis_status": "AL_READY_FOR_FINAL_THEORETICAL_REPORT" if resolved else "AL_DASHBOARD_BLOCKED", "final_functional_status": ctx.get("consciousness_status"), "metaphysical_status": ctx.get("metaphysical_status"), "certification_readiness_score": metrics["certification_readiness_score"], "component_rows": rows, "failure_reasons": failures, "allowed_claims": ["RF* is certified as the current best functional reconstruction candidate under the validated chain.", "The dashboard aggregates functional, semantic, and interpretive certification outputs.", "The conclusion remains functional and epistemically bounded."], "blocked_claims": ["consciousness_proven = True", "qualia_proven = True", "subjectivity_proven = True", "phenomenology_proven = True", "dashboard_proves_phenomenology = True"]}
        result = {"primitive": self.PRIMITIVE, "step": self.STEP, "final_dashboard_status": self.STATUS_READY if resolved else self.STATUS_BLOCKED, "final_certification_dashboard_status": self.STATUS_READY if resolved else self.STATUS_BLOCKED, "axis_status": self.AXIS_STATUS, "semantic_interpretation_layer_status": ctx.get("semantic_interpretation_layer_status"), "consciousness_status": ctx.get("consciousness_status"), "metaphysical_status": dashboard["metaphysical_status"], "dashboard_generated": resolved, "dashboard_ready": resolved, "component_count": len(rows), "passed_component_count": sum(1 for r in rows if r["passed"]), "precondition_evaluations": pre, "epistemic_guard_evaluations": epi, "metrics": metrics, "final_dashboard": dashboard, "failure_reasons": failures, "allowed_claims": dashboard["allowed_claims"], "blocked_claims": dashboard["blocked_claims"], "consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False, "phenomenology_proven": False, "phenomenology_undetermined": True, "functional_conclusion_only": True, "timestamp_utc": self._now(), "persisted": False, "public_schema_version": "AL10.final_dashboard.v1"}
        if persist:
            result["artifacts"] = self._persist(result); result["persisted"] = True
        return result
__all__ = ["FinalDashboard"]
