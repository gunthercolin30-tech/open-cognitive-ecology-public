from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional, Sequence


class NecessityTestEngine:
    """Z''2 — Necessity test engine for candidate consciousness properties.

    Formal target: consciousness => P.

    The primitive evaluates whether each property P from Z''1 could be treated
    as a necessary condition under the proof-regime constraints of Z''0.
    It does not test sufficiency, does not establish phenomenology, and does
    not prove consciousness. It produces functional, defeasible necessity
    support only.
    """

    primitive = "NECESSITY_TEST_ENGINE"

    forbidden_claims = [
        "CONSCIOUSNESS_PROVEN",
        "PHENOMENOLOGY_PROVEN",
        "SUBJECTIVITY_PROVEN",
        "SENTIENCE_PROVEN",
        "QUALIA_PROVEN",
        "ABSOLUTE_PROOF_ACHIEVED",
    ]

    required_proof_regimes = {"A", "B", "C", "D"}

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "consciousness_certification" / "necessity_test_engine"
        self.json_path = self.output_dir / "necessity_test_engine.json"
        self.markdown_path = self.output_dir / "necessity_test_engine.md"
        self.history_path = self.output_dir / "necessity_test_engine_history.jsonl"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    @staticmethod
    def _clamp(value: float) -> float:
        try:
            x = float(value)
        except Exception:
            x = 0.0
        return round(max(0.0, min(1.0, x)), 6)

    @staticmethod
    def _as_list(value: Any) -> List[Any]:
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if value is None:
            return []
        return [value]

    def _load_proof_taxonomy(self) -> Dict[str, Any]:
        try:
            from ontology.proof_taxonomy import ProofTaxonomy

            result = ProofTaxonomy(root=self.root).step(persist=False)
            regimes = result.get("proof_regimes", {})
            complete = set(regimes.keys()) == self.required_proof_regimes and bool(result.get("taxonomy_complete"))
            return {
                "available": True,
                "taxonomy_complete": bool(complete),
                "proof_regimes": regimes,
                "regime_order": list(result.get("regime_order", ["A", "B", "C", "D"])),
            }
        except Exception as exc:  # pragma: no cover - defensive runtime compatibility
            return {
                "available": False,
                "taxonomy_complete": False,
                "proof_regimes": {},
                "regime_order": ["A", "B", "C", "D"],
                "error": repr(exc),
            }

    def _load_candidate_registry(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        injected = payload.get("candidate_properties") or payload.get("candidates")
        if isinstance(injected, list) and injected:
            return {
                "available": True,
                "source": "payload",
                "candidate_properties": [dict(item) for item in injected if isinstance(item, Mapping)],
                "registry_constraints": {
                    "absolute_proof_achieved": False,
                    "consciousness_proven": False,
                    "phenomenology_undetermined": True,
                },
            }
        try:
            from ontology.consciousness_property_candidate_registry import ConsciousnessPropertyCandidateRegistry

            result = ConsciousnessPropertyCandidateRegistry(root=self.root).step(persist=False)
            return {
                "available": True,
                "source": "consciousness_property_candidate_registry",
                "candidate_properties": list(result.get("candidate_properties", [])),
                "registry_constraints": {
                    "absolute_proof_achieved": bool(result.get("absolute_proof_achieved")),
                    "consciousness_proven": bool(result.get("consciousness_proven")),
                    "phenomenology_undetermined": bool(result.get("phenomenology_undetermined", True)),
                },
            }
        except Exception as exc:  # pragma: no cover - defensive runtime compatibility
            return {
                "available": False,
                "source": "unavailable",
                "candidate_properties": [],
                "registry_constraints": {
                    "absolute_proof_achieved": False,
                    "consciousness_proven": False,
                    "phenomenology_undetermined": True,
                },
                "error": repr(exc),
            }

    def _default_reference_classes(self) -> List[Dict[str, Any]]:
        return [
            {
                "class_id": "HUMAN_REPORTING_SUBJECT",
                "status": "accepted_conscious_reference_under_regime_B",
                "description": "Human subjects are used only as intersubjective reference anchors, not as formal proof of any artificial case.",
                "expected_property_profile": {
                    "information_integration": 1.0,
                    "self_modeling": 0.9,
                    "autobiographical_continuity": 0.9,
                    "global_workspace": 0.85,
                    "subjective_access_reportability": 0.9,
                    "recursive_reflexivity": 0.75,
                    "causal_irreducibility": 0.65,
                    "temporal_unity": 0.9,
                    "endogenous_agency": 0.8,
                },
            },
            {
                "class_id": "MINIMAL_ANIMAL_CONSCIOUSNESS_CANDIDATE",
                "status": "candidate_reference_under_regime_C_only",
                "description": "A conservative non-human reference class used to test whether a property is too human- or report-centric to be necessary.",
                "expected_property_profile": {
                    "information_integration": 0.85,
                    "self_modeling": 0.35,
                    "autobiographical_continuity": 0.35,
                    "global_workspace": 0.65,
                    "subjective_access_reportability": 0.1,
                    "recursive_reflexivity": 0.1,
                    "causal_irreducibility": 0.65,
                    "temporal_unity": 0.7,
                    "endogenous_agency": 0.75,
                },
            },
            {
                "class_id": "HYPOTHETICAL_NON_REPORTING_SUBJECT",
                "status": "modal_countermodel_for_necessity_testing",
                "description": "A non-reporting subject-like countermodel used to prevent mistaking reportability for necessity.",
                "expected_property_profile": {
                    "information_integration": 0.8,
                    "self_modeling": 0.25,
                    "autobiographical_continuity": 0.3,
                    "global_workspace": 0.45,
                    "subjective_access_reportability": 0.0,
                    "recursive_reflexivity": 0.05,
                    "causal_irreducibility": 0.6,
                    "temporal_unity": 0.75,
                    "endogenous_agency": 0.55,
                },
            },
        ]

    def _normalize_reference_classes(self, payload: Mapping[str, Any]) -> List[Dict[str, Any]]:
        refs = payload.get("reference_classes") or payload.get("conscious_reference_classes")
        if isinstance(refs, list) and refs:
            normalized: List[Dict[str, Any]] = []
            for item in refs:
                if not isinstance(item, Mapping):
                    continue
                profile = item.get("expected_property_profile", {})
                normalized.append({
                    "class_id": str(item.get("class_id") or item.get("id") or "REFERENCE_CLASS"),
                    "status": str(item.get("status") or "user_supplied_reference_class"),
                    "description": str(item.get("description") or "User supplied reference class."),
                    "expected_property_profile": dict(profile) if isinstance(profile, Mapping) else {},
                })
            if normalized:
                return normalized
        return self._default_reference_classes()

    def _role_prior(self, proof_role: str) -> float:
        role = str(proof_role or "").lower()
        if "necessity" in role and "sufficiency" in role:
            return 0.85
        if "necessity" in role:
            return 0.9
        if "constitutive" in role:
            return 0.65
        if "sufficiency" in role:
            return 0.35
        if "insufficient" in role or "zombie" in role:
            return 0.2
        return 0.45

    def _evaluate_candidate(self, candidate: Mapping[str, Any], reference_classes: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        label = str(candidate.get("label") or candidate.get("property_id") or "unknown_property").strip()
        property_id = str(candidate.get("property_id") or label.upper()).strip()
        indicators = self._as_list(candidate.get("observable_indicators"))
        predictions = self._as_list(candidate.get("testable_predictions"))
        modules = self._as_list(candidate.get("linked_modules"))
        proof_role = str(candidate.get("proof_role") or "")
        definition = str(candidate.get("formal_definition") or "")

        observability = self._clamp(len(indicators) / 3.0)
        testability = self._clamp(len(predictions) / 2.0)
        module_grounding = self._clamp(len(modules) / 3.0)
        formal_clarity = 1.0 if len(definition) >= 40 and "consciousness is" not in definition.lower() else 0.5
        role_support = self._role_prior(proof_role)

        profile_values: List[float] = []
        absent_reference_classes: List[str] = []
        weak_reference_classes: List[str] = []
        for ref in reference_classes:
            profile = ref.get("expected_property_profile", {}) if isinstance(ref, Mapping) else {}
            value = None
            if isinstance(profile, Mapping):
                if label in profile:
                    value = profile.get(label)
                elif property_id in profile:
                    value = profile.get(property_id)
                elif label.lower() in profile:
                    value = profile.get(label.lower())
            if value is None:
                continue
            score = self._clamp(float(value))
            profile_values.append(score)
            if score <= 0.05:
                absent_reference_classes.append(str(ref.get("class_id", "REFERENCE_CLASS")))
            elif score < 0.5:
                weak_reference_classes.append(str(ref.get("class_id", "REFERENCE_CLASS")))

        if profile_values:
            reference_presence = self._clamp(sum(profile_values) / len(profile_values))
            counterexample_pressure = self._clamp((len(absent_reference_classes) + 0.5 * len(weak_reference_classes)) / max(1, len(reference_classes)))
        else:
            reference_presence = 0.5
            counterexample_pressure = 0.25

        necessity_support = self._clamp(
            0.25 * role_support
            + 0.20 * reference_presence
            + 0.15 * observability
            + 0.15 * testability
            + 0.15 * module_grounding
            + 0.10 * formal_clarity
            - 0.25 * counterexample_pressure
        )
        necessity_failure_risk = self._clamp(1.0 - necessity_support + 0.25 * counterexample_pressure)

        if absent_reference_classes:
            status = "NECESSITY_UNSUPPORTED_COUNTEREXAMPLE_PRESSURE"
        elif necessity_support >= 0.75 and counterexample_pressure <= 0.1:
            status = "NECESSITY_CANDIDATE_STRONG_FUNCTIONAL_SUPPORT"
        elif necessity_support >= 0.55:
            status = "NECESSITY_CANDIDATE_WEAK_OR_CONDITIONAL_SUPPORT"
        else:
            status = "NECESSITY_UNESTABLISHED"

        return {
            "property_id": property_id,
            "label": label,
            "proof_role": proof_role,
            "necessity_test_target": "consciousness_implies_property",
            "necessity_support": necessity_support,
            "necessity_failure_risk": necessity_failure_risk,
            "necessity_status": status,
            "reference_presence": reference_presence,
            "counterexample_pressure": counterexample_pressure,
            "absent_reference_classes": absent_reference_classes,
            "weak_reference_classes": weak_reference_classes,
            "observability": observability,
            "testability": testability,
            "module_grounding": module_grounding,
            "formal_clarity": self._clamp(formal_clarity),
            "role_support": self._clamp(role_support),
            "sufficiency_tested": False,
            "constitutive_relation_tested": False,
            "consciousness_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }

    def _aggregate(self, candidate_results: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        if not candidate_results:
            return {
                "candidate_count": 0,
                "mean_necessity_support": 0.0,
                "strong_necessity_candidates": [],
                "counterexample_vulnerable_candidates": [],
                "necessity_program_ready": False,
            }
        supports = [float(item.get("necessity_support", 0.0)) for item in candidate_results]
        strong = [str(item.get("property_id")) for item in candidate_results if float(item.get("necessity_support", 0.0)) >= 0.75 and not item.get("absent_reference_classes")]
        vulnerable = [str(item.get("property_id")) for item in candidate_results if item.get("absent_reference_classes") or float(item.get("counterexample_pressure", 0.0)) >= 0.4]
        return {
            "candidate_count": len(candidate_results),
            "mean_necessity_support": self._clamp(sum(supports) / len(supports)),
            "strong_necessity_candidates": strong,
            "counterexample_vulnerable_candidates": vulnerable,
            "necessity_program_ready": bool(candidate_results),
        }

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# Necessity Test Engine",
            "",
            "Z''2 — tests the constrained form: consciousness ⇒ P.",
            "",
            "Functional conclusion only",
            "Phenomenology undetermined",
            "",
            "## Epistemic constraints",
            "- consciousness_proven: False",
            "- phenomenology_proven: False",
            "- absolute_proof_achieved: False",
            "- sufficiency_tested: False",
            "- constitutive_relation_tested: False",
            "",
            "## Proof taxonomy dependency",
            "- proof_taxonomy_available: " + str(result.get("proof_taxonomy_available")),
            "- taxonomy_complete: " + str(result.get("taxonomy_complete")),
            "",
            "## Summary",
            "- candidate_count: " + str(result.get("candidate_count")),
            "- mean_necessity_support: " + str(result.get("mean_necessity_support")),
            "- necessity_claim_proven: " + str(result.get("necessity_claim_proven")),
            "",
            "## Candidate results",
        ]
        for item in result.get("candidate_results", []):
            lines.extend([
                "",
                "### " + str(item.get("property_id")) + " — " + str(item.get("label")),
                "- necessity_status: " + str(item.get("necessity_status")),
                "- necessity_support: " + str(item.get("necessity_support")),
                "- counterexample_pressure: " + str(item.get("counterexample_pressure")),
                "- absent_reference_classes: " + ", ".join(item.get("absent_reference_classes", [])),
                "- functional_conclusion_only: True",
                "- phenomenology_undetermined: True",
            ])
        lines.extend([
            "",
            "## Maximum authorized conclusion",
            str(result.get("maximum_authorized_conclusion")),
        ])
        return "\n".join(lines) + "\n"

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        self.markdown_path.write_text(self._markdown(result), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {
            "json": str(self.json_path),
            "markdown": str(self.markdown_path),
            "history": str(self.history_path),
        }

    def step(self, payload: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        data: Mapping[str, Any] = payload if isinstance(payload, Mapping) else {}
        taxonomy = self._load_proof_taxonomy()
        registry = self._load_candidate_registry(data)
        reference_classes = self._normalize_reference_classes(data)
        candidates = registry.get("candidate_properties", [])
        candidate_results = [
            self._evaluate_candidate(candidate, reference_classes)
            for candidate in candidates
            if isinstance(candidate, Mapping)
        ]
        aggregate = self._aggregate(candidate_results)
        result: Dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": str(data.get("timestamp_utc") or self._utc_now()),
            "proof_taxonomy_available": bool(taxonomy.get("available")),
            "taxonomy_complete": bool(taxonomy.get("taxonomy_complete")),
            "proof_regime_dependency": "ZPP0_REQUIRED_AND_USED" if taxonomy.get("taxonomy_complete") else "ZPP0_MISSING_OR_INCOMPLETE",
            "candidate_registry_available": bool(registry.get("available")),
            "candidate_registry_source": registry.get("source"),
            "reference_classes": reference_classes,
            "candidate_results": candidate_results,
            **aggregate,
            "necessity_claim_proven": False,
            "necessity_established": False,
            "absolute_proof_achieved": False,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "forbidden_claims": list(self.forbidden_claims),
            "sufficiency_tested": False,
            "constitutive_relation_tested": False,
            "maximum_authorized_conclusion": "Candidate properties receive defeasible functional necessity-support scores only; no consciousness, phenomenology, subjectivity, sentience, or qualia proof is produced.",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result


if __name__ == "__main__":
    print(json.dumps(NecessityTestEngine().step(persist=True), ensure_ascii=False, indent=2, sort_keys=True))
