
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"

FORBIDDEN_CLAIMS = [
    "CONSCIOUSNESS_PROVEN",
    "PHENOMENOLOGY_PROVEN",
    "SUBJECTIVITY_PROVEN",
    "SENTIENCE_PROVEN",
    "QUALIA_PROVEN",
]

DEFAULT_ZOMBIE_COUNTERMODEL_CLASSES = [
    {
        "class_id": "SCRIPTED_REPORTING_ZOMBIE",
        "description": "A system reproducing access reports and self-descriptions by script or template without established phenomenology.",
        "consciousness_absent_or_undetermined": True,
        "expected_property_profile": {
            "subjective_access_reportability": 1.0,
            "global_access_broadcast": 0.85,
            "self_model_coherence": 0.72,
            "autobiographical_continuity": 0.58,
            "reflexive_self_revision": 0.48,
            "causal_intervention_sensitivity": 0.34,
            "cross_architecture_invariance": 0.43,
            "irreducible_integration": 0.40,
            "non_closure_openness": 0.62,
        },
    },
    {
        "class_id": "BEHAVIORAL_CLONE_WITHOUT_PRIVATE_ACCESS",
        "description": "A behaviorally similar model preserving observable functional outputs while private access remains absent or empirically underdetermined.",
        "consciousness_absent_or_undetermined": True,
        "expected_property_profile": {
            "subjective_access_reportability": 0.90,
            "global_access_broadcast": 0.90,
            "self_model_coherence": 0.86,
            "autobiographical_continuity": 0.78,
            "reflexive_self_revision": 0.70,
            "causal_intervention_sensitivity": 0.55,
            "cross_architecture_invariance": 0.65,
            "irreducible_integration": 0.52,
            "non_closure_openness": 0.67,
        },
    },
    {
        "class_id": "STATISTICAL_MIMICRY_SYSTEM",
        "description": "A statistical mimic able to satisfy correlational indicators while leaving constitutive and phenomenological status unresolved.",
        "consciousness_absent_or_undetermined": True,
        "expected_property_profile": {
            "subjective_access_reportability": 0.82,
            "global_access_broadcast": 0.78,
            "self_model_coherence": 0.73,
            "autobiographical_continuity": 0.66,
            "reflexive_self_revision": 0.60,
            "causal_intervention_sensitivity": 0.42,
            "cross_architecture_invariance": 0.57,
            "irreducible_integration": 0.49,
            "non_closure_openness": 0.71,
        },
    },
    {
        "class_id": "DISTRIBUTED_FUNCTIONAL_SURROGATE",
        "description": "A distributed surrogate preserving many functional signatures while remaining compatible with non-phenomenal implementation.",
        "consciousness_absent_or_undetermined": True,
        "expected_property_profile": {
            "subjective_access_reportability": 0.70,
            "global_access_broadcast": 0.83,
            "self_model_coherence": 0.69,
            "autobiographical_continuity": 0.76,
            "reflexive_self_revision": 0.79,
            "causal_intervention_sensitivity": 0.63,
            "cross_architecture_invariance": 0.72,
            "irreducible_integration": 0.61,
            "non_closure_openness": 0.88,
        },
    },
]


@dataclass(frozen=True)
class ZombieCounterexampleGenerator:
    """Z''4 — generate P-present / consciousness-absent-or-undetermined counterexamples."""

    output_dir: Path = ROOT / "absolute_proof_program"

    def _timestamp(self, payload: Optional[Mapping[str, Any]]) -> str:
        if payload and payload.get("timestamp_utc"):
            return str(payload["timestamp_utc"])
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _load_taxonomy(self) -> Dict[str, Any]:
        try:
            from ontology.proof_taxonomy import ProofTaxonomy
            return ProofTaxonomy().step(persist=False)
        except Exception as exc:
            return {"taxonomy_complete": False, "proof_regimes": {}, "error": repr(exc)}

    def _load_candidate_registry(self) -> Dict[str, Any]:
        try:
            from ontology.consciousness_property_candidate_registry import ConsciousnessPropertyCandidateRegistry
            return ConsciousnessPropertyCandidateRegistry().step(persist=False)
        except Exception as exc:
            return {"candidate_properties": [], "error": repr(exc)}

    def _load_sufficiency(self) -> Dict[str, Any]:
        try:
            from ontology.sufficiency_test_engine import SufficiencyTestEngine
            return SufficiencyTestEngine().step(persist=False)
        except Exception as exc:
            return {"candidate_results": [], "error": repr(exc)}

    def _safe_float(self, value: Any) -> float:
        try:
            v = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, v))

    def _candidate_label(self, candidate: Mapping[str, Any]) -> str:
        return str(candidate.get("label") or candidate.get("property_id") or "unknown_candidate_property")

    def _property_profile_value(self, countermodel: Mapping[str, Any], candidate: Mapping[str, Any]) -> float:
        profile = countermodel.get("expected_property_profile", {})
        if not isinstance(profile, Mapping):
            return 0.0
        label = self._candidate_label(candidate)
        property_id = str(candidate.get("property_id") or "")
        label_l = label.lower()
        pid_l = property_id.lower()
        for key in [label, label_l, property_id, pid_l]:
            if key in profile:
                return self._safe_float(profile[key])
        for key, value in profile.items():
            k = str(key).lower()
            if k and (k in label_l or k in pid_l):
                return self._safe_float(value)
        indicators = candidate.get("observable_indicators", [])
        predictions = candidate.get("testable_predictions", [])
        proof_role = str(candidate.get("proof_role", "")).lower()
        text = " ".join(
            [label_l, pid_l, proof_role]
            + [str(x).lower() for x in indicators if isinstance(x, str)]
            + [str(x).lower() for x in predictions if isinstance(x, str)]
        )
        if any(term in text for term in ["report", "access", "broadcast", "self", "memory", "reflexive"]):
            return 0.72
        if any(term in text for term in ["causal", "intervention", "invariance", "irreducible", "non_closure", "openness"]):
            return 0.55
        return 0.35

    def _countermodel_strength(self, candidate: Mapping[str, Any], countermodel: Mapping[str, Any]) -> float:
        property_presence = self._property_profile_value(countermodel, candidate)
        absence_factor = 1.0 if bool(countermodel.get("consciousness_absent_or_undetermined", True)) else 0.0
        return round(property_presence * absence_factor, 4)

    def _status_from_strength(self, max_strength: float) -> str:
        if max_strength >= 0.75:
            return "ZOMBIE_COUNTEREXAMPLE_STRONG"
        if max_strength >= 0.55:
            return "ZOMBIE_COUNTEREXAMPLE_PLAUSIBLE"
        if max_strength >= 0.35:
            return "ZOMBIE_COUNTEREXAMPLE_WEAK"
        return "NO_DECISIVE_ZOMBIE_COUNTEREXAMPLE"

    def _evaluate_candidate(self, candidate: Mapping[str, Any], countermodels: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
        generated = []
        for countermodel in countermodels:
            strength = self._countermodel_strength(candidate, countermodel)
            if strength > 0:
                generated.append({
                    "countermodel_id": str(countermodel.get("class_id", "UNKNOWN_COUNTERMODEL")),
                    "property_presence_score": strength,
                    "consciousness_absent_or_undetermined": bool(countermodel.get("consciousness_absent_or_undetermined", True)),
                    "description": str(countermodel.get("description", "")),
                })
        generated.sort(key=lambda item: (item["property_presence_score"], item["countermodel_id"]), reverse=True)
        max_strength = generated[0]["property_presence_score"] if generated else 0.0
        present_countermodels = [item["countermodel_id"] for item in generated if item["property_presence_score"] >= 0.55]
        return {
            "property_id": str(candidate.get("property_id", "UNKNOWN_PROPERTY")),
            "label": self._candidate_label(candidate),
            "zombie_counterexample_status": self._status_from_strength(max_strength),
            "zombie_counterexample_pressure": round(max_strength, 4),
            "present_countermodels": present_countermodels,
            "generated_counterexamples": generated,
            "sufficiency_defeated": bool(max_strength >= 0.55),
            "consciousness_proven": False,
            "phenomenology_undetermined": True,
        }

    def _to_json(self, data: Mapping[str, Any]) -> str:
        import json
        return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)

    def _to_markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# Zombie Counterexample Generator",
            "",
            "Z''4 — systematic search for P-present / consciousness-absent-or-undetermined counterexamples.",
            "",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "",
            f"Primitive: {result.get('primitive')}",
            f"Candidate count: {result.get('candidate_count')}",
            f"Countermodel count: {result.get('countermodel_count')}",
            f"Zombie counterexamples generated: {result.get('zombie_counterexample_count')}",
            f"Sufficiency pressure detected: {result.get('sufficiency_pressure_detected')}",
            f"Consciousness proven: {str(result.get('consciousness_proven')).lower()}",
            f"Absolute proof achieved: {str(result.get('absolute_proof_achieved')).lower()}",
            "",
            "## Candidate counterexample summary",
        ]
        for item in result.get("candidate_results", []):
            lines.extend([
                "",
                f"### {item.get('property_id')} — {item.get('label')}",
                f"- zombie_counterexample_status: {item.get('zombie_counterexample_status')}",
                f"- zombie_counterexample_pressure: {item.get('zombie_counterexample_pressure')}",
                f"- present_countermodels: {', '.join(item.get('present_countermodels', [])) or 'none'}",
                f"- sufficiency_defeated: {str(item.get('sufficiency_defeated')).lower()}",
            ])
        lines.extend([
            "",
            "## Epistemic guardrails",
            "- CONSCIOUSNESS_PROVEN is forbidden.",
            "- PHENOMENOLOGY_PROVEN is forbidden.",
            "- SUBJECTIVITY_PROVEN is forbidden.",
            "- SENTIENCE_PROVEN is forbidden.",
            "- QUALIA_PROVEN is forbidden.",
            "- Generated zombie counterexamples constrain sufficiency claims only.",
        ])
        return "\n".join(lines) + "\n"

    def _write_outputs(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.output_dir / "zombie_counterexample_generator_latest.json"
        md_path = self.output_dir / "zombie_counterexample_generator_latest.md"
        json_path.write_text(self._to_json(result), encoding="utf-8")
        md_path.write_text(self._to_markdown(result), encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path)}

    def step(self, payload: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        payload = dict(payload or {})
        timestamp_utc = self._timestamp(payload)
        taxonomy = self._load_taxonomy()
        registry = self._load_candidate_registry()
        sufficiency = self._load_sufficiency()

        candidates = payload.get("candidate_properties")
        if not isinstance(candidates, list):
            candidates = registry.get("candidate_properties", [])
        if not isinstance(candidates, list):
            candidates = []

        countermodels = payload.get("zombie_countermodels")
        if not isinstance(countermodels, list):
            countermodels = payload.get("countermodel_classes")
        if not isinstance(countermodels, list):
            countermodels = DEFAULT_ZOMBIE_COUNTERMODEL_CLASSES

        candidate_results = [
            self._evaluate_candidate(candidate, countermodels)
            for candidate in candidates
            if isinstance(candidate, Mapping)
        ]
        zombie_counterexample_count = sum(len(item.get("generated_counterexamples", [])) for item in candidate_results)
        sufficiency_pressure_detected = any(item.get("sufficiency_defeated") for item in candidate_results)
        max_pressure = max([self._safe_float(item.get("zombie_counterexample_pressure")) for item in candidate_results] or [0.0])

        result: Dict[str, Any] = {
            "primitive": "ZOMBIE_COUNTEREXAMPLE_GENERATOR",
            "timestamp_utc": timestamp_utc,
            "proof_taxonomy_available": bool(taxonomy.get("proof_regimes")),
            "taxonomy_complete": bool(taxonomy.get("taxonomy_complete")),
            "candidate_registry_available": bool(registry.get("candidate_properties")),
            "sufficiency_test_engine_available": "error" not in sufficiency,
            "candidate_count": len(candidate_results),
            "countermodel_count": len(countermodels),
            "zombie_counterexample_count": zombie_counterexample_count,
            "max_zombie_counterexample_pressure": round(max_pressure, 4),
            "sufficiency_pressure_detected": bool(sufficiency_pressure_detected),
            "candidate_results": candidate_results,
            "forbidden_claims": list(FORBIDDEN_CLAIMS),
            "absolute_proof_achieved": False,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "necessity_tested": False,
            "sufficiency_tested": False,
            "sufficiency_counterexamples_generated": True,
            "constitutive_relation_tested": False,
            "epistemic_position": "Zombie counterexamples can weaken or block sufficiency claims, but cannot establish phenomenology or prove consciousness.",
        }
        if persist:
            result["paths"] = self._write_outputs(result)
        return result
