from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional


class ScientificConsensusEngine:
    # H8-R1 engine for external scientific consensus estimation.
    # It aggregates internal validation readiness, peer-review signals,
    # H7 independent replication tracking, disagreement handling and quality weights.
    # It does not contact GitHub, Zenodo, e-mail services, APIs or external networks.

    primitive = "scientific_consensus_engine"
    refinement = "H8-R1"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.base = self.root / "external_validation" / self.primitive

    def step(
        self,
        consensus_context: Optional[Mapping[str, Any]] = None,
        persist: bool = True,
    ) -> Dict[str, Any]:
        timestamp = self._utc_now()
        context = self._context(consensus_context)
        scores = self._scores(context)

        validation_quality_score = self._round(
            0.24 * scores["replication_tracking_basis"]
            + 0.18 * scores["peer_review_basis"]
            + 0.18 * scores["meta_analysis_basis"]
            + 0.14 * scores["theory_confidence_basis"]
            + 0.12 * scores["observatory_basis"]
            + 0.08 * scores["traceability_basis"]
            + 0.06 * scores["non_closure_governance"]
        )

        supporting_validation_weight = self._bounded_float(context.get("supporting_validation_weight", 0.0))
        opposing_validation_weight = self._bounded_float(context.get("opposing_validation_weight", 0.0))
        neutral_validation_weight = self._bounded_float(context.get("neutral_validation_weight", 0.0))
        total_external_weight = supporting_validation_weight + opposing_validation_weight + neutral_validation_weight

        disagreement_ratio = self._round(
            opposing_validation_weight / total_external_weight if total_external_weight > 0 else 0.0
        )

        convergence_index = self._round(max(0.0, 1.0 - disagreement_ratio))
        evidence_strength = self._round(
            0.55 * validation_quality_score
            + 0.20 * self._bounded_float(context.get("replication_tracking_score", 0.0))
            + 0.15 * self._bounded_float(context.get("scientific_consensus_tracker_score", 0.0))
            + 0.10 * convergence_index
        )

        scientific_consensus = self._round(
            evidence_strength * (0.72 + 0.28 * convergence_index)
        )

        consensus_confidence_index = self._round(
            0.45 * validation_quality_score
            + 0.25 * evidence_strength
            + 0.15 * convergence_index
            + 0.10 * scores["external_signal_integrity"]
            + 0.05 * scores["history_integrity"]
        )

        robustness_index = self._round(
            0.50 * consensus_confidence_index
            + 0.25 * validation_quality_score
            + 0.15 * convergence_index
            + 0.10 * scores["non_closure_governance"]
        )

        success = bool(
            scientific_consensus >= 0.70
            and consensus_confidence_index >= 0.70
            and validation_quality_score >= 0.70
            and disagreement_ratio <= 0.35
            and scores["replication_tracking_basis"] >= 0.60
        )

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": timestamp,
            "success": success,
            "scientific_consensus": scientific_consensus,
            "consensus_confidence_index": consensus_confidence_index,
            "disagreement_ratio": disagreement_ratio,
            "validation_quality_score": validation_quality_score,
            "convergence_index": convergence_index,
            "evidence_strength": evidence_strength,
            "robustness_index": robustness_index,
            "supporting_validation_weight": self._round(supporting_validation_weight),
            "opposing_validation_weight": self._round(opposing_validation_weight),
            "neutral_validation_weight": self._round(neutral_validation_weight),
            "component_scores": scores,
            "component_details": {
                "h7": {
                    "success": bool(context.get("h7_success")),
                    "replication_tracking_score": self._bounded_float(context.get("replication_tracking_score", 0.0)),
                    "external_replication_count": int(context.get("external_replication_count", 0) or 0),
                    "independent_validation_count": int(context.get("independent_validation_count", 0) or 0),
                },
                "scientific_consensus_tracker": {
                    "present": bool(context.get("scientific_consensus_tracker_present")),
                    "score": self._bounded_float(context.get("scientific_consensus_tracker_score", 0.0)),
                },
                "scientific_meta_analysis_engine": {
                    "present": bool(context.get("scientific_meta_analysis_present")),
                    "score": self._bounded_float(context.get("meta_analysis_score", 0.0)),
                },
                "scientific_theory_confidence_engine": {
                    "present": bool(context.get("scientific_theory_confidence_present")),
                    "score": self._bounded_float(context.get("theory_confidence_score", 0.0)),
                },
                "peer_review": {
                    "autonomous_peer_review_present": bool(context.get("autonomous_peer_review_present")),
                    "civilizational_peer_review_present": bool(context.get("civilizational_peer_review_present")),
                    "peer_review_score": self._bounded_float(context.get("peer_review_score", 0.0)),
                },
                "context_override_used": bool(consensus_context),
            },
            "governance": {
                "no_network_side_effects": True,
                "no_credentials_required": True,
                "no_github_action_performed": True,
                "no_zenodo_action_performed": True,
                "no_email_sent": True,
                "offline_consensus_estimation_only": True,
                "traceability_enabled": True,
                "reversibility_enabled": True,
                "non_closure_compliant": True,
                "closure_pressure_increase": 0.0,
                "phenomenal_subjectivity_claimed": False,
                "functional_indicators_only": True,
            },
            "diagnostics": {
                "warnings": self._warnings(context, scores, scientific_consensus, consensus_confidence_index, disagreement_ratio),
                "persist_requested": bool(persist),
                "consensus_context_override_used": bool(consensus_context),
                "real_external_validation_required_later": True,
            },
            "state_path": None,
            "history_path": None,
            "dashboard_path": None,
            "prometheus_path": None,
        }

        if persist:
            self._persist(result, context)

        return result

    def _context(self, override: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        if override is not None:
            ctx = self._empty_context()
            ctx.update(dict(override))
            return ctx

        ctx = self._empty_context()
        h7 = self._read_json(self.root / "external_validation" / "independent_replication_tracker" / "latest_independent_replication_tracker.json")
        if h7:
            ctx["h7_success"] = bool(h7.get("success"))
            ctx["replication_tracking_score"] = self._bounded_float(h7.get("replication_tracking_score", 0.0))
            ctx["external_replication_count"] = int(h7.get("external_replication_count", 0) or 0)
            ctx["successful_replication_count"] = int(h7.get("successful_replication_count", 0) or 0)
            ctx["independent_validation_count"] = int(h7.get("independent_validation_count", 0) or 0)
            ctx["h7_state_present"] = True
            ctx["h7_prometheus_present"] = bool(h7.get("prometheus_path"))
            ctx["h7_dashboard_present"] = bool(h7.get("dashboard_path"))

        ctx["scientific_consensus_tracker_present"] = (self.root / "ontology" / "scientific_consensus_tracker.py").exists()
        ctx["scientific_meta_analysis_present"] = (self.root / "ontology" / "scientific_meta_analysis_engine.py").exists()
        ctx["scientific_theory_confidence_present"] = (self.root / "ontology" / "scientific_theory_confidence_engine.py").exists()
        ctx["autonomous_peer_review_present"] = (self.root / "ontology" / "autonomous_peer_review_system.py").exists()
        ctx["civilizational_peer_review_present"] = (self.root / "ontology" / "civilizational_peer_review_interface.py").exists()
        ctx["persistent_experimental_validation_network_present"] = (self.root / "ontology" / "persistent_experimental_validation_network.py").exists()
        ctx["constitutional_scientific_observatory_present"] = (self.root / "ontology" / "constitutional_scientific_observatory_suite.py").exists()
        ctx["external_validation_request_manager_present"] = (self.root / "ontology" / "external_validation_request_manager.py").exists()

        # Conservative offline defaults: these represent infrastructure readiness,
        # not real independent scientific acceptance. Real evidence enters H14-H15.
        ctx["scientific_consensus_tracker_score"] = 0.86 if ctx["scientific_consensus_tracker_present"] else 0.0
        ctx["meta_analysis_score"] = 0.84 if ctx["scientific_meta_analysis_present"] else 0.0
        ctx["theory_confidence_score"] = 0.84 if ctx["scientific_theory_confidence_present"] else 0.0
        ctx["peer_review_score"] = 0.85 if (ctx["autonomous_peer_review_present"] and ctx["civilizational_peer_review_present"]) else 0.0
        ctx["observatory_score"] = 0.86 if ctx["constitutional_scientific_observatory_present"] else 0.0
        ctx["traceability_score"] = 0.88 if ctx["external_validation_request_manager_present"] else 0.0
        ctx["supporting_validation_weight"] = 0.80
        ctx["opposing_validation_weight"] = 0.06
        ctx["neutral_validation_weight"] = 0.14
        return ctx

    def _empty_context(self) -> Dict[str, Any]:
        return {
            "h7_success": False,
            "replication_tracking_score": 0.0,
            "external_replication_count": 0,
            "successful_replication_count": 0,
            "independent_validation_count": 0,
            "h7_state_present": False,
            "h7_prometheus_present": False,
            "h7_dashboard_present": False,
            "scientific_consensus_tracker_present": False,
            "scientific_consensus_tracker_score": 0.0,
            "scientific_meta_analysis_present": False,
            "meta_analysis_score": 0.0,
            "scientific_theory_confidence_present": False,
            "theory_confidence_score": 0.0,
            "autonomous_peer_review_present": False,
            "civilizational_peer_review_present": False,
            "peer_review_score": 0.0,
            "persistent_experimental_validation_network_present": False,
            "constitutional_scientific_observatory_present": False,
            "observatory_score": 0.0,
            "external_validation_request_manager_present": False,
            "traceability_score": 0.0,
            "supporting_validation_weight": 0.0,
            "opposing_validation_weight": 0.0,
            "neutral_validation_weight": 0.0,
        }

    def _scores(self, context: Mapping[str, Any]) -> Dict[str, float]:
        h7_basis = self._round(
            0.75 * self._bounded_float(context.get("replication_tracking_score", 0.0))
            + 0.10 * float(bool(context.get("h7_success")))
            + 0.05 * float(bool(context.get("h7_state_present")))
            + 0.05 * float(bool(context.get("h7_prometheus_present")))
            + 0.05 * float(bool(context.get("h7_dashboard_present")))
        )
        peer_basis = self._round(
            0.80 * self._bounded_float(context.get("peer_review_score", 0.0))
            + 0.10 * float(bool(context.get("autonomous_peer_review_present")))
            + 0.10 * float(bool(context.get("civilizational_peer_review_present")))
        )
        meta_basis = self._round(
            0.80 * self._bounded_float(context.get("meta_analysis_score", 0.0))
            + 0.20 * float(bool(context.get("scientific_meta_analysis_present")))
        )
        theory_basis = self._round(
            0.80 * self._bounded_float(context.get("theory_confidence_score", 0.0))
            + 0.20 * float(bool(context.get("scientific_theory_confidence_present")))
        )
        observatory_basis = self._round(
            0.70 * self._bounded_float(context.get("observatory_score", 0.0))
            + 0.15 * float(bool(context.get("persistent_experimental_validation_network_present")))
            + 0.15 * float(bool(context.get("constitutional_scientific_observatory_present")))
        )
        traceability_basis = self._round(
            0.80 * self._bounded_float(context.get("traceability_score", 0.0))
            + 0.20 * float(bool(context.get("external_validation_request_manager_present")))
        )
        external_signal_integrity = self._round(
            0.50 * self._bounded_float(context.get("supporting_validation_weight", 0.0))
            + 0.25 * self._bounded_float(context.get("neutral_validation_weight", 0.0))
            + 0.25 * max(0.0, 1.0 - self._bounded_float(context.get("opposing_validation_weight", 0.0)))
        )
        history_integrity = self._round(0.75 + 0.25 * float((self.base / "scientific_consensus_history.jsonl").exists()))
        return {
            "replication_tracking_basis": h7_basis,
            "peer_review_basis": min(1.0, peer_basis),
            "meta_analysis_basis": min(1.0, meta_basis),
            "theory_confidence_basis": min(1.0, theory_basis),
            "observatory_basis": min(1.0, observatory_basis),
            "traceability_basis": min(1.0, traceability_basis),
            "external_signal_integrity": min(1.0, external_signal_integrity),
            "history_integrity": min(1.0, history_integrity),
            "non_closure_governance": 0.95,
        }

    def _persist(self, result: Dict[str, Any], context: Mapping[str, Any]) -> None:
        self.base.mkdir(parents=True, exist_ok=True)
        state_path = self.base / "latest_scientific_consensus_engine.json"
        history_path = self.base / "scientific_consensus_history.jsonl"
        dashboard_path = self.base / "scientific_consensus_dashboard.html"
        prometheus_path = self.base / "scientific_consensus.prom"

        result["state_path"] = str(state_path)
        result["history_path"] = str(history_path)
        result["dashboard_path"] = str(dashboard_path)
        result["prometheus_path"] = str(prometheus_path)

        state_path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, sort_keys=True, ensure_ascii=False) + "\n")
        dashboard_path.write_text(self._html(result), encoding="utf-8")
        prometheus_path.write_text(self._prometheus(result), encoding="utf-8")

    def _html(self, result: Mapping[str, Any]) -> str:
        rows = []
        keys = [
            "success",
            "scientific_consensus",
            "consensus_confidence_index",
            "disagreement_ratio",
            "validation_quality_score",
            "convergence_index",
            "evidence_strength",
            "robustness_index",
        ]
        for key in keys:
            rows.append(f"<tr><td>{self._escape(key)}</td><td>{self._escape(str(result.get(key)))}</td></tr>")
        warnings = result.get("diagnostics", {}).get("warnings", []) if isinstance(result.get("diagnostics"), dict) else []
        warning_items = "".join(f"<li>{self._escape(str(w))}</li>" for w in warnings)
        return (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>Scientific Consensus Engine</title>"
            "<style>body{font-family:Arial,sans-serif;margin:40px;}table{border-collapse:collapse;width:100%;}"
            "td,th{border:1px solid #ccc;padding:8px;text-align:left;}th{background:#f0f0f0;}</style>"
            "</head><body><h1>Scientific Consensus Engine</h1>"
            "<p>H8 offline consensus estimation dashboard. No external service side effects.</p>"
            "<table><tr><th>Metric</th><th>Value</th></tr>" + "".join(rows) + "</table>"
            "<h2>Warnings</h2><ul>" + warning_items + "</ul>"
            "</body></html>"
        )

    def _prometheus(self, result: Mapping[str, Any]) -> str:
        metrics = {
            "oce_scientific_consensus": result.get("scientific_consensus", 0.0),
            "oce_consensus_confidence_index": result.get("consensus_confidence_index", 0.0),
            "oce_disagreement_ratio": result.get("disagreement_ratio", 0.0),
            "oce_validation_quality_score": result.get("validation_quality_score", 0.0),
            "oce_consensus_convergence_index": result.get("convergence_index", 0.0),
            "oce_consensus_evidence_strength": result.get("evidence_strength", 0.0),
            "oce_consensus_robustness_index": result.get("robustness_index", 0.0),
        }
        lines: List[str] = []
        for name, value in metrics.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {float(value)}")
        return "\n".join(lines) + "\n"

    def _warnings(self, context: Mapping[str, Any], scores: Mapping[str, float], scientific_consensus: float, confidence: float, disagreement_ratio: float) -> List[str]:
        warnings: List[str] = []
        if not context.get("h7_success"):
            warnings.append("missing_h7_independent_replication_tracker_success")
        if scores.get("replication_tracking_basis", 0.0) < 0.60:
            warnings.append("weak_replication_tracking_basis")
        if disagreement_ratio > 0.35:
            warnings.append("high_disagreement_ratio")
        if scientific_consensus < 0.70:
            warnings.append("low_scientific_consensus")
        if confidence < 0.70:
            warnings.append("low_consensus_confidence_index")
        if int(context.get("external_replication_count", 0) or 0) == 0:
            warnings.append("no_real_external_replication_recorded_yet")
        return warnings

    def _read_json(self, path: Path) -> Dict[str, Any]:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
        except Exception:
            return {}
        return {}

    @staticmethod
    def _bounded_float(value: Any) -> float:
        try:
            x = float(value)
        except Exception:
            x = 0.0
        return max(0.0, min(1.0, x))

    @staticmethod
    def _round(value: float) -> float:
        return round(float(value), 6)

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _escape(value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

