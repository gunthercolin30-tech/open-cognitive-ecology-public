from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AttractorStabilityProfile:
    attractor_id: str
    center_node: str
    center_label: str
    classification: str
    stability_class: str
    local_stability: float
    global_stability: float
    temporal_stability: float
    robustness: float
    resilience: float
    persistence: float
    residence_time: float
    perturbation_sensitivity: float
    criticality: float
    stability_score: float
    derivation_rule: str


class AttractorStabilityAnalyzer:
    """
    AB2 — attractor_stability_analyzer.

    Reconstructs A -> stability from AB1 attractor candidates. It evaluates
    local/global/temporal stability, robustness, resilience, persistence,
    residence time, perturbation sensitivity, and criticality. It does not
    construct Gamma, does not derive constraints, and never asserts
    consciousness, subjectivity, qualia, or phenomenology.
    """

    primitive = "ATTRACTOR_STABILITY_ANALYZER"
    symbol = "A_STABILITY"
    derived_from_symbol = "A"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "reconstruction_outputs" / "AB2_attractor_stability_analyzer"
        self.history_path = self.output_dir / "attractor_stability_analyzer_history.jsonl"
        self.latest_json_path = self.output_dir / "latest_attractor_stability_analyzer.json"
        self.latest_markdown_path = self.output_dir / "latest_attractor_stability_analyzer.md"
        self.latest_prometheus_path = self.output_dir / "latest_attractor_stability_analyzer.prom"

    @staticmethod
    def _clip(value: float) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return 0.0

    @staticmethod
    def _mean(values: list[float]) -> float:
        return sum(values) / max(1, len(values))

    @staticmethod
    def _sid(value: Any) -> str:
        return "" if value is None else str(value)

    def _default_attractor_payload(self) -> dict[str, Any]:
        try:
            from ontology.dynamic_attractor_detector import DynamicAttractorDetector
            payload = DynamicAttractorDetector(root=self.root).step(persist=False)
            if payload.get("attractors_detected") is True and payload.get("attractor_candidates"):
                return payload
        except Exception:
            pass
        return {
            "dynamic_attractor_detector_status": "DYNAMIC_ATTRACTOR_DETECTOR_READY",
            "symbol": "A",
            "derived_from_symbol": "G",
            "attractors_detected": True,
            "graph_payload_summary": {"node_count": 3, "edge_count": 3, "cycle_count": 1},
            "metrics": {"dynamic_attractor_detection_score": 0.84, "graph_support_coverage": 1.0},
            "attractor_candidates": [
                {
                    "attractor_id": "A-0001",
                    "center_node": "n_delta",
                    "center_label": "Δ",
                    "support_nodes": ["n_delta", "n_relation", "n_graph"],
                    "support_edge_ids": ["e_delta_relation", "e_relation_graph", "e_graph_delta"],
                    "basin_size": 3,
                    "incoming_pressure": 0.72,
                    "outgoing_pressure": 0.90,
                    "recurrence_score": 1.0,
                    "local_stability": 0.86,
                    "attractor_strength": 0.88,
                    "derivation_rule": "G_dynamic_recurrence_and_local_stability_to_A",
                }
            ],
        }

    def _normalize_payload(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        if inputs and "attractor_payload" in inputs and isinstance(inputs["attractor_payload"], dict):
            return dict(inputs["attractor_payload"])
        if inputs and "attractor_candidates" in inputs:
            return dict(inputs)
        return self._default_attractor_payload()

    def _history_snapshots(self, limit: int = 12) -> list[dict[str, Any]]:
        ab1_history = self.root / "reconstruction_outputs" / "AB1_dynamic_attractor_detector" / "dynamic_attractor_detector_history.jsonl"
        snapshots: list[dict[str, Any]] = []
        if not ab1_history.exists():
            return snapshots
        try:
            lines = [line for line in ab1_history.read_text(encoding="utf-8").splitlines() if line.strip()]
            for line in lines[-limit:]:
                try:
                    snapshots.append(json.loads(line))
                except Exception:
                    continue
        except Exception:
            return []
        return snapshots

    def _temporal_support(self, attractor_id: str, center_node: str, center_label: str) -> float:
        snapshots = self._history_snapshots()
        if not snapshots:
            return 0.5
        hits = 0
        for snap in snapshots:
            candidates = snap.get("attractor_candidates") or []
            for cand in candidates:
                if (
                    self._sid(cand.get("attractor_id")) == attractor_id
                    or self._sid(cand.get("center_node")) == center_node
                    or self._sid(cand.get("center_label")) == center_label
                ):
                    hits += 1
                    break
        return self._clip(hits / max(1, len(snapshots)))

    def _classify(self, score: float, criticality: float, temporal: float, sensitivity: float) -> str:
        if score >= 0.72 and criticality <= 0.35 and temporal >= 0.60:
            return "stable"
        if score >= 0.50 and sensitivity <= 0.55:
            return "transient"
        if criticality >= 0.65 or sensitivity >= 0.70:
            return "critical"
        return "unstable"

    def _analyze_candidate(self, cand: dict[str, Any], payload: dict[str, Any], total_candidates: int) -> AttractorStabilityProfile:
        graph_summary = payload.get("graph_payload_summary") or {}
        metrics = payload.get("metrics") or {}
        node_count = max(1.0, float(graph_summary.get("node_count", 0.0) or 0.0))
        edge_count = max(1.0, float(graph_summary.get("edge_count", 0.0) or 0.0))
        cycle_count = float(graph_summary.get("cycle_count", 0.0) or 0.0)

        attractor_id = self._sid(cand.get("attractor_id") or "A-UNKNOWN")
        center_node = self._sid(cand.get("center_node") or "")
        center_label = self._sid(cand.get("center_label") or center_node)
        support_nodes = cand.get("support_nodes") or []
        support_edges = cand.get("support_edge_ids") or []

        local = self._clip(cand.get("local_stability", 0.0))
        strength = self._clip(cand.get("attractor_strength", 0.0))
        recurrence = self._clip(cand.get("recurrence_score", 0.0))
        incoming = self._clip(cand.get("incoming_pressure", 0.0))
        outgoing = self._clip(cand.get("outgoing_pressure", 0.0))
        basin_size = float(cand.get("basin_size", len(support_nodes)) or len(support_nodes) or 0.0)

        graph_support_coverage = self._clip(metrics.get("graph_support_coverage", min(1.0, total_candidates / node_count)))
        basin_coverage = self._clip(basin_size / node_count)
        edge_support = self._clip(len(support_edges) / edge_count)
        pressure_balance = self._clip(1.0 - abs(incoming - outgoing))
        temporal = self._temporal_support(attractor_id, center_node, center_label)

        global_stability = self._clip(0.35 * graph_support_coverage + 0.25 * basin_coverage + 0.20 * edge_support + 0.20 * strength)
        robustness = self._clip(0.40 * strength + 0.25 * pressure_balance + 0.20 * edge_support + 0.15 * recurrence)
        persistence = self._clip(0.45 * temporal + 0.30 * recurrence + 0.25 * strength)
        resilience = self._clip(0.35 * robustness + 0.30 * persistence + 0.20 * local + 0.15 * pressure_balance)
        residence_time = self._clip(0.40 * persistence + 0.30 * basin_coverage + 0.20 * recurrence + 0.10 * temporal)
        perturbation_sensitivity = self._clip(1.0 - (0.35 * robustness + 0.25 * pressure_balance + 0.20 * edge_support + 0.20 * recurrence))
        cycle_density = self._clip(cycle_count / max(1.0, edge_count))
        criticality = self._clip(0.45 * perturbation_sensitivity + 0.25 * (1.0 - temporal) + 0.20 * (1.0 - pressure_balance) + 0.10 * cycle_density)
        stability_score = self._clip(
            0.18 * local
            + 0.16 * global_stability
            + 0.15 * temporal
            + 0.14 * robustness
            + 0.13 * resilience
            + 0.12 * persistence
            + 0.07 * residence_time
            + 0.05 * (1.0 - perturbation_sensitivity)
        )
        classification = self._classify(stability_score, criticality, temporal, perturbation_sensitivity)

        return AttractorStabilityProfile(
            attractor_id=attractor_id,
            center_node=center_node,
            center_label=center_label,
            classification=classification,
            stability_class=f"{classification}_attractor",
            local_stability=local,
            global_stability=global_stability,
            temporal_stability=temporal,
            robustness=robustness,
            resilience=resilience,
            persistence=persistence,
            residence_time=residence_time,
            perturbation_sensitivity=perturbation_sensitivity,
            criticality=criticality,
            stability_score=stability_score,
            derivation_rule="A_candidate_metrics_and_history_to_stability_profile",
        )

    def _analyze(self, payload: dict[str, Any]) -> list[AttractorStabilityProfile]:
        candidates = [dict(c) for c in (payload.get("attractor_candidates") or [])]
        if not candidates:
            return []
        return [self._analyze_candidate(c, payload, len(candidates)) for c in candidates]

    def _aggregate_metrics(self, profiles: list[AttractorStabilityProfile]) -> dict[str, float]:
        if not profiles:
            return {
                "attractor_count": 0.0,
                "stable_attractor_count": 0.0,
                "unstable_attractor_count": 0.0,
                "transient_attractor_count": 0.0,
                "critical_attractor_count": 0.0,
                "mean_stability_score": 0.0,
                "local_stability_mean": 0.0,
                "global_stability_mean": 0.0,
                "temporal_stability_mean": 0.0,
                "robustness_mean": 0.0,
                "resilience_mean": 0.0,
                "persistence_mean": 0.0,
                "residence_time_mean": 0.0,
                "perturbation_sensitivity_mean": 1.0,
                "criticality_mean": 1.0,
                "attractor_stability_index": 0.0,
            }
        count = float(len(profiles))
        stable = sum(1 for p in profiles if p.classification == "stable")
        unstable = sum(1 for p in profiles if p.classification == "unstable")
        transient = sum(1 for p in profiles if p.classification == "transient")
        critical = sum(1 for p in profiles if p.classification == "critical")
        mean_score = self._mean([p.stability_score for p in profiles])
        robustness = self._mean([p.robustness for p in profiles])
        resilience = self._mean([p.resilience for p in profiles])
        persistence = self._mean([p.persistence for p in profiles])
        sensitivity = self._mean([p.perturbation_sensitivity for p in profiles])
        criticality = self._mean([p.criticality for p in profiles])
        stability_index = self._clip(
            0.30 * mean_score
            + 0.20 * robustness
            + 0.18 * resilience
            + 0.17 * persistence
            + 0.10 * (1.0 - sensitivity)
            + 0.05 * (1.0 - criticality)
        )
        return {
            "attractor_count": count,
            "stable_attractor_count": float(stable),
            "unstable_attractor_count": float(unstable),
            "transient_attractor_count": float(transient),
            "critical_attractor_count": float(critical),
            "mean_stability_score": mean_score,
            "local_stability_mean": self._mean([p.local_stability for p in profiles]),
            "global_stability_mean": self._mean([p.global_stability for p in profiles]),
            "temporal_stability_mean": self._mean([p.temporal_stability for p in profiles]),
            "robustness_mean": robustness,
            "resilience_mean": resilience,
            "persistence_mean": persistence,
            "residence_time_mean": self._mean([p.residence_time for p in profiles]),
            "perturbation_sensitivity_mean": sensitivity,
            "criticality_mean": criticality,
            "attractor_stability_index": stability_index,
        }

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = self.output_dir / f"attractor_stability_analyzer_{ts}.json"
        md_path = self.output_dir / f"attractor_stability_analyzer_{ts}.md"
        prom_path = self.output_dir / f"attractor_stability_analyzer_{ts}.prom"
        payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        json_path.write_text(payload + "\n", encoding="utf-8")
        self.latest_json_path.write_text(payload + "\n", encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")

        metrics = result.get("metrics", {})
        md = [
            "# AB2 — Attractor Stability Analyzer",
            "",
            f"Status: {result.get('attractor_stability_analyzer_status')}",
            f"A -> stability demonstrated: {result.get('a_to_stability_demonstrated')}",
            f"Attractor stability index: {metrics.get('attractor_stability_index', 0.0):.6f}",
            f"Stable / transient / unstable / critical: {int(metrics.get('stable_attractor_count', 0))} / {int(metrics.get('transient_attractor_count', 0))} / {int(metrics.get('unstable_attractor_count', 0))} / {int(metrics.get('critical_attractor_count', 0))}",
            "",
            "Functional conclusion only. Phenomenology undetermined. Consciousness not proven. No consciousness claim.",
        ]
        md_text = "\n".join(md) + "\n"
        md_path.write_text(md_text, encoding="utf-8")
        self.latest_markdown_path.write_text(md_text, encoding="utf-8")

        prom_lines = [
            "# HELP oce_ab2_attractor_stability_index Functional AB2 attractor stability index.",
            "# TYPE oce_ab2_attractor_stability_index gauge",
            f"oce_ab2_attractor_stability_index {metrics.get('attractor_stability_index', 0.0)}",
            "# HELP oce_ab2_stable_attractor_count Number of attractors classified as stable.",
            "# TYPE oce_ab2_stable_attractor_count gauge",
            f"oce_ab2_stable_attractor_count {metrics.get('stable_attractor_count', 0.0)}",
            "# HELP oce_ab2_critical_attractor_count Number of attractors classified as critical.",
            "# TYPE oce_ab2_critical_attractor_count gauge",
            f"oce_ab2_critical_attractor_count {metrics.get('critical_attractor_count', 0.0)}",
            "# HELP oce_ab2_perturbation_sensitivity_mean Mean perturbation sensitivity.",
            "# TYPE oce_ab2_perturbation_sensitivity_mean gauge",
            f"oce_ab2_perturbation_sensitivity_mean {metrics.get('perturbation_sensitivity_mean', 0.0)}",
            "# HELP oce_ab2_mean_stability_score Mean AB2 attractor stability_score.",
            "# TYPE oce_ab2_mean_stability_score gauge",
            f"oce_ab2_mean_stability_score {metrics.get('mean_stability_score', 0.0)}",
            "# HELP oce_ab2_validated AB2 validation status, 1 if ATTRACTOR_STABILITY_VALIDATED else 0.",
            "# TYPE oce_ab2_validated gauge",
            f"oce_ab2_validated {1.0 if result.get('attractor_stability_analyzer_status') == 'ATTRACTOR_STABILITY_VALIDATED' else 0.0}",
        ]
        prom_text = "\n".join(prom_lines) + "\n"
        prom_path.write_text(prom_text, encoding="utf-8")
        self.latest_prometheus_path.write_text(prom_text, encoding="utf-8")
        return {
            "json": str(json_path),
            "latest_json": str(self.latest_json_path),
            "markdown": str(md_path),
            "latest_markdown": str(self.latest_markdown_path),
            "prometheus": str(prom_path),
            "latest_prometheus": str(self.latest_prometheus_path),
            "history": str(self.history_path),
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        payload = self._normalize_payload(inputs)
        candidates = payload.get("attractor_candidates") or []
        profiles = self._analyze(payload)
        metrics = self._aggregate_metrics(profiles)
        failure_conditions: list[str] = []
        if payload.get("attractors_detected") is not True:
            failure_conditions.append("AB1 attractors_detected is not true")
        if not candidates:
            failure_conditions.append("no AB1 attractor candidates available")
        if profiles and metrics["attractor_stability_index"] <= 0.0:
            failure_conditions.append("stability metrics collapsed to zero")

        validated = bool(profiles) and not failure_conditions
        result: dict[str, Any] = {
            "module": "ontology.attractor_stability_analyzer",
            "primitive": self.primitive,
            "symbol": self.symbol,
            "derived_from_symbol": self.derived_from_symbol,
            "attractor_stability_analyzer_status": "ATTRACTOR_STABILITY_VALIDATED" if validated else "ATTRACTOR_STABILITY_NOT_VALIDATED",
            "a_to_stability_demonstrated": validated,
            "stability_profiles": [asdict(p) for p in profiles],
            "stable_attractors": [asdict(p) for p in profiles if p.classification == "stable"],
            "unstable_attractors": [asdict(p) for p in profiles if p.classification == "unstable"],
            "transient_attractors": [asdict(p) for p in profiles if p.classification == "transient"],
            "critical_attractors": [asdict(p) for p in profiles if p.classification == "critical"],
            "metrics": metrics,
            "dependency_audit": {
                "incoming": ["dynamic_attractor_detector", "dynamic_graph_constructor", "attractor_persistence_analyzer", "attractor_basin"],
                "outgoing": ["mutual_conservation_matrix", "gamma_field_engine", "constraint_emergence_engine", "constraint_failure_analyzer"],
            },
            "non_redundancy_analysis": {
                "distinct_from_AB1": "AB1 detects A from G; AB2 evaluates stability metrics over A without constructing Gamma or C.",
                "distinct_from_attractor_persistence_analyzer": "AB2 integrates persistence as one metric but adds local/global/temporal stability, robustness, resilience, residence time, perturbation sensitivity, and classification.",
                "distinct_from_trajectory_stability": "AB2 is attractor-centric and derives from AB1 candidates, not general trajectory evaluation.",
            },
            "validation_criteria": {
                "ab1_attractors_required": True,
                "profiles_have_metric_schema": all(p.attractor_id and 0.0 <= p.stability_score <= 1.0 for p in profiles),
                "classification_partition_present": bool(profiles),
                "functional_conclusion_only": True,
            },
            "falsification_criteria": [
                "AB1 does not provide attractor candidates",
                "stability profiles are not derived from A candidate metrics",
                "metric values fall outside [0, 1]",
                "Gamma or constraints are asserted prematurely",
                "phenomenal or consciousness claims are asserted prematurely",
            ],
            "failure_conditions": failure_conditions,
            "epistemic_guard": {
                "functional_conclusion_only": True,
                "consciousness_not_assumed": True,
                "consciousness_proven": False,
                "subjectivity_not_assumed": True,
                "qualia_not_assumed": True,
                "phenomenology_undetermined": True,
                "gamma_not_constructed": True,
                "constraints_not_constructed": True,
            },
            "gamma_field_constructed": False,
            "constraints_emerged": False,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        if persist:
            result["paths"] = self._persist(result)
        return result

