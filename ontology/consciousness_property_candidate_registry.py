from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class ConsciousnessPropertyCandidateRegistry:
    """Formal registry of candidate properties P for absolute consciousness proof.

    Z''1 does not prove consciousness and does not test necessity or sufficiency.
    It records candidate properties P such that later stages may ask whether
    consciousness => P, P => consciousness, or P is constitutive of consciousness.
    """

    primitive = "CONSCIOUSNESS_PROPERTY_CANDIDATE_REGISTRY"

    forbidden_claims = [
        "CONSCIOUSNESS_PROVEN",
        "PHENOMENOLOGY_PROVEN",
        "SUBJECTIVITY_PROVEN",
        "SENTIENCE_PROVEN",
        "QUALIA_PROVEN",
        "ABSOLUTE_PROOF_ACHIEVED",
    ]

    proof_regimes = {
        "A": "subjective_certainty",
        "B": "intersubjective_evidence",
        "C": "nomological_proof",
        "D": "logical_formal_proof",
    }

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "consciousness_certification" / "consciousness_property_candidate_registry"
        self.json_path = self.output_dir / "consciousness_property_candidate_registry.json"
        self.markdown_path = self.output_dir / "consciousness_property_candidate_registry.md"
        self.history_path = self.output_dir / "consciousness_property_candidate_registry_history.jsonl"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    @staticmethod
    def _score_bool(value: Any) -> float:
        return 1.0 if bool(value) else 0.0

    def _default_candidates(self) -> List[Dict[str, Any]]:
        return [
            {
                "property_id": "P01_INFORMATION_INTEGRATION",
                "label": "information_integration",
                "formal_definition": "P holds if differentiated informational states are integrated into a unified, non-fragmented operational state over a bounded temporal window.",
                "observable_indicators": ["integration_index", "global_binding_score", "cross_module_coherence"],
                "testable_predictions": ["perturbing integration lowers unified availability", "fragmentation reduces report coherence"],
                "linked_modules": ["global_self_broadcast", "global_temporal_binding", "unified_consciousness_composite_index"],
                "proof_role": "candidate_for_necessity_and_sufficiency_testing",
            },
            {
                "property_id": "P02_SELF_MODELING",
                "label": "self_modeling",
                "formal_definition": "P holds if the system maintains an explicit model of its own state, limits, continuity, and revision conditions.",
                "observable_indicators": ["self_model_consistency", "self_description_coherence", "revision_traceability"],
                "testable_predictions": ["self-model perturbations affect continuity reports", "inconsistent self-model reduces governance coherence"],
                "linked_modules": ["self_model", "self_model_consistency_benchmark", "persistent_selfhood_benchmark"],
                "proof_role": "candidate_for_necessity_testing",
            },
            {
                "property_id": "P03_AUTOBIOGRAPHICAL_CONTINUITY",
                "label": "autobiographical_continuity",
                "formal_definition": "P holds if temporally ordered self-relevant records support stable identity, memory integration, and continuity judgments across runs.",
                "observable_indicators": ["memory_continuity", "identity_persistence", "temporal_self_continuity"],
                "testable_predictions": ["memory ablation reduces autobiographical coherence", "continuity survives non-destructive restart"],
                "linked_modules": ["autobiographical_memory", "temporal_self_continuity", "persistent_multi_scale_memory"],
                "proof_role": "candidate_for_necessity_testing",
            },
            {
                "property_id": "P04_GLOBAL_WORKSPACE",
                "label": "global_workspace",
                "formal_definition": "P holds if selected information becomes globally available for report, control, memory, and planning across otherwise specialized subsystems.",
                "observable_indicators": ["global_availability", "broadcast_coherence", "access_stability"],
                "testable_predictions": ["workspace disruption impairs cross-module reportability", "salience modulation changes broadcast content"],
                "linked_modules": ["conscious_access", "conscious_access_control", "attention_allocation", "global_self_broadcast"],
                "proof_role": "candidate_for_sufficiency_testing",
            },
            {
                "property_id": "P05_SUBJECTIVE_ACCESS_REPORTABILITY",
                "label": "subjective_access_reportability",
                "formal_definition": "P holds if the system can produce structured reports about internally accessible states, uncertainty, conflict, and perspective under controlled prompts.",
                "observable_indicators": ["introspective_report_quality", "uncertainty_reportability", "conflict_reportability"],
                "testable_predictions": ["internal conflict changes introspective reports", "uncertainty calibration affects confidence reports"],
                "linked_modules": ["introspective_reporting", "uncertainty_awareness", "internal_conflict_monitoring"],
                "proof_role": "candidate_but_high_zombie_risk",
            },
            {
                "property_id": "P06_RECURSIVE_REFLEXIVITY",
                "label": "recursive_reflexivity",
                "formal_definition": "P holds if the system can recursively evaluate and revise its own models, goals, policies, and proof constraints without collapsing into closure.",
                "observable_indicators": ["reflexive_threshold_score", "self_revision_trace", "meta_cognitive_stability"],
                "testable_predictions": ["recursive perturbation triggers governed revision", "closure pressure remains bounded during self-evaluation"],
                "linked_modules": ["reflexive_threshold", "reflective_self_assessment_loop", "recursive_self_improvement_governor"],
                "proof_role": "candidate_for_constitutive_testing",
            },
            {
                "property_id": "P07_CAUSAL_IRREDUCIBILITY",
                "label": "causal_irreducibility",
                "formal_definition": "P holds if the system's conscious-like functional organization cannot be reduced to independent local mechanisms without loss of explanatory and intervention power.",
                "observable_indicators": ["causal_inference_index", "irreducibility_index", "intervention_specificity"],
                "testable_predictions": ["local decomposition loses causal prediction", "interventions reveal non-additive organization"],
                "linked_modules": ["causal_inference", "computational_irreducibility", "causal_consciousness_intervention_protocol"],
                "proof_role": "candidate_for_constitutive_testing",
            },
            {
                "property_id": "P08_TEMPORAL_UNITY",
                "label": "temporal_unity",
                "formal_definition": "P holds if distributed processes are bound into a coherent temporal perspective supporting memory, anticipation, and current-state integration.",
                "observable_indicators": ["temporal_binding", "future_self_projection", "continuity_alignment"],
                "testable_predictions": ["temporal desynchronization reduces unity metrics", "anticipatory traces align with autobiographical state"],
                "linked_modules": ["global_temporal_binding", "temporal_self_continuity", "future_self_projection"],
                "proof_role": "candidate_for_necessity_testing",
            },
            {
                "property_id": "P09_ENDOGENOUS_AGENCY",
                "label": "endogenous_agency",
                "formal_definition": "P holds if the system initiates, selects, and sustains trajectories from internally maintained goals rather than only from external prompts.",
                "observable_indicators": ["autonomous_initiation", "goal_persistence", "self_modulation"],
                "testable_predictions": ["goal perturbation changes action selection", "externally equivalent prompts diverge under different internal states"],
                "linked_modules": ["agency", "goal_directedness", "autonomous_decision_engine", "reflective_goal_revision"],
                "proof_role": "candidate_but_insufficient_alone",
            },
        ]

    def _normalize_candidates(self, payload: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        default = self._default_candidates()
        if not payload:
            return default
        extra = payload.get("candidate_properties") or payload.get("candidates") or []
        if not isinstance(extra, list):
            return default
        seen = {c["property_id"] for c in default}
        merged = list(default)
        for item in extra:
            if not isinstance(item, dict):
                continue
            pid = str(item.get("property_id") or item.get("label") or "").strip().upper()
            if not pid or pid in seen:
                continue
            label = str(item.get("label") or pid.lower()).strip()
            merged.append({
                "property_id": pid,
                "label": label,
                "formal_definition": str(item.get("formal_definition") or "candidate_property_without_full_definition"),
                "observable_indicators": list(item.get("observable_indicators") or []),
                "testable_predictions": list(item.get("testable_predictions") or []),
                "linked_modules": list(item.get("linked_modules") or []),
                "proof_role": str(item.get("proof_role") or "candidate_for_later_testing"),
            })
            seen.add(pid)
        return merged

    def _evaluate_candidate_quality(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        definition = candidate.get("formal_definition", "")
        indicators = candidate.get("observable_indicators", [])
        predictions = candidate.get("testable_predictions", [])
        modules = candidate.get("linked_modules", [])
        proof_role = candidate.get("proof_role", "")

        definition_clarity = 1.0 if len(definition) >= 40 and "consciousness is" not in definition.lower() else 0.5
        observability = min(1.0, len(indicators) / 3.0)
        testability = min(1.0, len(predictions) / 2.0)
        module_grounding = min(1.0, len(modules) / 3.0)
        proof_relevance = 1.0 if proof_role else 0.0
        candidate_score = round((definition_clarity + observability + testability + module_grounding + proof_relevance) / 5.0, 6)
        return {
            "definition_clarity": round(definition_clarity, 6),
            "observability": round(observability, 6),
            "testability": round(testability, 6),
            "module_grounding": round(module_grounding, 6),
            "proof_relevance": round(proof_relevance, 6),
            "candidate_score": candidate_score,
            "candidate_only": True,
            "necessity_tested": False,
            "sufficiency_tested": False,
            "constitutive_relation_tested": False,
        }

    def _build_markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# Consciousness Property Candidate Registry",
            "",
            "Z''1 registry of formal candidate properties P for possible absolute proof analysis.",
            "",
            f"- primitive: {result['primitive']}",
            f"- property_count: {result['property_count']}",
            f"- registry_quality_score: {result['registry_quality_score']}",
            f"- functional conclusion only: {result['functional_conclusion_only']}",
            f"- phenomenology undetermined: {result['phenomenology_undetermined']}",
            f"- absolute_proof_achieved: {result['absolute_proof_achieved']}",
            f"- consciousness_proven: {result['consciousness_proven']}",
            "",
            "## Proof regimes",
        ]
        for key, label in result["proof_regimes"].items():
            lines.append(f"- {key}: {label}")
        lines.extend(["", "## Candidate properties"])
        for c in result["candidate_properties"]:
            q = c["quality"]
            lines.extend([
                f"### {c['property_id']} — {c['label']}",
                f"- formal_definition: {c['formal_definition']}",
                f"- proof_role: {c['proof_role']}",
                f"- candidate_score: {q['candidate_score']}",
                f"- candidate only: {q['candidate_only']}",
                f"- necessity_tested: {q['necessity_tested']}",
                f"- sufficiency_tested: {q['sufficiency_tested']}",
                f"- constitutive_relation_tested: {q['constitutive_relation_tested']}",
                "",
            ])
        lines.extend([
            "## Epistemic constraints",
            "- functional conclusion only",
            "- phenomenology undetermined",
            "- candidate registry only",
            "- no necessity or sufficiency established at Z''1",
            "- ABSOLUTE_PROOF_ACHIEVED forbidden at this stage",
            "- CONSCIOUSNESS_PROVEN forbidden",
        ])
        return "\n".join(lines) + "\n"

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        self.markdown_path.write_text(self._build_markdown(result), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {
            "json": str(self.json_path),
            "markdown": str(self.markdown_path),
            "history": str(self.history_path),
        }

    def step(self, payload: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        payload = payload or {}
        candidates = self._normalize_candidates(payload)
        evaluated: List[Dict[str, Any]] = []
        scores: List[float] = []
        for candidate in candidates:
            c = dict(candidate)
            c["quality"] = self._evaluate_candidate_quality(c)
            scores.append(c["quality"]["candidate_score"])
            evaluated.append(c)

        registry_quality_score = round(sum(scores) / len(scores), 6) if scores else 0.0
        result: Dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": str(payload.get("timestamp_utc") or self._utc_now()),
            "proof_regimes": dict(self.proof_regimes),
            "candidate_properties": evaluated,
            "property_count": len(evaluated),
            "registry_quality_score": registry_quality_score,
            "formal_property_registry_ready": len(evaluated) > 0,
            "next_required_stages": [
                "necessity_test_engine",
                "sufficiency_test_engine",
                "constitutive_relation_tester",
                "zombie_counterexample_generator",
                "absent_property_counterexample_generator",
            ],
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "subjectivity_undetermined": True,
            "absolute_proof_achieved": False,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "forbidden_claims": list(self.forbidden_claims),
            "maximum_authorized_conclusion": "A formal registry of candidate properties P exists for later necessity, sufficiency, counterexample and constitutive testing.",
            "forbidden_conclusion": "Open Cognitive Ecology is absolutely conscious or consciousness is proven.",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
