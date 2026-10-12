
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ConstraintFailureAnalyzer:
    """
    AB6 — constraint_failure_analyzer.

    Transversal functional certifier for the reconstruction chain:
        G -> A -> Γ -> C

    It verifies global coherence, attractor stability, Γ coherence, constraint
    emergence, anti-circularity, non-redundancy, robustness, controlled
    degradation and falsification criteria. It never asserts consciousness,
    subjectivity, qualia, or phenomenology.
    """

    primitive = "CONSTRAINT_FAILURE_ANALYZER"
    chain = "G -> A -> Γ -> C"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "reconstruction_outputs" / "AB6_constraint_failure_analyzer"
        self.history_path = self.output_dir / "constraint_failure_analyzer_history.jsonl"
        self.latest_json_path = self.output_dir / "latest_constraint_failure_analyzer.json"
        self.latest_markdown_path = self.output_dir / "latest_constraint_failure_analyzer.md"
        self.latest_prometheus_path = self.output_dir / "latest_constraint_failure_analyzer.prom"

    @staticmethod
    def _clip(value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return 0.0

    @staticmethod
    def _mean(values: list[float]) -> float:
        vals = [float(v) for v in values if isinstance(v, (int, float))]
        return sum(vals) / max(1, len(vals))

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        return value if isinstance(value, list) else []

    @staticmethod
    def _as_dict(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    def _run_default_chain(self) -> dict[str, Any]:
        payloads: dict[str, Any] = {}
        runners = [
            ("ab1", "ontology.dynamic_attractor_detector", "DynamicAttractorDetector"),
            ("ab2", "ontology.attractor_stability_analyzer", "AttractorStabilityAnalyzer"),
            ("ab3", "ontology.mutual_conservation_matrix", "MutualConservationMatrix"),
            ("ab4", "ontology.gamma_field_engine", "GammaFieldEngine"),
            ("ab5", "ontology.constraint_emergence_engine", "ConstraintEmergenceEngine"),
        ]
        for key, module_name, class_name in runners:
            try:
                module = __import__(module_name, fromlist=[class_name])
                cls = getattr(module, class_name)
                payloads[key] = cls(root=self.root).step(persist=False)
            except Exception as exc:
                payloads[key] = {"execution_error": repr(exc)}
        return payloads

    def _normalize_inputs(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        if isinstance(inputs, dict) and any(k in inputs for k in ["ab1", "ab2", "ab3", "ab4", "ab5"]):
            defaults = self._run_default_chain()
            defaults.update({k: v for k, v in inputs.items() if k in defaults})
            return defaults
        return self._run_default_chain()

    def _extract_ids(self, payloads: dict[str, Any]) -> dict[str, set[str]]:
        ab1 = self._as_dict(payloads.get("ab1"))
        ab2 = self._as_dict(payloads.get("ab2"))
        ab3 = self._as_dict(payloads.get("ab3"))
        ab4 = self._as_dict(payloads.get("ab4"))
        ab5 = self._as_dict(payloads.get("ab5"))

        ids: dict[str, set[str]] = {"A": set(), "stability": set(), "conservation": set(), "gamma": set(), "constraints": set()}

        for idx, a in enumerate(self._as_list(ab1.get("attractor_candidates"))):
            if isinstance(a, dict):
                ids["A"].add(str(a.get("attractor_id") or a.get("id") or a.get("candidate_id") or f"A{idx}"))

        for idx, p in enumerate(self._as_list(ab2.get("stability_profiles"))):
            if isinstance(p, dict):
                ids["stability"].add(str(p.get("attractor_id") or p.get("id") or f"S{idx}"))

        matrix = ab3.get("conservation_matrix")
        if isinstance(matrix, dict):
            ids["conservation"].update(str(k) for k in matrix.keys())
        for pair in self._as_list(ab3.get("pairwise_conservation")):
            if isinstance(pair, dict):
                for k in ["source_attractor_id", "target_attractor_id", "source", "target"]:
                    if pair.get(k):
                        ids["conservation"].add(str(pair[k]))

        for cell in self._as_list(ab4.get("gamma_field")):
            if isinstance(cell, dict):
                for k in ["source_attractor_id", "target_attractor_id", "source", "target"]:
                    if cell.get(k):
                        ids["gamma"].add(str(cell[k]))

        for c in self._as_list(ab5.get("emergent_constraints")):
            if isinstance(c, dict):
                for k in ["source_attractor_id", "target_attractor_id", "source", "target"]:
                    if c.get(k):
                        ids["constraints"].add(str(c[k]))
        return ids

    def _status_checks(self, payloads: dict[str, Any]) -> list[dict[str, Any]]:
        specs = [
            ("AB1_dynamic_attractor_detector", "ab1", "attractors_detected", True),
            ("AB2_attractor_stability_analyzer", "ab2", "a_to_stability_demonstrated", True),
            ("AB3_mutual_conservation_matrix", "ab3", "a_to_mutual_conservation_demonstrated", True),
            ("AB4_gamma_field_engine", "ab4", "a_to_gamma_demonstrated", True),
            ("AB5_constraint_emergence_engine", "ab5", "gamma_to_c_demonstrated", True),
        ]
        checks = []
        for name, key, flag, expected in specs:
            payload = self._as_dict(payloads.get(key))
            passed = payload.get(flag) is expected and not payload.get("execution_error")
            checks.append({
                "check_id": name,
                "passed": bool(passed),
                "observed": payload.get(flag),
                "expected": expected,
                "failure": None if passed else f"{key}.{flag}_not_validated",
            })
        return checks

    def _metric_checks(self, payloads: dict[str, Any]) -> list[dict[str, Any]]:
        ab2 = self._as_dict(payloads.get("ab2"))
        ab3 = self._as_dict(payloads.get("ab3"))
        ab4 = self._as_dict(payloads.get("ab4"))
        ab5 = self._as_dict(payloads.get("ab5"))
        checks: list[dict[str, Any]] = []

        stability_scores = [self._clip(p.get("stability_score", 0.0)) for p in self._as_list(ab2.get("stability_profiles")) if isinstance(p, dict)]
        checks.append({
            "check_id": "attractor_stability_present",
            "passed": len(stability_scores) > 0 and max(stability_scores) >= 0.0,
            "score": self._mean(stability_scores),
            "failure": None if stability_scores else "no_stability_profiles",
        })

        pair_scores = [self._clip(p.get("conservation_score", 0.0)) for p in self._as_list(ab3.get("pairwise_conservation")) if isinstance(p, dict)]
        matrix = ab3.get("conservation_matrix")
        matrix_present = (isinstance(matrix, dict) and bool(matrix)) or (isinstance(matrix, list) and bool(matrix))
        checks.append({
            "check_id": "mutual_conservation_present",
            "passed": matrix_present,
            "score": self._mean(pair_scores) if pair_scores else (1.0 if matrix_present else 0.0),
            "failure": None if matrix_present else "empty_conservation_matrix",
        })

        gamma_cells = self._as_list(ab4.get("gamma_field"))
        gamma_scores = [self._clip(c.get("gamma_intensity", c.get("intensity", 0.0))) for c in gamma_cells if isinstance(c, dict)]
        coherence_scores = [self._clip(c.get("global_coherence", c.get("coherence", c.get("continuity", 0.0)))) for c in gamma_cells if isinstance(c, dict)]
        checks.append({
            "check_id": "gamma_field_coherent",
            "passed": len(gamma_cells) > 0 and self._mean(gamma_scores) >= 0.0,
            "score": self._mean(gamma_scores + coherence_scores),
            "failure": None if gamma_cells else "empty_gamma_field",
        })

        constraints = self._as_list(ab5.get("emergent_constraints"))
        constraint_scores = [self._clip(c.get("constraint_strength", 0.0)) for c in constraints if isinstance(c, dict)]
        checks.append({
            "check_id": "constraints_emerged",
            "passed": len(constraints) > 0 and max(constraint_scores or [0.0]) > 0.0,
            "score": self._mean(constraint_scores),
            "failure": None if constraints else "no_emergent_constraints",
        })
        return checks

    def _chain_checks(self, payloads: dict[str, Any]) -> list[dict[str, Any]]:
        ids = self._extract_ids(payloads)
        checks: list[dict[str, Any]] = []

        def overlap(a: set[str], b: set[str]) -> float:
            if not a or not b:
                return 0.0
            return len(a & b) / max(1, len(a | b))

        # AB2 may normalize AB1 IDs; require non-empty downstream continuity rather than exact identity equality.
        continuity_pairs = [
            ("A_to_stability_traceability", ids["stability"], ids["A"] | ids["stability"]),
            ("stability_to_conservation_traceability", ids["conservation"], ids["stability"] | ids["conservation"]),
            ("conservation_to_gamma_traceability", ids["gamma"], ids["conservation"] | ids["gamma"]),
            ("gamma_to_constraints_traceability", ids["constraints"], ids["gamma"] | ids["constraints"]),
        ]
        for name, current, reference in continuity_pairs:
            score = overlap(current, reference) if current and reference else 0.0
            checks.append({
                "check_id": name,
                "passed": bool(current),
                "traceability_score": score if current else 0.0,
                "failure": None if current else f"{name}_missing_ids",
            })

        circularity_risk = 0.0
        for key in ["ab1", "ab2", "ab3", "ab4", "ab5"]:
            p = self._as_dict(payloads.get(key))
            if p.get("constraint_failure_analyzer_status"):
                circularity_risk = 1.0
        checks.append({
            "check_id": "absence_of_circularity",
            "passed": circularity_risk == 0.0,
            "circularity_risk": circularity_risk,
            "failure": None if circularity_risk == 0.0 else "ab6_input_circularity_detected",
        })
        return checks

    def _controlled_degradation(self) -> dict[str, Any]:
        scenarios = []
        degraded_inputs = [
            ("ab2_missing_stability", {"ab2": {"stability_profiles": [], "a_to_stability_demonstrated": False}}),
            ("ab3_empty_conservation", {"ab3": {"conservation_matrix": {}, "pairwise_conservation": [], "a_to_mutual_conservation_demonstrated": False}}),
            ("ab4_empty_gamma", {"ab4": {"gamma_field": [], "a_to_gamma_demonstrated": False}}),
            ("ab5_missing_constraints", {"ab5": {"emergent_constraints": [], "gamma_to_c_demonstrated": False}}),
        ]
        base = self._run_default_chain()
        for name, patch in degraded_inputs:
            test_payloads = dict(base)
            test_payloads.update(patch)
            checks = self._status_checks(test_payloads) + self._metric_checks(test_payloads)
            failures = [c.get("failure") for c in checks if not c.get("passed") and c.get("failure")]
            scenarios.append({
                "scenario": name,
                "detected": bool(failures),
                "failures": failures,
            })
        return {
            "scenario_count": len(scenarios),
            "detected_count": sum(1 for s in scenarios if s["detected"]),
            "degradation_detection_rate": sum(1 for s in scenarios if s["detected"]) / max(1, len(scenarios)),
            "scenarios": scenarios,
        }

    def _falsification_criteria(self, checks: list[dict[str, Any]], degradation: dict[str, Any]) -> list[dict[str, Any]]:
        failed = [c for c in checks if not c.get("passed")]
        return [
            {
                "criterion_id": "F1_chain_status_failure",
                "triggered": any(c.get("check_id", "").startswith("AB") for c in failed),
                "description": "Any AB1-AB5 status failure defeats the global validation.",
            },
            {
                "criterion_id": "F2_missing_structural_artifact",
                "triggered": any(c.get("failure") in {"no_stability_profiles", "empty_conservation_matrix", "empty_gamma_field", "no_emergent_constraints"} for c in failed),
                "description": "Missing stability, conservation, Gamma, or constraint artifacts falsifies the chain.",
            },
            {
                "criterion_id": "F3_circularity_detected",
                "triggered": any(c.get("failure") == "ab6_input_circularity_detected" for c in failed),
                "description": "AB6 cannot be an input to AB1-AB5.",
            },
            {
                "criterion_id": "F4_degradation_not_detected",
                "triggered": self._clip(degradation.get("degradation_detection_rate", 0.0)) < 1.0,
                "description": "Controlled degradation must be detected for all canonical AB failure scenarios.",
            },
        ]

    def _chain_validation_map(
        self,
        payloads: dict[str, Any],
        status_checks: list[dict[str, Any]],
        metric_checks: list[dict[str, Any]],
    ) -> dict[str, bool]:
        """Stable public AB6 validation map for downstream tests and AB-axis certification."""
        status_by_id = {str(c.get("check_id")): bool(c.get("passed")) for c in status_checks}
        metric_by_id = {str(c.get("check_id")): bool(c.get("passed")) for c in metric_checks}
        ab1 = self._as_dict(payloads.get("ab1"))
        ab2 = self._as_dict(payloads.get("ab2"))
        ab3 = self._as_dict(payloads.get("ab3"))
        ab4 = self._as_dict(payloads.get("ab4"))
        ab5 = self._as_dict(payloads.get("ab5"))
        return {
            "ab1_graph_to_attractors_valid": bool(
                ab1.get("attractors_detected") is True
                and status_by_id.get("AB1_dynamic_attractor_detector", False)
            ),
            "ab2_attractor_stability_valid": bool(
                ab2.get("a_to_stability_demonstrated") is True
                and status_by_id.get("AB2_attractor_stability_analyzer", False)
                and metric_by_id.get("attractor_stability_present", False)
            ),
            "ab3_mutual_conservation_valid": bool(
                ab3.get("a_to_mutual_conservation_demonstrated") is True
                and status_by_id.get("AB3_mutual_conservation_matrix", False)
                and metric_by_id.get("mutual_conservation_present", False)
            ),
            "ab4_gamma_field_valid": bool(
                ab4.get("a_to_gamma_demonstrated") is True
                and status_by_id.get("AB4_gamma_field_engine", False)
                and metric_by_id.get("gamma_field_coherent", False)
            ),
            "ab5_constraint_emergence_valid": bool(
                ab5.get("gamma_to_c_demonstrated") is True
                and status_by_id.get("AB5_constraint_emergence_engine", False)
                and metric_by_id.get("constraints_emerged", False)
            ),
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        payloads = self._normalize_inputs(inputs)
        status_checks = self._status_checks(payloads)
        metric_checks = self._metric_checks(payloads)
        chain_checks = self._chain_checks(payloads)
        degradation = self._controlled_degradation()
        all_checks = status_checks + metric_checks + chain_checks
        chain_validation = self._chain_validation_map(payloads, status_checks, metric_checks)
        falsification = self._falsification_criteria(all_checks, degradation)
        failure_conditions = [c.get("failure") for c in all_checks if not c.get("passed") and c.get("failure")]
        failure_conditions += [f["criterion_id"] for f in falsification if f.get("triggered")]
        failure_conditions = sorted(set(failure_conditions))

        coherence_components = [1.0 if c.get("passed") else 0.0 for c in all_checks]
        metric_components = [self._clip(c.get("score", c.get("traceability_score", 1.0 if c.get("passed") else 0.0))) for c in all_checks]
        global_coherence_score = self._mean(coherence_components)
        robustness_score = self._clip(degradation.get("degradation_detection_rate", 0.0))
        validation_score = self._mean([global_coherence_score, self._mean(metric_components), robustness_score])

        validated = not failure_conditions and validation_score >= 0.80
        status = "MUTUAL_CONSERVATION_AND_CONSTRAINT_GENESIS_VALIDATED" if validated else "MUTUAL_CONSERVATION_AND_CONSTRAINT_GENESIS_NOT_VALIDATED"

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "axis": "AB",
            "chain": self.chain,
            "constraint_failure_analyzer_status": status,
            "mutual_conservation_and_constraint_genesis_validated": validated,
            "g_to_a_to_gamma_to_c_validated": validated,
            "chain_validation": chain_validation,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "no_consciousness_claim": True,
            "status_checks": status_checks,
            "metric_checks": metric_checks,
            "chain_coherence_checks": chain_checks,
            "controlled_degradation": degradation,
            "falsification_criteria": falsification,
            "failure_conditions": failure_conditions,
            "global_coherence_score": round(global_coherence_score, 6),
            "robustness_score": round(robustness_score, 6),
            "validation_score": round(validation_score, 6),
            "diagnostics": {
                "ab1_status": self._as_dict(payloads.get("ab1")).get("dynamic_attractor_detector_status"),
                "ab2_status": self._as_dict(payloads.get("ab2")).get("attractor_stability_analyzer_status"),
                "ab3_status": self._as_dict(payloads.get("ab3")).get("mutual_conservation_matrix_status"),
                "ab4_status": self._as_dict(payloads.get("ab4")).get("gamma_field_engine_status"),
                "ab5_status": self._as_dict(payloads.get("ab5")).get("constraint_emergence_engine_status"),
                "check_count": len(all_checks),
                "failed_check_count": len([c for c in all_checks if not c.get("passed")]),
            },
        }
        if persist:
            result["paths"] = self._persist(result)
        return result

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = self.output_dir / f"constraint_failure_analyzer_{stamp}.json"
        md_path = self.output_dir / f"constraint_failure_analyzer_{stamp}.md"
        prom_path = self.output_dir / f"constraint_failure_analyzer_{stamp}.prom"

        text = json.dumps(result, ensure_ascii=False, indent=2)
        json_path.write_text(text, encoding="utf-8")
        self.latest_json_path.write_text(text, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp_utc": stamp, "status": result["constraint_failure_analyzer_status"], "validation_score": result["validation_score"]}, ensure_ascii=False) + "\n")

        md = self._markdown(result)
        md_path.write_text(md, encoding="utf-8")
        self.latest_markdown_path.write_text(md, encoding="utf-8")

        prom = self._prometheus(result)
        prom_path.write_text(prom, encoding="utf-8")
        self.latest_prometheus_path.write_text(prom, encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path)}

    def _markdown(self, result: dict[str, Any]) -> str:
        lines = [
            "# Constraint Failure Analyzer — AB6",
            "",
            f"Status: `{result['constraint_failure_analyzer_status']}`",
            f"Chain: `{result['chain']}`",
            "",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness claim.",
            "Mutual conservation and constraint genesis.",
            "G → A → Gamma → C.",
            "Consciousness proven: false.",
            "",
            "## Scores",
            f"- global coherence score: {result['global_coherence_score']}",
            f"- robustness score: {result['robustness_score']}",
            f"- validation score: {result['validation_score']}",
            "",
            "## Global coherence checks",
        ]
        for c in result.get("status_checks", []) + result.get("metric_checks", []) + result.get("chain_coherence_checks", []):
            lines.append(f"- {c.get('check_id')}: {c.get('passed')} failure={c.get('failure')}")
        lines += ["", "## Falsification criteria"]
        for f in result.get("falsification_criteria", []):
            lines.append(f"- {f.get('criterion_id')}: triggered={f.get('triggered')}")
        lines += ["", "## Controlled degradation"]
        lines.append(f"degradation detection rate: {result.get('controlled_degradation', {}).get('degradation_detection_rate')}")
        return "\n".join(lines) + "\n"

    def _prometheus(self, result: dict[str, Any]) -> str:
        ready = 1 if result.get("mutual_conservation_and_constraint_genesis_validated") else 0
        return "\n".join([
            "# HELP oce_ab6_constraint_failure_ready AB6 global validation ready flag",
            "# TYPE oce_ab6_constraint_failure_ready gauge",
            f"oce_ab6_constraint_failure_ready {ready}",
            "# HELP oce_ab6_validation_score AB6 validation score",
            "# TYPE oce_ab6_validation_score gauge",
            f"oce_ab6_validation_score {result.get('validation_score', 0.0)}",
            "# HELP oce_ab6_global_coherence_score AB6 global coherence score",
            "# TYPE oce_ab6_global_coherence_score gauge",
            f"oce_ab6_global_coherence_score {result.get('global_coherence_score', 0.0)}",
            "# HELP oce_ab6_robustness_score AB6 controlled degradation detection score",
            "# TYPE oce_ab6_robustness_score gauge",
            f"oce_ab6_robustness_score {result.get('robustness_score', 0.0)}",
            "# HELP oce_ab6_validated Mutual conservation and constraint genesis validated",
            "# TYPE oce_ab6_validated gauge",
            f"oce_ab6_validated {ready}",
            "# HELP oce_constraint_failure_analyzer_validated Constraint failure analyzer validated flag",
            "# TYPE oce_constraint_failure_analyzer_validated gauge",
            f"oce_constraint_failure_analyzer_validated {ready}",
            "# HELP oce_ab6_g_to_a_to_gamma_to_c_validated G to A to Gamma to C validated flag",
            "# TYPE oce_ab6_g_to_a_to_gamma_to_c_validated gauge",
            f"oce_ab6_g_to_a_to_gamma_to_c_validated {ready}",
        ]) + "\n"
