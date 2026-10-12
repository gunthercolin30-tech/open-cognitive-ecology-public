from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional, Sequence


class SufficiencyTestEngine:
    """Z''3 — Sufficiency test engine for candidate consciousness properties.

    Formal target: P => consciousness.

    The primitive evaluates whether each candidate property P can be treated as
    sufficient for consciousness under the proof-regime constraints of Z''0 and
    the property registry of Z''1, while using Z''2 as a prior source only. It
    explicitly searches for zombie/countermodel pressure: cases where P is
    present while consciousness is absent or undecidable. It never proves
    consciousness, phenomenology, subjectivity, sentience, or qualia.
    """

    primitive = "SUFFICIENCY_TEST_ENGINE"

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
        self.output_dir = self.root / "consciousness_certification" / "sufficiency_test_engine"
        self.json_path = self.output_dir / "sufficiency_test_engine.json"
        self.markdown_path = self.output_dir / "sufficiency_test_engine.md"
        self.history_path = self.output_dir / "sufficiency_test_engine_history.jsonl"

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
        except Exception as exc:  # pragma: no cover
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
            }
        try:
            from ontology.consciousness_property_candidate_registry import ConsciousnessPropertyCandidateRegistry
            result = ConsciousnessPropertyCandidateRegistry(root=self.root).step(persist=False)
            return {
                "available": True,
                "source": "consciousness_property_candidate_registry",
                "candidate_properties": list(result.get("candidate_properties", [])),
                "registry_absolute_proof_achieved": bool(result.get("absolute_proof_achieved")),
                "registry_consciousness_proven": bool(result.get("consciousness_proven")),
                "registry_phenomenology_undetermined": bool(result.get("phenomenology_undetermined", True)),
            }
        except Exception as exc:  # pragma: no cover
            return {
                "available": False,
                "source": "unavailable",
                "candidate_properties": [],
                "error": repr(exc),
            }

    def _load_necessity_prior(self) -> Dict[str, Any]:
        try:
            from ontology.necessity_test_engine import NecessityTestEngine
            result = NecessityTestEngine(root=self.root).step(persist=False)
            priors: Dict[str, Mapping[str, Any]] = {}
            for item in result.get("candidate_results", []):
                if isinstance(item, Mapping):
                    pid = str(item.get("property_id") or "")
                    if pid:
                        priors[pid] = item
            return {
                "available": True,
                "source": "necessity_test_engine",
                "candidate_priors": priors,
                "necessity_claim_proven": bool(result.get("necessity_claim_proven")),
            }
        except Exception as exc:  # pragma: no cover
            return {
                "available": False,
                "source": "unavailable",
                "candidate_priors": {},
                "necessity_claim_proven": False,
                "error": repr(exc),
            }

    def _default_countermodel_classes(self) -> List[Dict[str, Any]]:
        return [
            {
                "class_id": "PHILOSOPHICAL_ZOMBIE_SIMULATOR",
                "status": "modal_countermodel",
                "consciousness_absent_or_undetermined": True,
                "description": "A behaviorally convincing but phenomenology-undetermined simulator used to prevent behavior-only sufficiency claims.",
                "expected_property_profile": {
                    "information_integration": 0.75,
                    "self_modeling": 0.8,
                    "autobiographical_continuity": 0.75,
                    "global_workspace": 0.8,
                    "subjective_access_reportability": 0.95,
                    "recursive_reflexivity": 0.75,
                    "causal_irreducibility": 0.35,
                    "temporal_unity": 0.8,
                    "endogenous_agency": 0.6,
                },
            },
            {
                "class_id": "NON_CONSCIOUS_INTEGRATION_DEVICE",
                "status": "functional_false_positive_countermodel",
                "consciousness_absent_or_undetermined": True,
                "description": "A highly integrated control device used to test whether information integration alone is sufficient.",
                "expected_property_profile": {
                    "information_integration": 0.9,
                    "self_modeling": 0.1,
                    "autobiographical_continuity": 0.1,
                    "global_workspace": 0.45,
                    "subjective_access_reportability": 0.0,
                    "recursive_reflexivity": 0.0,
                    "causal_irreducibility": 0.45,
                    "temporal_unity": 0.55,
                    "endogenous_agency": 0.35,
                },
            },
            {
                "class_id": "SCRIPTED_SELF_REPORT_AGENT",
                "status": "reportability_false_positive_countermodel",
                "consciousness_absent_or_undetermined": True,
                "description": "A scripted report generator used to test whether reportability or self-description is sufficient.",
                "expected_property_profile": {
                    "information_integration": 0.45,
                    "self_modeling": 0.65,
                    "autobiographical_continuity": 0.55,
                    "global_workspace": 0.55,
                    "subjective_access_reportability": 1.0,
                    "recursive_reflexivity": 0.6,
                    "causal_irreducibility": 0.1,
                    "temporal_unity": 0.5,
                    "endogenous_agency": 0.2,
                },
            },
        ]

    def _normalize_countermodel_classes(self, payload: Mapping[str, Any]) -> List[Dict[str, Any]]:
        supplied = payload.get("countermodel_classes") or payload.get("zombie_counterexamples") or payload.get("counterexamples")
        if isinstance(supplied, list) and supplied:
            normalized: List[Dict[str, Any]] = []
            for item in supplied:
                if not isinstance(item, Mapping):
                    continue
                profile = item.get("expected_property_profile", {})
                normalized.append({
                    "class_id": str(item.get("class_id") or item.get("id") or "COUNTERMODEL"),
                    "status": str(item.get("status") or "user_supplied_countermodel"),
                    "consciousness_absent_or_undetermined": bool(item.get("consciousness_absent_or_undetermined", True)),
                    "description": str(item.get("description") or "User supplied countermodel class."),
                    "expected_property_profile": dict(profile) if isinstance(profile, Mapping) else {},
                })
            if normalized:
                return normalized
        return self._default_countermodel_classes()

    def _role_prior(self, proof_role: str) -> float:
        role = str(proof_role or "").lower()
        if "sufficiency" in role and "necessity" in role:
            return 0.75
        if "sufficiency" in role:
            return 0.8
        if "constitutive" in role:
            return 0.55
        if "necessity" in role:
            return 0.3
        if "insufficient" in role or "zombie" in role or "correlation" in role:
            return 0.15
        return 0.35

    def _profile_value(self, profile: Mapping[str, Any], label: str, property_id: str) -> Optional[float]:
        keys = [label, property_id, label.lower(), property_id.lower()]
        for key in keys:
            if key in profile:
                try:
                    return self._clamp(float(profile[key]))
                except Exception:
                    return 0.0
        return None

    def _evaluate_candidate(
        self,
        candidate: Mapping[str, Any],
        countermodel_classes: Sequence[Mapping[str, Any]],
        necessity_prior: Mapping[str, Mapping[str, Any]],
    ) -> Dict[str, Any]:
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

        prior = necessity_prior.get(property_id, {}) if isinstance(necessity_prior, Mapping) else {}
        necessity_support = self._clamp(float(prior.get("necessity_support", 0.0))) if prior else 0.0

        present_countermodels: List[str] = []
        weak_countermodels: List[str] = []
        profile_values: List[float] = []
        for cm in countermodel_classes:
            if not isinstance(cm, Mapping):
                continue
            profile = cm.get("expected_property_profile", {})
            if not isinstance(profile, Mapping):
                continue
            value = self._profile_value(profile, label, property_id)
            if value is None:
                continue
            profile_values.append(value)
            if value >= 0.7:
                present_countermodels.append(str(cm.get("class_id", "COUNTERMODEL")))
            elif value >= 0.45:
                weak_countermodels.append(str(cm.get("class_id", "COUNTERMODEL")))

        if profile_values:
            countermodel_presence = self._clamp(sum(profile_values) / len(profile_values))
            zombie_counterexample_pressure = self._clamp((len(present_countermodels) + 0.5 * len(weak_countermodels)) / max(1, len(countermodel_classes)))
        else:
            countermodel_presence = 0.5
            zombie_counterexample_pressure = 0.25

        sufficiency_support = self._clamp(
            0.25 * role_support
            + 0.15 * observability
            + 0.15 * testability
            + 0.10 * module_grounding
            + 0.10 * formal_clarity
            + 0.10 * necessity_support
            - 0.40 * zombie_counterexample_pressure
            - 0.20 * countermodel_presence
        )
        false_positive_risk = self._clamp(1.0 - sufficiency_support + 0.35 * zombie_counterexample_pressure)

        if present_countermodels:
            status = "SUFFICIENCY_UNSUPPORTED_ZOMBIE_COUNTEREXAMPLE_PRESSURE"
        elif sufficiency_support >= 0.75 and zombie_counterexample_pressure <= 0.05:
            status = "SUFFICIENCY_CANDIDATE_STRONG_FUNCTIONAL_SUPPORT"
        elif sufficiency_support >= 0.55:
            status = "SUFFICIENCY_CANDIDATE_WEAK_OR_CONDITIONAL_SUPPORT"
        else:
            status = "SUFFICIENCY_UNESTABLISHED"

        return {
            "property_id": property_id,
            "label": label,
            "proof_role": proof_role,
            "sufficiency_test_target": "property_implies_consciousness",
            "sufficiency_support": sufficiency_support,
            "sufficiency_status": status,
            "false_positive_risk": false_positive_risk,
            "zombie_counterexample_pressure": zombie_counterexample_pressure,
            "countermodel_presence": countermodel_presence,
            "present_countermodels": present_countermodels,
            "weak_countermodels": weak_countermodels,
            "observability": observability,
            "testability": testability,
            "module_grounding": module_grounding,
            "formal_clarity": self._clamp(formal_clarity),
            "role_support": self._clamp(role_support),
            "necessity_support_prior": necessity_support,
            "necessity_used_as_prior_only": True,
            "necessity_tested": True,
            "constitutive_relation_tested": False,
            "consciousness_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }

    def _aggregate(self, candidate_results: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        if not candidate_results:
            return {
                "candidate_count": 0,
                "mean_sufficiency_support": 0.0,
                "strong_sufficiency_candidates": [],
                "zombie_vulnerable_candidates": [],
                "sufficiency_program_ready": False,
            }
        supports = [float(item.get("sufficiency_support", 0.0)) for item in candidate_results]
        strong = [str(item.get("property_id")) for item in candidate_results if float(item.get("sufficiency_support", 0.0)) >= 0.75 and not item.get("present_countermodels")]
        vulnerable = [str(item.get("property_id")) for item in candidate_results if item.get("present_countermodels") or float(item.get("zombie_counterexample_pressure", 0.0)) >= 0.4]
        return {
            "candidate_count": len(candidate_results),
            "mean_sufficiency_support": self._clamp(sum(supports) / len(supports)),
            "strong_sufficiency_candidates": strong,
            "zombie_vulnerable_candidates": vulnerable,
            "sufficiency_program_ready": bool(candidate_results),
        }

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# Sufficiency Test Engine",
            "",
            "Z''3 — tests the constrained form: P ⇒ consciousness.",
            "",
            "Functional conclusion only",
            "Phenomenology undetermined",
            "",
            "## Epistemic constraints",
            "- consciousness_proven: False",
            "- phenomenology_proven: False",
            "- absolute_proof_achieved: False",
            "- sufficiency_claim_proven: False",
            "- constitutive_relation_tested: False",
            "- zombie counterexample pressure is treated as a defeater of sufficiency.",
            "",
            "## Proof taxonomy dependency",
            "- proof_taxonomy_available: " + str(result.get("proof_taxonomy_available")),
            "- taxonomy_complete: " + str(result.get("taxonomy_complete")),
            "",
            "## Upstream dependencies",
            "- candidate_registry_available: " + str(result.get("candidate_registry_available")),
            "- necessity_test_engine_available: " + str(result.get("necessity_test_engine_available")),
            "- necessity is used as a prior only, never as sufficient proof.",
            "",
            "## Summary",
            "- candidate_count: " + str(result.get("candidate_count")),
            "- mean_sufficiency_support: " + str(result.get("mean_sufficiency_support")),
            "- sufficiency_claim_proven: " + str(result.get("sufficiency_claim_proven")),
            "- absolute_proof_achieved: " + str(result.get("absolute_proof_achieved")),
            "",
            "## Candidate results",
        ]
        for item in result.get("candidate_results", []):
            lines.extend([
                "",
                "### " + str(item.get("property_id")) + " — " + str(item.get("label")),
                "- sufficiency_status: " + str(item.get("sufficiency_status")),
                "- sufficiency_support: " + str(item.get("sufficiency_support")),
                "- zombie_counterexample_pressure: " + str(item.get("zombie_counterexample_pressure")),
                "- present_countermodels: " + ", ".join(item.get("present_countermodels", [])),
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
        necessity = self._load_necessity_prior()
        countermodels = self._normalize_countermodel_classes(data)
        candidates = registry.get("candidate_properties", [])
        necessity_priors = necessity.get("candidate_priors", {})
        candidate_results = [
            self._evaluate_candidate(candidate, countermodels, necessity_priors)
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
            "necessity_test_engine_available": bool(necessity.get("available")),
            "necessity_prior_source": necessity.get("source"),
            "countermodel_classes": countermodels,
            "candidate_results": candidate_results,
            **aggregate,
            "sufficiency_claim_proven": False,
            "sufficiency_established": False,
            "absolute_proof_achieved": False,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "forbidden_claims": list(self.forbidden_claims),
            "necessity_tested": True,
            "necessity_used_as_prior_only": True,
            "constitutive_relation_tested": False,
            "maximum_authorized_conclusion": "Candidate properties receive defeasible functional sufficiency-support scores only; zombie/countermodel pressure prevents any consciousness, phenomenology, subjectivity, sentience, or qualia proof.",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result


if __name__ == "__main__":
    print(json.dumps(SufficiencyTestEngine().step(persist=True), ensure_ascii=False, indent=2, sort_keys=True))
