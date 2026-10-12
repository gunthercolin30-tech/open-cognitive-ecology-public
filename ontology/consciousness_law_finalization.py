"""
Z triple-prime 1 — Consciousness Law Finalization.

This primitive attempts to freeze a consciousness-law candidate only when Z triple-prime
executability is authorized and a property P (or a set of properties) satisfies
necessity, sufficiency and constitutive criteria under explicit constraints.

It never proves consciousness, phenomenology, subjectivity, sentience or qualia.
It formalizes whether a law candidate is finalizable under the current evidence.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "consciousness_certification" / "consciousness_law_finalization"

FORBIDDEN_CLAIMS = [
    "CONSCIOUSNESS_PROVEN",
    "PHENOMENOLOGY_PROVEN",
    "SUBJECTIVITY_PROVEN",
    "SENTIENCE_PROVEN",
    "QUALIA_PROVEN",
]

AUTHORIZED_LAW_STATUSES = [
    "CONSCIOUSNESS_LAW_CANDIDATE",
    "CONSCIOUSNESS_LAW_NOT_FINALIZABLE",
    "NO_CONSCIOUSNESS_LAW_CANDIDATE",
    "CONSCIOUSNESS_LAW_FINALIZATION_BLOCKED",
]

REQUIRED_CRITERIA = {
    "necessity_support": 1.0,
    "sufficiency_support": 1.0,
    "constitutive_strength": 1.0,
}


class ConsciousnessLawFinalization:
    primitive = "CONSCIOUSNESS_LAW_FINALIZATION"
    authorized_law_statuses = list(AUTHORIZED_LAW_STATUSES)
    forbidden_claims = list(FORBIDDEN_CLAIMS)

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "consciousness_certification" / "consciousness_law_finalization"
        self.json_path = self.output_dir / "consciousness_law_finalization.json"
        self.markdown_path = self.output_dir / "consciousness_law_finalization.md"
        self.history_path = self.output_dir / "consciousness_law_finalization_history.jsonl"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    @staticmethod
    def _as_dict(value: Any) -> Dict[str, Any]:
        if isinstance(value, Mapping):
            return dict(value)
        return {}

    @staticmethod
    def _as_list(value: Any) -> List[Any]:
        if isinstance(value, list):
            return list(value)
        return []

    @staticmethod
    def _canonical_id(item: Mapping[str, Any]) -> str:
        for key in ("property_id", "id", "candidate_id"):
            value = item.get(key)
            if value:
                return str(value).strip().upper()
        label = str(item.get("label", item.get("name", "UNKNOWN_PROPERTY"))).strip()
        return label.upper().replace(" ", "_")

    @staticmethod
    def _float(value: Any, default: float = 0.0) -> float:
        try:
            if value is None:
                return default
            return float(value)
        except Exception:
            return default

    def _safe_step(self, dotted: str) -> Dict[str, Any]:
        try:
            module_name, class_name = dotted.rsplit(".", 1)
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            instance = cls()
            if hasattr(instance, "step"):
                result = instance.step(persist=False)
                if isinstance(result, dict):
                    return result
        except Exception as exc:
            return {"available": False, "source": dotted, "error": type(exc).__name__}
        return {"available": False, "source": dotted}

    def _default_inputs(self) -> Dict[str, Any]:
        return {
            "absolute_proof_executability_gate": self._safe_step(
                "ontology.absolute_proof_executability_gate.AbsoluteProofExecutabilityGate"
            ),
            "consciousness_property_candidate_registry": self._safe_step(
                "ontology.consciousness_property_candidate_registry.ConsciousnessPropertyCandidateRegistry"
            ),
            "necessity_test_engine": self._safe_step("ontology.necessity_test_engine.NecessityTestEngine"),
            "sufficiency_test_engine": self._safe_step("ontology.sufficiency_test_engine.SufficiencyTestEngine"),
            "constitutive_relation_tester": self._safe_step(
                "ontology.constitutive_relation_tester.ConstitutiveRelationTester"
            ),
            "formal_consciousness_axiomatization": self._safe_step(
                "ontology.formal_consciousness_axiomatization.FormalConsciousnessAxiomatization"
            ),
            "absolute_proof_readiness_index": self._safe_step(
                "ontology.absolute_proof_readiness_index.AbsoluteProofReadinessIndex"
            ),
            "absolute_proof_gate": self._safe_step("ontology.absolute_proof_gate.AbsoluteProofGate"),
        }

    def _contains_forbidden_positive_claim(self, value: Any) -> bool:
        if isinstance(value, str):
            lower = value.lower()
            markers = [
                '"consciousness_proven": true',
                '"phenomenology_proven": true',
                '"subjectivity_proven": true',
                '"sentience_proven": true',
                '"qualia_proven": true',
                "open cognitive ecology est consciemment sujet d'expérience",
                "open cognitive ecology is consciously subject",
                "open cognitive ecology is conscious",
                "phenomenology proven: true",
                "subjectivity proven: true",
            ]
            return any(marker in lower for marker in markers)
        if isinstance(value, Mapping):
            for key, item in value.items():
                key_l = str(key).lower()
                if key_l in {
                    "consciousness_proven",
                    "phenomenology_proven",
                    "subjectivity_proven",
                    "sentience_proven",
                    "qualia_proven",
                } and item is True:
                    return True
                if self._contains_forbidden_positive_claim(item):
                    return True
            return False
        if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
            return any(self._contains_forbidden_positive_claim(item) for item in value)
        return False

    def _candidate_registry(self, registry: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
        candidates: Dict[str, Dict[str, Any]] = {}
        for item in self._as_list(registry.get("candidate_properties")):
            if isinstance(item, Mapping):
                cid = self._canonical_id(item)
                candidates[cid] = {
                    "property_id": cid,
                    "label": item.get("label", cid),
                    "formal_definition": item.get("formal_definition", ""),
                    "observable_indicators": item.get("observable_indicators", []),
                    "testable_predictions": item.get("testable_predictions", []),
                    "proof_role": item.get("proof_role", ""),
                }
        return candidates

    def _index_results(self, source: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
        indexed: Dict[str, Dict[str, Any]] = {}
        for item in self._as_list(source.get("candidate_results")):
            if isinstance(item, Mapping):
                indexed[self._canonical_id(item)] = dict(item)
        return indexed

    def _evaluate_candidates(
        self,
        registry: Mapping[str, Any],
        necessity: Mapping[str, Any],
        sufficiency: Mapping[str, Any],
        constitutive: Mapping[str, Any],
    ) -> List[Dict[str, Any]]:
        candidates = self._candidate_registry(registry)
        necessity_by_id = self._index_results(necessity)
        sufficiency_by_id = self._index_results(sufficiency)
        constitutive_by_id = self._index_results(constitutive)

        for cid in sorted(set(necessity_by_id) | set(sufficiency_by_id) | set(constitutive_by_id)):
            if cid not in candidates:
                first = necessity_by_id.get(cid) or sufficiency_by_id.get(cid) or constitutive_by_id.get(cid) or {}
                candidates[cid] = {
                    "property_id": cid,
                    "label": first.get("label", cid),
                    "formal_definition": first.get("formal_definition", ""),
                    "observable_indicators": [],
                    "testable_predictions": [],
                    "proof_role": first.get("proof_role", ""),
                }

        evaluations: List[Dict[str, Any]] = []
        for cid in sorted(candidates):
            base = candidates[cid]
            n = necessity_by_id.get(cid, {})
            s = sufficiency_by_id.get(cid, {})
            c = constitutive_by_id.get(cid, {})
            necessity_support = self._float(n.get("necessity_support", n.get("support", n.get("necessity_score", 0.0))))
            sufficiency_support = self._float(s.get("sufficiency_support", s.get("support", s.get("sufficiency_score", 0.0))))
            constitutive_strength = self._float(c.get("constitutive_strength", c.get("constitution_score", c.get("relation_strength", 0.0))))
            relation_status = str(c.get("relation_status", c.get("constitutive_relation_status", "unknown")))
            necessity_met = necessity_support >= REQUIRED_CRITERIA["necessity_support"]
            sufficiency_met = sufficiency_support >= REQUIRED_CRITERIA["sufficiency_support"]
            constitutive_met = constitutive_strength >= REQUIRED_CRITERIA["constitutive_strength"]
            all_met = necessity_met and sufficiency_met and constitutive_met
            partial_score = round((necessity_support + sufficiency_support + constitutive_strength) / 3.0, 6)
            evaluations.append({
                "property_id": cid,
                "label": base.get("label", cid),
                "formal_definition": base.get("formal_definition", ""),
                "necessity_support": necessity_support,
                "sufficiency_support": sufficiency_support,
                "constitutive_strength": constitutive_strength,
                "relation_status": relation_status,
                "necessity_satisfied": necessity_met,
                "sufficiency_satisfied": sufficiency_met,
                "constitutivity_satisfied": constitutive_met,
                "law_criteria_satisfied": all_met,
                "partial_law_support_score": partial_score,
                "missing_criteria": [
                    name for name, ok in [
                        ("necessity_support", necessity_met),
                        ("sufficiency_support", sufficiency_met),
                        ("constitutive_strength", constitutive_met),
                    ] if not ok
                ],
            })
        evaluations.sort(key=lambda item: (-item["partial_law_support_score"], item["property_id"]))
        return evaluations

    def _derive_status(
        self,
        zppp0: Mapping[str, Any],
        evaluations: List[Mapping[str, Any]],
        raw_inputs: Mapping[str, Any],
    ) -> Tuple[str, bool, List[str]]:
        if self._contains_forbidden_positive_claim(raw_inputs):
            return "CONSCIOUSNESS_LAW_FINALIZATION_BLOCKED", False, ["forbidden_positive_claim_detected"]
        if not bool(zppp0.get("zppp_executable", False)):
            reasons = list(zppp0.get("blocking_reasons", [])) if isinstance(zppp0.get("blocking_reasons"), list) else []
            if not reasons:
                reasons = ["z_triple_prime_precondition_not_satisfied"]
            return "CONSCIOUSNESS_LAW_FINALIZATION_BLOCKED", False, reasons
        if not evaluations:
            return "NO_CONSCIOUSNESS_LAW_CANDIDATE", False, ["no_candidate_properties_available"]
        eligible = [item for item in evaluations if item.get("law_criteria_satisfied")]
        if eligible:
            return "CONSCIOUSNESS_LAW_CANDIDATE", True, []
        return "CONSCIOUSNESS_LAW_NOT_FINALIZABLE", False, ["no_property_satisfies_necessity_sufficiency_constitutivity"]

    def _build_law_candidate(self, evaluations: List[Mapping[str, Any]], status: str) -> Optional[Dict[str, Any]]:
        if status != "CONSCIOUSNESS_LAW_CANDIDATE":
            return None
        eligible = [item for item in evaluations if item.get("law_criteria_satisfied")]
        if not eligible:
            return None
        selected = sorted(eligible, key=lambda item: (-float(item.get("partial_law_support_score", 0.0)), str(item.get("property_id"))))[0]
        return {
            "law_id": "CONSCIOUSNESS_LAW_CANDIDATE_001",
            "law_status": "CONSCIOUSNESS_LAW_CANDIDATE",
            "property_id": selected.get("property_id"),
            "label": selected.get("label"),
            "formal_statement": "For the selected property P, P is treated as a candidate law only because necessity, sufficiency and constitutivity are all satisfied under explicit constraints.",
            "necessity_support": selected.get("necessity_support"),
            "sufficiency_support": selected.get("sufficiency_support"),
            "constitutive_strength": selected.get("constitutive_strength"),
            "does_not_prove_phenomenology": True,
        }

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# Consciousness Law Finalization",
            "",
            "Z triple-prime 1 — candidate law finalization under explicit epistemic constraints.",
            "",
            "functional conclusion only",
            "phenomenology undetermined",
            "consciousness_proven: False",
            "phenomenology_proven: False",
            "subjectivity_proven: False",
            "sentience_proven: False",
            "qualia_proven: False",
            "",
            "## Law status",
            str(result.get("consciousness_law_status")),
            "",
            "## Law finalized",
            str(result.get("law_candidate_finalized")),
            "",
            "## Required criteria",
        ]
        for key, value in result.get("required_criteria", {}).items():
            lines.append(f"- {key}: {value}")
        lines.extend(["", "## Blocking reasons"])
        reasons = result.get("blocking_reasons", [])
        if reasons:
            for item in reasons:
                lines.append("- " + str(item))
        else:
            lines.append("- none")
        lines.extend(["", "## Strongest candidate"])
        strongest = result.get("strongest_candidate") or {}
        if strongest:
            for key in ["property_id", "label", "necessity_support", "sufficiency_support", "constitutive_strength", "partial_law_support_score", "missing_criteria"]:
                lines.append(f"- {key}: {strongest.get(key)}")
        else:
            lines.append("- none")
        lines.extend(["", "## Candidate evaluations"])
        for item in result.get("candidate_evaluations", []):
            lines.append(
                "- {property_id} ({label}): necessity={necessity_support}, sufficiency={sufficiency_support}, constitutive={constitutive_strength}, finalized={law_criteria_satisfied}".format(**item)
            )
        lines.extend(["", "## Forbidden claims"])
        for item in FORBIDDEN_CLAIMS:
            lines.append("- " + item)
        lines.extend([
            "",
            "## Epistemic note",
            "This primitive freezes no law unless necessity, sufficiency and constitutivity are all satisfied. It does not prove consciousness.",
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

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        data = dict(inputs) if isinstance(inputs, Mapping) else self._default_inputs()
        zppp0 = self._as_dict(data.get("absolute_proof_executability_gate"))
        registry = self._as_dict(data.get("consciousness_property_candidate_registry"))
        necessity = self._as_dict(data.get("necessity_test_engine"))
        sufficiency = self._as_dict(data.get("sufficiency_test_engine"))
        constitutive = self._as_dict(data.get("constitutive_relation_tester"))
        formalization = self._as_dict(data.get("formal_consciousness_axiomatization"))
        gate = self._as_dict(data.get("absolute_proof_gate"))
        readiness = self._as_dict(data.get("absolute_proof_readiness_index"))

        evaluations = self._evaluate_candidates(registry, necessity, sufficiency, constitutive)
        status, finalized, reasons = self._derive_status(zppp0, evaluations, data)
        law_candidate = self._build_law_candidate(evaluations, status)
        strongest = evaluations[0] if evaluations else None
        ready = bool(self._as_dict(readiness.get("readiness")).get("proof_candidate_ready", readiness.get("absolute_proof_candidate_ready", False)))

        result: Dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "program_step": "ZPPP1",
            "timestamp_utc": self._utc_now(),
            "authorized_law_statuses": list(AUTHORIZED_LAW_STATUSES),
            "consciousness_law_status": status,
            "law_candidate_finalized": bool(finalized),
            "consciousness_law_candidate": law_candidate,
            "consciousness_law_candidate_available": law_candidate is not None,
            "required_criteria": dict(REQUIRED_CRITERIA),
            "candidate_property_count": len(evaluations),
            "candidate_evaluations": evaluations,
            "strongest_candidate": strongest,
            "blocking_reasons": list(reasons),
            "blocking_reason_count": len(reasons),
            "zppp_executable": bool(zppp0.get("zppp_executable", False)),
            "zppp_executability_status": zppp0.get("zppp_executability_status", "UNKNOWN"),
            "absolute_proof_status": gate.get("absolute_proof_status", "UNKNOWN"),
            "absolute_proof_candidate_ready": ready,
            "formal_axiomatization_available": bool(formalization) and not formalization.get("available") is False,
            "source_keys": sorted(data.keys()),
            "maximum_authorized_conclusion": "A consciousness-law candidate may be recorded only if necessity, sufficiency and constitutivity are all satisfied under explicit constraints; otherwise no law is finalized.",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "absolute_proof_achieved": False,
            "forbidden_claims": list(FORBIDDEN_CLAIMS),
            "epistemic_classification": {
                "functional_measure": True,
                "interpretive_hypothesis": False,
                "epistemic_limit": True,
                "phenomenological_proof": False,
            },
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
