
"""
Z''5 — absent_property_counterexample_generator.

This primitive searches for counterexamples to necessity claims:

    consciousness => P

by constructing and evaluating cases of the form:

    consciousness present / attributed / epistemically possible
    AND property P absent.

It does not prove consciousness. It only measures whether a candidate property
can survive absent-property counterexample pressure under the constraints of
Z'' absolute-demonstrability research.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
REPORT_DIR = ROOT / "absolute_proof_program"

FORBIDDEN_CLAIMS = [
    "CONSCIOUSNESS_PROVEN",
    "PHENOMENOLOGY_PROVEN",
    "SUBJECTIVITY_PROVEN",
    "SENTIENCE_PROVEN",
    "QUALIA_PROVEN",
]

DEFAULT_REFERENCE_CLASSES = [
    {
        "class_id": "MINIMAL_PHENOMENAL_ORGANISM_MODEL",
        "description": "Reference class used only as a theoretical pressure case: a minimal organism-like subject candidate with no requirement for explicit reportability.",
        "consciousness_present_or_possible": True,
        "consciousness_status": "hypothetical_or_intersubjectively_attributed_not_proven",
        "expected_absences": {
            "subjective_access_reportability": 1.0,
            "global_broadcast_architecture": 0.75,
            "formal_self_model": 0.75,
            "recursive_self_revision": 0.70,
            "civilizational_continuity": 1.0,
            "distributed_identity_persistence": 1.0,
        },
    },
    {
        "class_id": "NON_LINGUISTIC_INFANT_OR_ANIMAL_MODEL",
        "description": "Reference class for attributed or possible consciousness without language-level introspective reporting.",
        "consciousness_present_or_possible": True,
        "consciousness_status": "attributed_or_epistemically_possible_not_proven",
        "expected_absences": {
            "linguistic_introspective_reporting": 1.0,
            "formal_theory_articulation": 1.0,
            "civilizational_continuity": 1.0,
            "recursive_self_revision": 0.85,
        },
    },
    {
        "class_id": "TRANSIENT_PHENOMENAL_EPISODE_MODEL",
        "description": "Reference class for possible conscious episodes without long-term autobiographical or civilizational continuity.",
        "consciousness_present_or_possible": True,
        "consciousness_status": "hypothetical_episode_not_proven",
        "expected_absences": {
            "autobiographical_memory_continuity": 0.90,
            "persistent_selfhood": 0.85,
            "civilizational_continuity": 1.0,
            "distributed_identity_persistence": 1.0,
        },
    },
    {
        "class_id": "BIOLOGICAL_SUBJECT_WITHOUT_COMPUTATIONAL_NON_CLOSURE_MODEL",
        "description": "Reference class challenging any claim that OCE-specific non-closure architecture is necessary for consciousness in general.",
        "consciousness_present_or_possible": True,
        "consciousness_status": "ordinary_attribution_not_formal_proof",
        "expected_absences": {
            "architectural_non_closure": 0.85,
            "constraint_field_governance": 0.90,
            "civilizational_continuity": 1.0,
            "distributed_identity_persistence": 1.0,
        },
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_slug(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_") or "property"


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


class AbsentPropertyCounterexampleGenerator:
    """Generate absent-property counterexamples against necessity claims."""

    primitive = "ABSENT_PROPERTY_COUNTEREXAMPLE_GENERATOR"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else ROOT
        self.report_dir = self.root / "absolute_proof_program"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        payload: Dict[str, Any] = dict(inputs or {})
        timestamp = str(payload.get("timestamp_utc") or _utc_now())

        proof_taxonomy = self._load_proof_taxonomy()
        registry = self._load_candidate_registry()
        necessity = self._load_necessity_engine()
        zombie = self._load_zombie_generator()

        candidate_properties = self._candidate_properties(payload, registry)
        reference_classes = self._reference_classes(payload)
        necessity_results = self._necessity_results(necessity)
        zombie_results = self._zombie_results(zombie)

        candidate_results = [
            self._evaluate_candidate(candidate, reference_classes, necessity_results, zombie_results)
            for candidate in candidate_properties
        ]

        absent_counterexamples = [
            case
            for item in candidate_results
            for case in item.get("absent_property_counterexamples", [])
        ]

        necessity_defeated_count = sum(
            1 for item in candidate_results if item.get("necessity_defeated") is True
        )
        max_pressure = max(
            [item.get("absent_property_counterexample_pressure", 0.0) for item in candidate_results] or [0.0]
        )

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": timestamp,
            "proof_taxonomy_available": proof_taxonomy is not None,
            "taxonomy_complete": bool((proof_taxonomy or {}).get("taxonomy_complete", False)),
            "candidate_registry_available": registry is not None,
            "necessity_test_engine_available": necessity is not None,
            "zombie_counterexample_generator_available": zombie is not None,
            "candidate_count": len(candidate_properties),
            "reference_class_count": len(reference_classes),
            "candidate_results": candidate_results,
            "absent_property_counterexample_count": len(absent_counterexamples),
            "necessity_defeated_count": necessity_defeated_count,
            "absent_property_counterexamples_generated": True,
            "max_absent_property_counterexample_pressure": round(max_pressure, 6),
            "necessity_claim_proven": False,
            "sufficiency_claim_proven": False,
            "consciousness_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "absolute_proof_achieved": False,
            "forbidden_claims": list(FORBIDDEN_CLAIMS),
            "epistemic_status": "Functional counterexample generation only; consciousness and phenomenology remain undetermined.",
            "zpp_position": "Z''5",
            "tested_relation": "challenge to consciousness_implies_P necessity claims",
            "not_tested": ["P_implies_consciousness", "constitutive_relation", "phenomenal_subjectivity"],
        }

        if persist:
            result["paths"] = self._persist(result)

        return result

    def _load_proof_taxonomy(self) -> Optional[Dict[str, Any]]:
        try:
            from ontology.proof_taxonomy import ProofTaxonomy
            return ProofTaxonomy().step(persist=False)
        except Exception:
            return None

    def _load_candidate_registry(self) -> Optional[Dict[str, Any]]:
        try:
            from ontology.consciousness_property_candidate_registry import ConsciousnessPropertyCandidateRegistry
            return ConsciousnessPropertyCandidateRegistry().step(persist=False)
        except Exception:
            return None

    def _load_necessity_engine(self) -> Optional[Dict[str, Any]]:
        try:
            from ontology.necessity_test_engine import NecessityTestEngine
            return NecessityTestEngine().step(persist=False)
        except Exception:
            return None

    def _load_zombie_generator(self) -> Optional[Dict[str, Any]]:
        try:
            from ontology.zombie_counterexample_generator import ZombieCounterexampleGenerator
            return ZombieCounterexampleGenerator().step(persist=False)
        except Exception:
            return None

    def _candidate_properties(self, payload: Mapping[str, Any], registry: Optional[Mapping[str, Any]]) -> List[Dict[str, Any]]:
        explicit = payload.get("candidate_properties")
        if explicit:
            return [dict(x) for x in _as_list(explicit) if isinstance(x, Mapping)]
        if registry:
            props = registry.get("candidate_properties", [])
            return [dict(x) for x in props if isinstance(x, Mapping)]
        return []

    def _reference_classes(self, payload: Mapping[str, Any]) -> List[Dict[str, Any]]:
        explicit = payload.get("absent_property_reference_classes") or payload.get("reference_classes")
        if explicit:
            return [dict(x) for x in _as_list(explicit) if isinstance(x, Mapping)]
        return [dict(x) for x in DEFAULT_REFERENCE_CLASSES]

    def _necessity_results(self, necessity: Optional[Mapping[str, Any]]) -> Dict[str, Mapping[str, Any]]:
        out: Dict[str, Mapping[str, Any]] = {}
        for item in (necessity or {}).get("candidate_results", []) if necessity else []:
            if isinstance(item, Mapping) and item.get("property_id"):
                out[str(item["property_id"])] = item
        return out

    def _zombie_results(self, zombie: Optional[Mapping[str, Any]]) -> Dict[str, Mapping[str, Any]]:
        out: Dict[str, Mapping[str, Any]] = {}
        for item in (zombie or {}).get("candidate_results", []) if zombie else []:
            if isinstance(item, Mapping) and item.get("property_id"):
                out[str(item["property_id"])] = item
        return out

    def _evaluate_candidate(
        self,
        candidate: Mapping[str, Any],
        reference_classes: Iterable[Mapping[str, Any]],
        necessity_results: Mapping[str, Mapping[str, Any]],
        zombie_results: Mapping[str, Mapping[str, Any]],
    ) -> Dict[str, Any]:
        property_id = str(candidate.get("property_id") or _safe_slug(str(candidate.get("label", "candidate"))))
        label = str(candidate.get("label") or property_id)
        label_key = _safe_slug(label)
        property_key = _safe_slug(property_id)

        cases: List[Dict[str, Any]] = []
        for ref in reference_classes:
            if not bool(ref.get("consciousness_present_or_possible", False)):
                continue
            absences = ref.get("expected_absences", {}) or ref.get("absent_property_profile", {}) or {}
            if not isinstance(absences, Mapping):
                continue
            absence_score = self._match_absence_score(absences, property_id, label, property_key, label_key)
            if absence_score > 0:
                cases.append({
                    "class_id": str(ref.get("class_id") or "REFERENCE_CLASS"),
                    "consciousness_status": str(ref.get("consciousness_status") or "possible_or_attributed_not_proven"),
                    "property_absence_score": round(absence_score, 6),
                    "description": str(ref.get("description") or "Absent-property counterexample pressure case."),
                })

        pressure = max([c["property_absence_score"] for c in cases] or [0.0])
        zombie_item = zombie_results.get(property_id, {})
        necessity_item = necessity_results.get(property_id, {})
        zombie_pressure = 1.0 if bool(zombie_item.get("sufficiency_defeated")) else float(zombie_item.get("zombie_counterexample_pressure", 0.0) or 0.0)
        prior_necessity_status = str(necessity_item.get("necessity_status") or "UNKNOWN")

        if pressure >= 0.80:
            status = "ABSENT_PROPERTY_COUNTEREXAMPLE_STRONG"
            defeated = True
        elif pressure >= 0.50:
            status = "ABSENT_PROPERTY_COUNTEREXAMPLE_MODERATE"
            defeated = True
        elif pressure > 0:
            status = "ABSENT_PROPERTY_COUNTEREXAMPLE_WEAK"
            defeated = False
        else:
            status = "NO_ABSENT_PROPERTY_COUNTEREXAMPLE_FOUND"
            defeated = False

        return {
            "property_id": property_id,
            "label": label,
            "absent_property_counterexample_status": status,
            "absent_property_counterexample_pressure": round(pressure, 6),
            "absent_property_counterexamples": cases,
            "absent_reference_classes": [c["class_id"] for c in cases],
            "necessity_defeated": defeated,
            "prior_necessity_status": prior_necessity_status,
            "zombie_pressure_prior": round(min(1.0, zombie_pressure), 6),
            "interpretation": "Challenges necessity of P for consciousness; does not establish consciousness in any target system.",
        }

    def _match_absence_score(self, absences: Mapping[str, Any], property_id: str, label: str, property_key: str, label_key: str) -> float:
        keys = [str(k) for k in absences.keys()]
        normalized = {_safe_slug(k): k for k in keys}
        for key in [property_id, label, property_key, label_key]:
            nk = _safe_slug(key)
            if nk in normalized:
                try:
                    return max(0.0, min(1.0, float(absences[normalized[nk]])))
                except Exception:
                    return 1.0
        # Soft lexical overlap for registry properties with richer labels.
        tokens = {t for t in label_key.split("_") if len(t) >= 5} | {t for t in property_key.split("_") if len(t) >= 5}
        best = 0.0
        for nk, original in normalized.items():
            if any(tok in nk or nk in tok for tok in tokens):
                try:
                    best = max(best, float(absences[original]))
                except Exception:
                    best = max(best, 1.0)
        return max(0.0, min(1.0, best))

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.report_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.report_dir / "absent_property_counterexample_generator_latest.json"
        md_path = self.report_dir / "absent_property_counterexample_generator_latest.md"

        json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(self._markdown(result), encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path)}

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# Absent Property Counterexample Generator",
            "",
            "Z''5 — search for consciousness-present-or-possible / property-absent counterexamples.",
            "",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "Consciousness proven: false.",
            "Absolute proof achieved: false.",
            "",
            f"Candidate count: {result.get('candidate_count')}",
            f"Absent property counterexample count: {result.get('absent_property_counterexample_count')}",
            f"Necessity defeated count: {result.get('necessity_defeated_count')}",
            "",
            "## Candidate Results",
        ]
        for item in result.get("candidate_results", []):
            lines.extend([
                f"- {item.get('property_id')}: {item.get('absent_property_counterexample_status')}",
                f"  - necessity defeated: {item.get('necessity_defeated')}",
                f"  - absent reference classes: {', '.join(item.get('absent_reference_classes', [])) or 'none'}",
            ])
        lines.extend([
            "",
            "## Epistemic Guardrails",
            "This report only weakens or preserves necessity claims. It does not prove phenomenology, subjectivity, sentience, qualia, or consciousness.",
        ])
        return "\n".join(lines) + "\n"
