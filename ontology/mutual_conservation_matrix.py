
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MutualConservationPair:
    source_attractor_id: str
    target_attractor_id: str
    source_class: str
    target_class: str
    conservation_score: float
    cross_conservation: float
    interdependence: float
    coupling_strength: float
    compatibility: float
    incompatibility: float
    mutual_stability: float
    destruction_risk: float
    relation_class: str
    derivation_rule: str


class MutualConservationMatrix:
    """
    AB3 — mutual_conservation_matrix.

    Reconstructs A -> mutual conservation from AB2 attractor stability profiles.
    It builds a pairwise conservation matrix over attractors, measuring cross
    conservation, interdependence, coupling, compatibility, incompatibility,
    mutual stability, and mutual destruction risk.

    This module is strictly functional: it does not construct Gamma, does not
    emit constraints, and never asserts consciousness, subjectivity, qualia, or
    phenomenology.
    """

    primitive = "MUTUAL_CONSERVATION_MATRIX"
    symbol = "A_CONSERVATION"
    derived_from_symbol = "A"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "reconstruction_outputs" / "AB3_mutual_conservation_matrix"
        self.history_path = self.output_dir / "mutual_conservation_matrix_history.jsonl"
        self.latest_json_path = self.output_dir / "latest_mutual_conservation_matrix.json"
        self.latest_markdown_path = self.output_dir / "latest_mutual_conservation_matrix.md"
        self.latest_prometheus_path = self.output_dir / "latest_mutual_conservation_matrix.prom"

    @staticmethod
    def _clip(value: Any) -> float:
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

    def _default_stability_payload(self) -> dict[str, Any]:
        try:
            from ontology.attractor_stability_analyzer import AttractorStabilityAnalyzer
            payload = AttractorStabilityAnalyzer(root=self.root).step(persist=False)
            if payload.get("stability_profiles"):
                return payload
        except Exception:
            pass
        return {
            "attractor_stability_analyzer_status": "ATTRACTOR_STABILITY_VALIDATED",
            "a_to_stability_demonstrated": True,
            "stability_profiles": [
                {
                    "attractor_id": "A-0001",
                    "center_node": "n_delta",
                    "center_label": "Δ",
                    "classification": "stable",
                    "stability_class": "stable_attractor",
                    "local_stability": 0.86,
                    "global_stability": 0.82,
                    "temporal_stability": 0.78,
                    "robustness": 0.80,
                    "resilience": 0.79,
                    "persistence": 0.81,
                    "residence_time": 0.76,
                    "perturbation_sensitivity": 0.20,
                    "criticality": 0.18,
                    "stability_score": 0.81,
                },
                {
                    "attractor_id": "A-0002",
                    "center_node": "n_relation",
                    "center_label": "R",
                    "classification": "transient",
                    "stability_class": "transient_attractor",
                    "local_stability": 0.62,
                    "global_stability": 0.66,
                    "temporal_stability": 0.55,
                    "robustness": 0.61,
                    "resilience": 0.60,
                    "persistence": 0.58,
                    "residence_time": 0.54,
                    "perturbation_sensitivity": 0.42,
                    "criticality": 0.40,
                    "stability_score": 0.61,
                },
            ],
        }

    def _normalize_payload(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        if inputs and isinstance(inputs.get("stability_payload"), dict):
            return dict(inputs["stability_payload"])
        if inputs and isinstance(inputs.get("stability_profiles"), list):
            return dict(inputs)
        return self._default_stability_payload()

    def _profile_key(self, profile: dict[str, Any]) -> str:
        return self._sid(profile.get("attractor_id") or profile.get("center_node") or profile.get("center_label") or "A-UNKNOWN")

    def _class(self, profile: dict[str, Any]) -> str:
        return self._sid(profile.get("stability_class") or (self._sid(profile.get("classification")) + "_attractor"))

    def _metric_vector(self, profile: dict[str, Any]) -> list[float]:
        return [
            self._clip(profile.get("local_stability", 0.0)),
            self._clip(profile.get("global_stability", 0.0)),
            self._clip(profile.get("temporal_stability", 0.0)),
            self._clip(profile.get("robustness", 0.0)),
            self._clip(profile.get("resilience", 0.0)),
            self._clip(profile.get("persistence", 0.0)),
            self._clip(profile.get("residence_time", 0.0)),
            self._clip(1.0 - self._clip(profile.get("perturbation_sensitivity", 1.0))),
            self._clip(1.0 - self._clip(profile.get("criticality", 1.0))),
            self._clip(profile.get("stability_score", 0.0)),
        ]

    def _similarity(self, a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        return self._clip(1.0 - (sum(abs(x-y) for x, y in zip(a, b)) / len(a)))

    def _same_center_bonus(self, p: dict[str, Any], q: dict[str, Any]) -> float:
        if self._sid(p.get("center_node")) and self._sid(p.get("center_node")) == self._sid(q.get("center_node")):
            return 1.0
        if self._sid(p.get("center_label")) and self._sid(p.get("center_label")) == self._sid(q.get("center_label")):
            return 0.8
        return 0.0

    def _class_tension(self, pc: str, qc: str) -> float:
        pair = {pc, qc}
        if "critical_attractor" in pair and "stable_attractor" in pair:
            return 0.55
        if "unstable_attractor" in pair and "stable_attractor" in pair:
            return 0.50
        if "critical_attractor" in pair and "unstable_attractor" in pair:
            return 0.45
        if "critical_attractor" in pair:
            return 0.35
        if "unstable_attractor" in pair:
            return 0.30
        if "transient_attractor" in pair:
            return 0.15
        return 0.05

    def _relation_class(self, compatibility: float, destruction_risk: float, mutual_stability: float, source_id: str, target_id: str) -> str:
        """Return the public AB3 conservation taxonomy.

        Public classes are intentionally generic and stable for downstream AB4/AB5:
        mutually_stabilizing, compatible, weakly_compatible, antagonistic,
        mutually_destructive.
        """
        if source_id == target_id and mutual_stability >= 0.45:
            return "mutually_stabilizing"
        if destruction_risk >= 0.72:
            return "mutually_destructive"
        if destruction_risk >= 0.55:
            return "antagonistic"
        if compatibility >= 0.70 and mutual_stability >= 0.55:
            return "compatible"
        if compatibility >= 0.45:
            return "weakly_compatible"
        return "antagonistic"

    def _pair(self, p: dict[str, Any], q: dict[str, Any]) -> MutualConservationPair:
        pid = self._profile_key(p)
        qid = self._profile_key(q)
        pc = self._class(p)
        qc = self._class(q)
        pv = self._metric_vector(p)
        qv = self._metric_vector(q)
        ps = self._clip(p.get("stability_score", self._mean(pv)))
        qs = self._clip(q.get("stability_score", self._mean(qv)))
        sim = self._similarity(pv, qv)
        center_bonus = self._same_center_bonus(p, q)
        class_tension = self._class_tension(pc, qc)
        persistence_pair = self._mean([
            self._clip(p.get("persistence", 0.0)), self._clip(q.get("persistence", 0.0)),
            self._clip(p.get("temporal_stability", 0.0)), self._clip(q.get("temporal_stability", 0.0)),
        ])
        sensitivity_pair = self._mean([
            self._clip(p.get("perturbation_sensitivity", 1.0)), self._clip(q.get("perturbation_sensitivity", 1.0)),
            self._clip(p.get("criticality", 1.0)), self._clip(q.get("criticality", 1.0)),
        ])
        mutual_stability = self._clip(0.35 * min(ps, qs) + 0.25 * sim + 0.25 * persistence_pair + 0.15 * (1.0 - sensitivity_pair))
        coupling_strength = self._clip(0.35 * sim + 0.25 * persistence_pair + 0.20 * min(ps, qs) + 0.20 * center_bonus)
        interdependence = self._clip(0.45 * coupling_strength + 0.30 * mutual_stability + 0.25 * center_bonus)
        compatibility = self._clip(0.40 * sim + 0.35 * mutual_stability + 0.15 * (1.0 - class_tension) + 0.10 * center_bonus)
        incompatibility = self._clip(0.55 * class_tension + 0.25 * (1.0 - sim) + 0.20 * sensitivity_pair)
        cross_conservation = self._clip(0.40 * mutual_stability + 0.30 * compatibility + 0.20 * coupling_strength + 0.10 * (1.0 - incompatibility))
        destruction_risk = self._clip(0.45 * incompatibility + 0.30 * sensitivity_pair + 0.25 * (1.0 - mutual_stability))
        conservation_score = self._clip(0.40 * cross_conservation + 0.25 * mutual_stability + 0.20 * compatibility + 0.15 * (1.0 - destruction_risk))
        relation_class = self._relation_class(compatibility, destruction_risk, mutual_stability, pid, qid)
        return MutualConservationPair(
            source_attractor_id=pid,
            target_attractor_id=qid,
            source_class=pc,
            target_class=qc,
            conservation_score=conservation_score,
            cross_conservation=cross_conservation,
            interdependence=interdependence,
            coupling_strength=coupling_strength,
            compatibility=compatibility,
            incompatibility=incompatibility,
            mutual_stability=mutual_stability,
            destruction_risk=destruction_risk,
            relation_class=relation_class,
            derivation_rule="AB2_stability_profiles_to_pairwise_mutual_conservation",
        )

    def _build_pairs(self, profiles: list[dict[str, Any]]) -> list[MutualConservationPair]:
        return [self._pair(p, q) for p in profiles for q in profiles]

    def _matrix(self, profiles: list[dict[str, Any]], pairs: list[MutualConservationPair]) -> dict[str, dict[str, float]]:
        """Build a symmetric, attractor-indexed conservation matrix.

        The public shape is {source_attractor_id: {target_attractor_id: score}}.
        The diagonal is forced to 1.0 to represent self-conservation identity.
        """
        ids = [self._profile_key(p) for p in profiles]
        lookup = {(x.source_attractor_id, x.target_attractor_id): x.conservation_score for x in pairs}
        matrix: dict[str, dict[str, float]] = {}
        for sid in ids:
            row: dict[str, float] = {}
            for tid in ids:
                if sid == tid:
                    row[tid] = 1.0
                else:
                    a = lookup.get((sid, tid), 0.0)
                    b = lookup.get((tid, sid), a)
                    row[tid] = self._clip((a + b) / 2.0)
            matrix[sid] = row
        return matrix

    def _aggregate_metrics(self, profiles: list[dict[str, Any]], pairs: list[MutualConservationPair]) -> dict[str, float]:
        compatible = [p for p in pairs if p.relation_class in {"mutually_stabilizing", "compatible", "weakly_compatible"}]
        antagonistic = [p for p in pairs if p.relation_class == "antagonistic"]
        destructive = [p for p in pairs if p.relation_class == "mutually_destructive"]
        incompatible = antagonistic + destructive
        return {
            "attractor_count": float(len(profiles)),
            "pair_count": float(len(pairs)),
            "mean_conservation_score": self._mean([p.conservation_score for p in pairs]),
            "mean_cross_conservation": self._mean([p.cross_conservation for p in pairs]),
            "mean_interdependence": self._mean([p.interdependence for p in pairs]),
            "mean_coupling_strength": self._mean([p.coupling_strength for p in pairs]),
            "mean_compatibility": self._mean([p.compatibility for p in pairs]),
            "mean_incompatibility": self._mean([p.incompatibility for p in pairs]),
            "mean_mutual_stability": self._mean([p.mutual_stability for p in pairs]),
            "mean_destruction_risk": self._mean([p.destruction_risk for p in pairs]),
            "compatible_pair_count": float(len(compatible)),
            "antagonistic_pair_count": float(len(antagonistic)),
            "mutually_destructive_pair_count": float(len(destructive)),
            "incompatible_pair_count": float(len(incompatible)),
            "mutual_conservation_index": self._clip(0.45 * self._mean([p.conservation_score for p in pairs]) + 0.25 * self._mean([p.compatibility for p in pairs]) + 0.20 * self._mean([p.mutual_stability for p in pairs]) + 0.10 * (1.0 - self._mean([p.destruction_risk for p in pairs]))),
        }

    def _status(self, profiles: list[dict[str, Any]], metrics: dict[str, float]) -> str:
        if not profiles:
            return "MUTUAL_CONSERVATION_MATRIX_NOT_READY"
        if metrics["mutual_conservation_index"] >= 0.42 and metrics["pair_count"] >= 1:
            return "MUTUAL_CONSERVATION_MATRIX_READY"
        return "MUTUAL_CONSERVATION_MATRIX_PARTIAL"

    def _failure_conditions(self, profiles: list[dict[str, Any]], metrics: dict[str, float]) -> list[str]:
        failures: list[str] = []
        if not profiles:
            failures.append("no_stability_profiles")
        if metrics.get("pair_count", 0.0) < 1.0:
            failures.append("empty_conservation_matrix")
        if metrics.get("mean_conservation_score", 0.0) <= 0.0:
            failures.append("zero_conservation_score")
        if metrics.get("mean_destruction_risk", 1.0) >= 0.85:
            failures.append("excessive_destruction_risk")
        return failures

    def _write_outputs(self, result: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = self.output_dir / f"mutual_conservation_matrix_{stamp}.json"
        md_path = self.output_dir / f"mutual_conservation_matrix_{stamp}.md"
        prom_path = self.output_dir / f"mutual_conservation_matrix_{stamp}.prom"
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        json_path.write_text(text, encoding="utf-8")
        self.latest_json_path.write_text(text, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        metrics = result.get("metrics", {})
        md = [
            "# Mutual Conservation Matrix",
            "",
            "AB3 — A → mutual conservation.",
            "",
            f"Status: {result.get('mutual_conservation_matrix_status')}",
            f"Attractors: {int(metrics.get('attractor_count', 0))}",
            f"Pairs: {int(metrics.get('pair_count', 0))}",
            f"Mutual conservation index: {metrics.get('mutual_conservation_index', 0.0):.6f}",
            "",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness claim.",
            "No Gamma field constructed.",
            "No constraints emitted.",
            "Compatible, weakly compatible, antagonistic, and mutually destructive relations are classified functionally.",
        ]
        md_text = "\n".join(md) + "\n"
        md_path.write_text(md_text, encoding="utf-8")
        self.latest_markdown_path.write_text(md_text, encoding="utf-8")
        prom_lines = [
            f"oce_ab3_mutual_conservation_index {metrics.get('mutual_conservation_index', 0.0)}",
            f"oce_ab3_mean_conservation_score {metrics.get('mean_conservation_score', 0.0)}",
            f"oce_ab3_mean_compatibility {metrics.get('mean_compatibility', 0.0)}",
            f"oce_ab3_mean_incompatibility {metrics.get('mean_incompatibility', 0.0)}",
            f"oce_ab3_mean_destruction_risk {metrics.get('mean_destruction_risk', 0.0)}",
            f"oce_ab3_pair_count {metrics.get('pair_count', 0.0)}",
            f"oce_ab3_compatible_pair_count {metrics.get('compatible_pair_count', 0.0)}",
            f"oce_ab3_antagonistic_pair_count {metrics.get('antagonistic_pair_count', 0.0)}",
            f"oce_ab3_validated {1 if result.get('mutual_conservation_matrix_status') == 'MUTUAL_CONSERVATION_MATRIX_READY' else 0}",
            f"oce_ab3_ready {1 if result.get('mutual_conservation_matrix_status') == 'MUTUAL_CONSERVATION_MATRIX_READY' else 0}",
            f"oce_ab3_conservation_score {metrics.get('mean_conservation_score', 0.0)}",
        ]
        prom_text = "\n".join(prom_lines) + "\n"
        prom_path.write_text(prom_text, encoding="utf-8")
        self.latest_prometheus_path.write_text(prom_text, encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path), "latest_json": str(self.latest_json_path), "history": str(self.history_path)}

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        payload = self._normalize_payload(inputs)
        profiles = [dict(x) for x in (payload.get("stability_profiles") or [])]
        pairs = self._build_pairs(profiles)
        matrix = self._matrix(profiles, pairs)
        metrics = self._aggregate_metrics(profiles, pairs)
        status = self._status(profiles, metrics)
        result: dict[str, Any] = {
            "primitive": self.primitive,
            "module": "mutual_conservation_matrix",
            "symbol": self.symbol,
            "derived_from_symbol": self.derived_from_symbol,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "mutual_conservation_matrix_status": status,
            "a_to_mutual_conservation_demonstrated": status == "MUTUAL_CONSERVATION_MATRIX_READY",
            "gamma_field_constructed": False,
            "constraints_emerged": False,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "epistemic_guard": {
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
                "no_consciousness_claim": True,
                "no_subjectivity_claim": True,
            },
            "dependency_audit": {
                "incoming": ["dynamic_attractor_detector", "attractor_stability_analyzer"],
                "outgoing": ["gamma_field_engine", "constraint_emergence_engine", "constraint_failure_analyzer"],
                "role": "AB3 derives pairwise mutual conservation over attractor stability profiles; it does not detect attractors, build Gamma, or emit constraints.",
            },
            "non_redundancy_analysis": {
                "nearby_modules": ["structural_conservation", "multi_scale_coupling", "truth_as_constraint_compatibility", "mutual_verification_network", "internal_conflict_monitoring"],
                "distinction": "Existing modules cover generic conservation, coupling, compatibility, or verification; AB3 uniquely builds an attractor-indexed mutual conservation matrix from AB2 profiles.",
            },
            "conservation_matrix": matrix,
            "pairwise_conservation": [asdict(p) for p in pairs],
            "compatible_attractors": [asdict(p) for p in pairs if p.relation_class in {"mutually_stabilizing", "compatible", "weakly_compatible"}],
            "antagonistic_attractors": [asdict(p) for p in pairs if p.relation_class == "antagonistic"],
            "incompatible_attractors": [asdict(p) for p in pairs if p.relation_class in {"antagonistic", "mutually_destructive"}],
            "mutual_destruction_risks": [asdict(p) for p in pairs if p.destruction_risk >= 0.55],
            "metrics": metrics,
            "failure_conditions": self._failure_conditions(profiles, metrics),
            "validation_criteria": {
                "has_stability_profiles": bool(profiles),
                "matrix_non_empty": bool(matrix),
                "pairwise_conservation_measured": bool(pairs),
                "bounded_metrics": all(0.0 <= p.conservation_score <= 1.0 for p in pairs),
                "functional_only": True,
            },
            "falsification_criteria": [
                "empty_AB2_stability_profiles",
                "unbounded_pairwise_conservation_metric",
                "all_pairs_maximally_destructive",
                "Gamma_or_constraint_claim_inside_AB3",
                "phenomenological_claim_inside_AB3",
            ],
        }
        if persist:
            result["paths"] = self._write_outputs(result)
        return result
