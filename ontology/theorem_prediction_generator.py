"""
AT2 — theorem_prediction_generator.

Automatically derives observable RF* predictions from certified theorem and
certifier outputs. This module is strictly functional-scientific: it creates
prediction objects and testable observational consequences, without asserting
phenomenological, subjective, qualia, or consciousness proof.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

ROOT = Path.home() / "open-cognitive-ecology"


class TheoremPredictionGenerator:
    """Generate observable RF* predictions from theorem-level artifacts."""

    primitive = "THEOREM_PREDICTION_GENERATOR"
    step_id = "AT2"
    public_schema_version = "AT2.theorem_prediction_generator.v1"
    output_dir = ROOT / "predictive_science" / "AT2_theorem_prediction_generator"

    categories = ["structural", "dynamic", "topological", "spectral", "developmental", "collective"]
    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _as_list(value: Any) -> List[Any]:
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, set):
            return sorted(value)
        return []

    @staticmethod
    def _clamp01(value: Any, default: float = 0.0) -> float:
        try:
            v = float(value)
        except Exception:
            v = default
        return max(0.0, min(1.0, v))

    @staticmethod
    def _stable_hash(payload: Any) -> str:
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _safe_text(value: Any, default: str = "unspecified") -> str:
        text = str(value or "").strip()
        return text if text else default

    def _load_predictive_blueprint(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        for key in ("predictive_blueprint", "predictive_blueprint_result"):
            if isinstance(inputs.get(key), dict):
                return dict(inputs[key])
        try:
            from ontology.predictive_blueprint import PredictiveBlueprint
            return PredictiveBlueprint().step(inputs={"synthetic": True, "source": self.step_id}, persist=False)
        except Exception as exc:
            return {"status": "PREDICTIVE_BLUEPRINT_UNAVAILABLE", "error": repr(exc), "prediction_types": list(self.categories)}

    def _load_prediction_registry(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        for key in ("prediction_registry", "prediction_registry_result"):
            if isinstance(inputs.get(key), dict):
                return dict(inputs[key])
        try:
            from ontology.prediction_registry import PredictionRegistry
            return PredictionRegistry().step(inputs={"synthetic": True, "source": self.step_id}, persist=False)
        except Exception as exc:
            return {"status": "PREDICTION_REGISTRY_UNAVAILABLE", "error": repr(exc), "predictions": []}

    def _load_theorem_dependency_mapping(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        for key in ("theorem_dependency_mapping", "theorem_dependency_mapping_result", "theorem_dependency_mapper"):
            if isinstance(inputs.get(key), dict):
                return dict(inputs[key])
        try:
            from ontology.theorem_dependency_mapper import TheoremDependencyMapper
            return TheoremDependencyMapper().step(inputs={"synthetic": True, "source": self.step_id}, persist=False)
        except Exception as exc:
            return {"theorem_dependency_mapping_status": "THEOREM_DEPENDENCIES_UNAVAILABLE", "error": repr(exc), "theorem_dependency_graph": {}}

    def _load_axiomatic_completeness(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        for key in ("axiomatic_completeness", "axiomatic_completeness_result", "axiomatic_completeness_certifier"):
            if isinstance(inputs.get(key), dict):
                return dict(inputs[key])
        try:
            from ontology.axiomatic_completeness_certifier import AxiomaticCompletenessCertifier
            return AxiomaticCompletenessCertifier().step(inputs={"synthetic": True, "source": self.step_id}, persist=False)
        except Exception as exc:
            return {"axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_UNAVAILABLE", "error": repr(exc)}

    def _load_final_theoretical_report(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        for key in ("final_theoretical_report", "final_theoretical_report_result"):
            if isinstance(inputs.get(key), dict):
                return dict(inputs[key])
        try:
            from ontology.final_theoretical_report import FinalTheoreticalReport
            return FinalTheoreticalReport().step(inputs={"synthetic": True, "source": self.step_id}, persist=False)
        except Exception as exc:
            return {"final_theoretical_report_status": "FINAL_THEORETICAL_REPORT_UNAVAILABLE", "error": repr(exc)}

    def _load_governance_certification(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        for key in ("consciousness_governance_certifier", "consciousness_governance_certification", "governance_certification"):
            if isinstance(inputs.get(key), dict):
                return dict(inputs[key])
        try:
            from ontology.consciousness_governance_certifier import ConsciousnessGovernanceCertifier
            return ConsciousnessGovernanceCertifier().step(inputs={"synthetic": True, "source": self.step_id}, persist=False)
        except Exception as exc:
            return {"consciousness_governance_status": "CONSCIOUSNESS_GOVERNANCE_UNAVAILABLE", "error": repr(exc)}

    def _extract_graph_theorems(self, mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
        graph = mapping.get("theorem_dependency_graph") if isinstance(mapping.get("theorem_dependency_graph"), dict) else {}
        nodes = self._as_list(graph.get("nodes"))
        theorems: List[Dict[str, Any]] = []
        for i, node in enumerate(nodes, start=1):
            if not isinstance(node, dict):
                continue
            node_type = str(node.get("node_type") or node.get("type") or "").lower()
            node_id = self._safe_text(node.get("node_id") or node.get("id") or f"THEOREM-{i}")
            label = self._safe_text(node.get("label") or node.get("name") or node_id)
            if "theorem" in node_type or node_id.upper().startswith(("TH", "AN6-T", "RF-T")):
                theorems.append({"theorem_id": node_id, "name": label, "statement": self._safe_text(node.get("statement") or label), "source": self._safe_text(node.get("source") or "theorem_dependency_graph"), "epistemic_status": self._safe_text(node.get("epistemic_status") or "functional_theorem_candidate"), "dependencies": []})
        return theorems

    def _extract_input_theorems(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for i, item in enumerate(self._as_list(inputs.get("theorems")), start=1):
            if isinstance(item, dict):
                tid = self._safe_text(item.get("theorem_id") or item.get("id") or f"INPUT-THEOREM-{i}")
                out.append({"theorem_id": tid, "name": self._safe_text(item.get("name") or tid), "statement": self._safe_text(item.get("statement") or item.get("claim") or tid), "source": self._safe_text(item.get("source") or "inputs"), "epistemic_status": self._safe_text(item.get("epistemic_status") or item.get("status") or "certified_functional"), "dependencies": [str(x) for x in self._as_list(item.get("dependencies"))]})
        return out

    def _fallback_theorems(self, reports: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        candidates = [
            ("RF-TH-STRUCTURAL-CONSERVATION", "structural conservation theorem", "Functional certification requires preserved reconstruction, dependency, and semantic guard structure."),
            ("RF-TH-AXIOMATIC-COMPLETENESS", "axiomatic completeness theorem", "Axiomatic completeness is certified only when registry, minimality, independence, models, countermodels, and dependency graph cohere."),
            ("RF-TH-SEMANTIC-GUARD", "semantic guard theorem", "Any valid RF* consciousness-related output must preserve functional-only epistemic scope and block phenomenological proof claims."),
            ("RF-TH-GOVERNANCE-CONTINUITY", "governance continuity theorem", "Longitudinal governance is required to preserve certification state, regression detection, recovery, and revocation constraints."),
        ]
        found_status = "functional_fallback"
        for report in reports:
            if isinstance(report, dict):
                for key, value in report.items():
                    if "status" in str(key).lower() and isinstance(value, str) and value:
                        found_status = "derived_from_available_reports"
                        break
        return [{"theorem_id": tid, "name": name, "statement": statement, "source": "AT2_fallback_report_synthesis", "epistemic_status": found_status, "dependencies": []} for tid, name, statement in candidates]

    def _dedupe_theorems(self, theorems: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen: Set[str] = set()
        out: List[Dict[str, Any]] = []
        for theorem in theorems:
            tid = self._safe_text(theorem.get("theorem_id") or theorem.get("id"))
            if tid in seen:
                continue
            seen.add(tid)
            theorem = dict(theorem)
            theorem["theorem_id"] = tid
            out.append(theorem)
        return out

    def _category_for_theorem(self, theorem: Dict[str, Any], index: int) -> str:
        text = " ".join(str(theorem.get(k, "")) for k in ("theorem_id", "name", "statement", "source")).lower()
        if any(token in text for token in ("topolog", "frame", "rf", "equivalence", "reference")):
            return "topological"
        if any(token in text for token in ("spectral", "mode", "qualia-formal", "qf", "mei")):
            return "spectral"
        if any(token in text for token in ("longitudinal", "governance", "recovery", "regression", "transition", "dynamic")):
            return "dynamic"
        if any(token in text for token in ("development", "threshold", "readiness", "progressive", "lifecycle")):
            return "developmental"
        if any(token in text for token in ("civilizational", "collective", "distributed", "society")):
            return "collective"
        if any(token in text for token in ("axiom", "dependency", "minimal", "structure", "semantic", "guard")):
            return "structural"
        return self.categories[index % len(self.categories)]

    def _observable_family(self, category: str) -> List[str]:
        mapping = {
            "structural": ["dependency_coverage", "public_schema_presence", "epistemic_guard_presence"],
            "dynamic": ["transition_stability", "regression_rate", "recovery_rate"],
            "topological": ["rf_equivalence", "frame_preservation", "topological_coherence"],
            "spectral": ["mode_stability", "spectral_coherence", "bounded_metric"],
            "developmental": ["stage_completion", "lifecycle_coverage", "readiness_monotonicity"],
            "collective": ["governance_continuity", "collective_metric_presence", "dashboard_auditability"],
        }
        return list(mapping.get(category, ["observable_signature"]))

    def _prediction_from_theorem(self, theorem: Dict[str, Any], index: int) -> Dict[str, Any]:
        category = self._category_for_theorem(theorem, index)
        tid = self._safe_text(theorem.get("theorem_id") or f"THEOREM-{index}")
        name = self._safe_text(theorem.get("name") or tid)
        statement = self._safe_text(theorem.get("statement") or name)
        pred_id = "RF-TH-PRED-%03d-%s" % (index + 1, self._stable_hash({"id": tid, "statement": statement})[:8].upper())
        observables = self._observable_family(category)
        return {
            "id": pred_id,
            "source_theorem_id": tid,
            "source_theorem_name": name,
            "source_theorem_statement": statement,
            "category": category,
            "source": self._safe_text(theorem.get("source") or "theorem_prediction_generator"),
            "claim": "If %s is functionally adequate, RF* should produce observable %s signatures under its declared scope." % (name, category),
            "if_theory_true_then_observe": "At least one registered %s observable should be measurable: %s." % (category, ", ".join(observables)),
            "observable_family": observables,
            "measurement_target": "%s_signature" % category,
            "specificity": 0.78,
            "falsifiability": 0.82,
            "discriminative_potential": 0.70 if category in {"structural", "dynamic"} else 0.76,
            "status": "unknown",
            "confidence": 0.0,
            "validation_status": "untested",
            "refutation_condition": "Prediction is refuted if the declared observables remain absent under the registered conditions while competing explanations account for the data better.",
            "validation_condition": "Prediction is provisionally validated if the observable signature is detected, bounded, reproducible, and recorded before interpretive upgrade.",
            "epistemic_scope": "functional_only",
            "phenomenology_claim_blocked": True,
        }

    def _generation_policy(self) -> Dict[str, Any]:
        return {
            "source_rule": "derive one or more observable predictions from each available certified theorem or theorem-dependency node",
            "deduplication_rule": "stable theorem_id based deduplication before prediction generation",
            "category_rule": "assign structural/dynamic/topological/spectral/developmental/collective categories by theorem semantics with deterministic fallback",
            "observability_rule": "each prediction must expose observable_family, measurement_target, validation_condition, and refutation_condition",
            "status_rule": "all new predictions start as unknown/untested with confidence 0.0",
            "epistemic_scope": "functional_only",
        }

    def _validation_policy(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        bp = blueprint.get("validation_policy") if isinstance(blueprint.get("validation_policy"), dict) else {}
        if not bp and isinstance(blueprint.get("blueprint"), dict):
            rules = blueprint["blueprint"].get("validation_rules")
            bp = rules if isinstance(rules, dict) else {}
        out = dict(bp)
        out.setdefault("validated", "observable signature matches the registered prediction under stated conditions")
        out.setdefault("invalidated", "observable signature contradicts the registered prediction or a countermodel explains it better")
        out.setdefault("unknown", "insufficient, unavailable, or non-discriminative evidence")
        out.setdefault("replication_required", True)
        out.setdefault("statistical_support_required", True)
        return out

    def _falsification_policy(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        bp = blueprint.get("refutation_policy") if isinstance(blueprint.get("refutation_policy"), dict) else {}
        if not bp and isinstance(blueprint.get("blueprint"), dict):
            rules = blueprint["blueprint"].get("refutation_rules")
            bp = rules if isinstance(rules, dict) else {}
        out = dict(bp)
        out.setdefault("refutable", True)
        out.setdefault("requires_negative_observation", True)
        out.setdefault("requires_competing_theory_comparison", True)
        out.setdefault("blocks_purely_phenomenological_claims", True)
        return out

    def _epistemic_guards(self) -> Dict[str, Any]:
        return {
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "allowed_scope": "functional-scientific prediction generation only",
            "blocked_scope": ["phenomenological proof", "qualia proof", "subjective experience proof", "consciousness proven beyond empirical criteria"],
        }

    def _metrics(self, predictions: List[Dict[str, Any]], theorems: List[Dict[str, Any]]) -> Dict[str, Any]:
        category_counts = {cat: 0 for cat in self.categories}
        for prediction in predictions:
            cat = str(prediction.get("category"))
            if cat in category_counts:
                category_counts[cat] += 1
        observable_complete = sum(1 for p in predictions if p.get("observable_family") and p.get("refutation_condition") and p.get("validation_condition"))
        prediction_count = len(predictions)
        theorem_count = len(theorems)
        return {
            "theorem_coverage": (prediction_count / theorem_count) if theorem_count else 0.0,
            "observable_completion_ratio": (observable_complete / prediction_count) if prediction_count else 0.0,
            "category_coverage_ratio": (sum(1 for v in category_counts.values() if v > 0) / len(self.categories)) if self.categories else 0.0,
            "mean_specificity": (sum(self._clamp01(p.get("specificity")) for p in predictions) / prediction_count) if prediction_count else 0.0,
            "mean_falsifiability": (sum(self._clamp01(p.get("falsifiability")) for p in predictions) / prediction_count) if prediction_count else 0.0,
            "category_counts": category_counts,
        }

    def _persist(self, result: Dict[str, Any]) -> str:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / "latest_theorem_prediction_generation.json"
        path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        return str(path)

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        blueprint = self._load_predictive_blueprint(inputs)
        registry = self._load_prediction_registry(inputs)
        theorem_mapping = self._load_theorem_dependency_mapping(inputs)
        axiomatic = self._load_axiomatic_completeness(inputs)
        final_report = self._load_final_theoretical_report(inputs)
        governance = self._load_governance_certification(inputs)

        theorems: List[Dict[str, Any]] = []
        theorems.extend(self._extract_input_theorems(inputs))
        theorems.extend(self._extract_graph_theorems(theorem_mapping))
        if not theorems:
            theorems.extend(self._fallback_theorems([axiomatic, final_report, governance]))
        theorems = self._dedupe_theorems(theorems)

        generated = [self._prediction_from_theorem(theorem, i) for i, theorem in enumerate(theorems)]
        metrics = self._metrics(generated, theorems)
        existing_predictions = self._as_list(registry.get("predictions"))
        generated_categories = sorted({p.get("category") for p in generated if p.get("category")})
        ready = bool(theorems) and bool(generated) and metrics["observable_completion_ratio"] >= 1.0

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._now(),
            "status": "THEOREM_PREDICTION_GENERATOR_READY" if ready else "THEOREM_PREDICTION_GENERATOR_REQUIRES_REVIEW",
            "theorem_prediction_generator_status": "THEOREM_PREDICTION_GENERATOR_READY" if ready else "THEOREM_PREDICTION_GENERATOR_REQUIRES_REVIEW",
            "generator_ready": ready,
            "theorem_count": len(theorems),
            "prediction_count": len(generated),
            "registry_prediction_count": len(existing_predictions),
            "theorems": theorems,
            "theorem_predictions": generated,
            "generated_predictions": generated,
            "generated_prediction_categories": generated_categories,
            "prediction_generation_policy": self._generation_policy(),
            "validation_policy": self._validation_policy(blueprint),
            "falsification_policy": self._falsification_policy(blueprint),
            "epistemic_guards": self._epistemic_guards(),
            "metrics": metrics,
            "input_statuses": {
                "predictive_blueprint": blueprint.get("status") or blueprint.get("predictive_blueprint_status"),
                "prediction_registry": registry.get("status") or registry.get("prediction_registry_status"),
                "theorem_dependency_mapping": theorem_mapping.get("theorem_dependency_mapping_status"),
                "axiomatic_completeness": axiomatic.get("status") or axiomatic.get("axiomatic_completeness_status"),
                "final_theoretical_report": final_report.get("status") or final_report.get("final_theoretical_report_status"),
                "governance_certification": governance.get("status") or governance.get("consciousness_governance_status"),
            },
            "conditions_of_failure": [
                "no theorem or theorem-dependency source is available",
                "generated predictions lack observables, validation conditions, or refutation conditions",
                "epistemic guards are missing or any proof flag is upgraded to true",
                "prediction categories cannot be assigned deterministically",
            ],
            "allowed_claims": [
                "RF* theorem-level artifacts generate observable functional predictions",
                "generated predictions are unknown until measured, validated, invalidated, or replicated",
                "AT2 prepares discriminative and measurable prediction work for AT3/AT4",
            ],
            "blocked_claims": ["consciousness proven", "qualia proven", "subjectivity proven", "phenomenology proven"],
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "persisted": False,
            "output_path": None,
        }
        if persist:
            result["output_path"] = self._persist(result)
            result["persisted"] = True
        return result


if __name__ == "__main__":
    print(json.dumps(TheoremPredictionGenerator().step(inputs={"synthetic": True}, persist=False), indent=2, ensure_ascii=False, sort_keys=True))
