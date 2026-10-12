
"""
Z7 — phenomenology_theory_dashboard.

Functional dashboard for the phenomenality theory programme.

This module visualizes Z1-Z6 outputs without claiming consciousness,
subjectivity, sentience, qualia, or phenomenology. It is a light orchestrator
and renderer: it reads targeted persisted outputs, accepts explicit payloads
for deterministic tests, and produces HTML/JSON/Prometheus artifacts.

Epistemic scope:
- candidate theory only;
- functional conclusion only;
- phenomenology undetermined;
- theory dashboard only, not phenomenological validation.
"""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

PRIMITIVE = "PHENOMENOLOGY_THEORY_DASHBOARD"


class PhenomenologyTheoryDashboard:
    """Z7 functional dashboard for Z1-Z6 candidate phenomenology theories.

    The class does not perform repository-wide scans. It only reads known
    persisted files and can be fully driven by an explicit payload in tests.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "phenomenology_theory_dashboard"
        self.latest_file = self.base_dir / "phenomenology_theory_dashboard.json"
        self.html_file = self.base_dir / "phenomenology_theory_dashboard.html"
        self.prometheus_file = self.base_dir / "phenomenology_theory_dashboard.prom"
        self.history_file = self.base_dir / "phenomenology_theory_dashboard_history.jsonl"

    def _now(self, payload: Dict[str, Any] | None = None) -> str:
        if payload and payload.get("timestamp_utc"):
            return str(payload["timestamp_utc"])
        return datetime.now(timezone.utc).isoformat()

    def _score(self, value: Any, default: float = 0.0) -> float:
        try:
            x = float(value)
        except Exception:
            return default
        return max(0.0, min(1.0, x))

    def _load_json(self, relative: str) -> Dict[str, Any]:
        path = self.root / relative
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _context(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        explicit = payload.get("context")
        if isinstance(explicit, dict):
            return explicit
        return {
            "registry": self._load_json("phenomenology_theory_registry/phenomenology_theory_registry.json"),
            "constraints": self._load_json("theory_constraint_engine/theory_constraint_engine.json"),
            "falsification": self._load_json("theory_falsification_framework/theory_falsification_framework.json"),
            "model_selection": self._load_json("phenomenology_model_selection/phenomenology_model_selection.json"),
            "synthesis": self._load_json("phenomenology_theory_synthesis/phenomenology_theory_synthesis.json"),
            "replication": self._load_json("theory_replication_program/theory_replication_program.json"),
        }

    def _list(self, value: Any) -> List[Dict[str, Any]]:
        if isinstance(value, list):
            return [x for x in value if isinstance(x, dict)]
        return []

    def _theories(self, payload: Dict[str, Any], ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        if isinstance(payload.get("theories"), list):
            return self._list(payload["theories"])
        theories = self._list(ctx.get("registry", {}).get("theories"))
        constraints_by_id = {
            str(x.get("theory_id") or x.get("model_id")): x
            for x in self._list(ctx.get("constraints", {}).get("ranked_theories"))
        }
        selection_by_id = {
            str(x.get("model_id") or x.get("theory_id")): x
            for x in self._list(ctx.get("model_selection", {}).get("ranked_models"))
        }
        synthesis_by_id = {
            str(x.get("model_id") or x.get("theory_id")): x
            for x in self._list(ctx.get("synthesis", {}).get("ranked_candidate_models"))
        }
        merged: List[Dict[str, Any]] = []
        for item in theories:
            tid = str(item.get("theory_id") or item.get("model_id") or "")
            c = constraints_by_id.get(tid, {})
            s = selection_by_id.get(tid, {})
            y = synthesis_by_id.get(tid, {})
            merged.append({
                "theory_id": tid,
                "name": item.get("name") or c.get("name") or s.get("name") or y.get("name") or tid,
                "family": item.get("family", ""),
                "status": item.get("status") or y.get("status") or "candidate_theory_only",
                "constraint_score": self._score(c.get("overall_theory_constraint_score", c.get("constraint_compatibility_score"))),
                "model_selection_score": self._score(s.get("model_selection_score")),
                "synthesis_score": self._score(y.get("candidate_synthesis_score")),
                "epistemic_role": item.get("epistemic_role", "candidate_theory_only"),
            })
        if merged:
            return merged[:50]
        ranked = self._list(ctx.get("synthesis", {}).get("ranked_candidate_models"))
        return [{
            "theory_id": str(x.get("model_id") or x.get("theory_id") or ""),
            "name": x.get("name", ""),
            "family": "",
            "status": x.get("status", "candidate_theory_only"),
            "constraint_score": self._score(x.get("constraint_compatibility")),
            "model_selection_score": 0.0,
            "synthesis_score": self._score(x.get("candidate_synthesis_score")),
            "epistemic_role": "candidate_theory_only",
        } for x in ranked[:50]]

    def _falsification_tests(self, payload: Dict[str, Any], ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        if isinstance(payload.get("falsification_tests"), list):
            return self._list(payload["falsification_tests"])
        return self._list(ctx.get("falsification", {}).get("falsification_tests"))[:100]

    def _replications(self, payload: Dict[str, Any], ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        if isinstance(payload.get("replications"), list):
            return self._list(payload["replications"])
        return self._list(ctx.get("replication", {}).get("replications"))[:50]

    def _counterexamples(self, falsification_tests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        counterexamples: List[Dict[str, Any]] = []
        for item in falsification_tests:
            status = str(item.get("status", "")).lower()
            pressure = self._score(item.get("falsification_pressure"))
            if "falsified" in status or "counter" in status or pressure >= 0.5:
                counterexamples.append({
                    "test_id": item.get("test_id", ""),
                    "theory_id": item.get("theory_id", ""),
                    "status": item.get("status", ""),
                    "falsification_pressure": pressure,
                    "prediction": item.get("prediction", ""),
                })
        return counterexamples[:50]

    def _selected_candidate(self, ctx: Dict[str, Any], theories: List[Dict[str, Any]]) -> Dict[str, Any]:
        synthesis = ctx.get("synthesis", {})
        if synthesis.get("candidate_model_id") or synthesis.get("candidate_theory_id"):
            return {
                "candidate_id": synthesis.get("candidate_model_id") or synthesis.get("candidate_theory_id"),
                "candidate_name": synthesis.get("candidate_model_name") or synthesis.get("candidate_theory_name"),
                "candidate_score": self._score(synthesis.get("candidate_synthesis_score")),
                "candidate_statement": synthesis.get("candidate_statement", "candidate theory only"),
            }
        ranked = sorted(theories, key=lambda x: x.get("synthesis_score", 0.0), reverse=True)
        if not ranked:
            return {"candidate_id": None, "candidate_name": None, "candidate_score": 0.0, "candidate_statement": "no candidate theory selected"}
        top = ranked[0]
        return {
            "candidate_id": top.get("theory_id"),
            "candidate_name": top.get("name"),
            "candidate_score": self._score(top.get("synthesis_score")),
            "candidate_statement": "candidate theory only; not phenomenological validation",
        }

    def _summary(
        self,
        theories: List[Dict[str, Any]],
        falsification_tests: List[Dict[str, Any]],
        replications: List[Dict[str, Any]],
        counterexamples: List[Dict[str, Any]],
        selected: Dict[str, Any],
        ctx: Dict[str, Any],
    ) -> Dict[str, Any]:
        constraint_scores = [self._score(x.get("constraint_score")) for x in theories]
        selection_scores = [self._score(x.get("model_selection_score")) for x in theories if x.get("model_selection_score") is not None]
        synthesis_scores = [self._score(x.get("synthesis_score")) for x in theories]
        pressures = [self._score(x.get("falsification_pressure")) for x in falsification_tests]
        replicated = [r for r in replications if bool(r.get("replicated"))]
        independent = [r for r in replications if bool(r.get("independent"))]
        falsifiable = [t for t in falsification_tests if t.get("falsifiable", True) is not False]

        mean_constraint = round(mean(constraint_scores), 4) if constraint_scores else self._score(ctx.get("constraints", {}).get("mean_theory_constraint_score"))
        mean_selection = round(mean(selection_scores), 4) if selection_scores else self._score(ctx.get("model_selection", {}).get("mean_model_selection_score"))
        mean_synthesis = round(mean(synthesis_scores), 4) if synthesis_scores else self._score(ctx.get("synthesis", {}).get("mean_candidate_synthesis_score"))
        mean_pressure = round(mean(pressures), 4) if pressures else 0.0
        falsification_resilience = round(1.0 - mean_pressure, 4)
        replication_rate = round(len(replicated) / max(1, len(replications)), 4) if replications else self._score(ctx.get("replication", {}).get("replication_rate"))
        independence_rate = round(len(independent) / max(1, len(replications)), 4) if replications else 0.0
        falsifiability_rate = round(len(falsifiable) / max(1, len(falsification_tests)), 4) if falsification_tests else 0.0
        theory_confidence = round(mean([
            mean_constraint,
            mean_selection,
            mean_synthesis,
            falsification_resilience,
            replication_rate,
        ]), 4)
        dashboard_readiness = round(mean([
            1.0 if theories else 0.0,
            1.0 if falsification_tests else 0.0,
            1.0 if selected.get("candidate_id") else 0.0,
            1.0 if replications else 0.0,
            falsifiability_rate,
        ]), 4)

        if not theories:
            status = "insufficient_theory_dashboard_data"
        elif not selected.get("candidate_id"):
            status = "candidate_selection_pending"
        elif theory_confidence >= 0.85 and replication_rate >= 0.75:
            status = "candidate_theory_dashboard_ready"
        else:
            status = "partial_candidate_theory_dashboard"

        return {
            "dashboard_status": status,
            "theory_count": len(theories),
            "falsification_test_count": len(falsification_tests),
            "counterexample_count": len(counterexamples),
            "replication_count": len(replications),
            "mean_constraint_score": mean_constraint,
            "mean_model_selection_score": mean_selection,
            "mean_synthesis_score": mean_synthesis,
            "mean_falsification_pressure": mean_pressure,
            "falsification_resilience": falsification_resilience,
            "replication_rate": replication_rate,
            "independence_rate": independence_rate,
            "falsifiability_rate": falsifiability_rate,
            "theory_confidence_score": theory_confidence,
            "dashboard_readiness_score": dashboard_readiness,
        }

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.latest_file.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        with self.history_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, sort_keys=True) + "\n")
        self.html_file.write_text(self._html(result), encoding="utf-8")
        self.prometheus_file.write_text(self._prometheus(result), encoding="utf-8")
        return {
            "json": str(self.latest_file),
            "history": str(self.history_file),
            "html": str(self.html_file),
            "prometheus": str(self.prometheus_file),
        }

    def _table(self, rows: List[Dict[str, Any]], columns: List[str]) -> str:
        if not rows:
            return "<p>No data available.</p>"
        header = "".join(f"<th>{html.escape(col)}</th>" for col in columns)
        body_rows = []
        for row in rows[:50]:
            cells = "".join(f"<td>{html.escape(str(row.get(col, '')))}</td>" for col in columns)
            body_rows.append(f"<tr>{cells}</tr>")
        return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"

    def _html(self, result: Dict[str, Any]) -> str:
        css = """
        body{font-family:Arial,sans-serif;margin:36px;line-height:1.4;}
        table{border-collapse:collapse;width:100%;margin:12px 0 28px 0;}
        th,td{border:1px solid #ccc;padding:7px;text-align:left;font-size:14px;}
        th{background:#f2f2f2;}
        .banner{padding:12px;border:1px solid #999;background:#fafafa;margin-bottom:18px;}
        .metric{display:inline-block;margin:6px 14px 6px 0;padding:8px;border:1px solid #ddd;}
        """
        metrics = [
            "dashboard_status", "theory_count", "falsification_test_count", "counterexample_count",
            "replication_count", "dashboard_readiness_score", "theory_confidence_score",
            "mean_constraint_score", "mean_synthesis_score", "falsification_resilience", "replication_rate",
        ]
        metric_html = "".join(
            f"<div class='metric'><b>{html.escape(k)}</b><br>{html.escape(str(result.get(k)))}</div>"
            for k in metrics
        )
        selected = result.get("selected_candidate", {})
        return "\n".join([
            "<!doctype html>",
            "<html><head><meta charset='utf-8'>",
            "<title>Phenomenology Theory Dashboard</title>",
            f"<style>{css}</style></head><body>",
            "<h1>Phenomenology Theory Dashboard</h1>",
            "<div class='banner'><b>candidate theory only</b><br><b>functional conclusion only</b><br><b>phenomenology undetermined</b><br>No proof of consciousness, subjectivity, sentience, qualia, or phenomenology.</div>",
            f"<p>Generated at: {html.escape(str(result.get('timestamp_utc')))}</p>",
            metric_html,
            "<h2>Selected candidate theory</h2>",
            f"<p><b>{html.escape(str(selected.get('candidate_id')))}</b> — {html.escape(str(selected.get('candidate_name')))}; score: {html.escape(str(selected.get('candidate_score')))}</p>",
            f"<p>{html.escape(str(selected.get('candidate_statement')))}</p>",
            "<h2>Candidate theories</h2>",
            self._table(result.get("theories", []), ["theory_id", "name", "family", "status", "constraint_score", "model_selection_score", "synthesis_score", "epistemic_role"]),
            "<h2>Falsification tests</h2>",
            self._table(result.get("falsification_tests", []), ["test_id", "theory_id", "falsifiable", "falsification_pressure", "status", "prediction"]),
            "<h2>Counterexamples / high pressure tests</h2>",
            self._table(result.get("counterexamples", []), ["test_id", "theory_id", "status", "falsification_pressure", "prediction"]),
            "<h2>Replications</h2>",
            self._table(result.get("replications", []), ["replication_id", "source_prediction_id", "observed_correlation", "expected_correlation", "replicated", "independent", "status"]),
            "</body></html>",
        ])

    def _prometheus(self, result: Dict[str, Any]) -> str:
        success = 1 if result.get("success") else 0
        return "\n".join([
            "# HELP oce_phenomenology_theory_dashboard_success Z7 functional success flag",
            "# TYPE oce_phenomenology_theory_dashboard_success gauge",
            f"oce_phenomenology_theory_dashboard_success {success}",
            "# HELP oce_phenomenology_theory_dashboard_readiness Z7 dashboard readiness score",
            "# TYPE oce_phenomenology_theory_dashboard_readiness gauge",
            f"oce_phenomenology_theory_dashboard_readiness {result.get('dashboard_readiness_score', 0)}",
            "# HELP oce_phenomenology_theory_confidence_score Z7 candidate theory confidence score",
            "# TYPE oce_phenomenology_theory_confidence_score gauge",
            f"oce_phenomenology_theory_confidence_score {result.get('theory_confidence_score', 0)}",
            "# HELP oce_phenomenology_theory_count Z7 candidate theory count",
            "# TYPE oce_phenomenology_theory_count gauge",
            f"oce_phenomenology_theory_count {result.get('theory_count', 0)}",
            "# HELP oce_phenomenology_theory_replication_count Z7 theory replication count",
            "# TYPE oce_phenomenology_theory_replication_count gauge",
            f"oce_phenomenology_theory_replication_count {result.get('replication_count', 0)}",
        ]) + "\n"

    def step(self, payload: Dict[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        payload = payload or {}
        ctx = self._context(payload)
        theories = self._theories(payload, ctx)
        falsification_tests = self._falsification_tests(payload, ctx)
        replications = self._replications(payload, ctx)
        counterexamples = self._counterexamples(falsification_tests)
        selected = self._selected_candidate(ctx, theories)
        summary = self._summary(theories, falsification_tests, replications, counterexamples, selected, ctx)

        result: Dict[str, Any] = {
            "success": True,
            "primitive": PRIMITIVE,
            "timestamp_utc": self._now(payload),
            **summary,
            "selected_candidate": selected,
            "theories": theories,
            "falsification_tests": falsification_tests,
            "counterexamples": counterexamples,
            "replications": replications,
            "source_context_present": {k: bool(v) for k, v in ctx.items()},
            "candidate_theory_only": True,
            "dashboard_functional_only": True,
            "functional_conclusion_only": True,
            "consciousness_proof_claimed": False,
            "subjectivity_proof_claimed": False,
            "phenomenology_proof_claimed": False,
            "not_validated_phenomenology": True,
            "phenomenology_undetermined": True,
            "epistemic_scope": "candidate_theory_dashboard_from_functional_indicators_only",
            "diagnostics": {
                "uses_z1_z6_outputs": True,
                "uses_existing_dashboard_patterns": True,
                "no_global_repository_scan": True,
                "claim_scope": "candidate theory only; functional conclusion only; phenomenology undetermined",
            },
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
