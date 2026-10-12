"""
Z triple-prime 2 - Universal Counterexample Exhaustion.

This primitive does not generate new counterexamples. It aggregates and classifies
known counterexample families against the law candidate produced by Z triple-prime 1.
It never proves consciousness, phenomenology, subjectivity, sentience or qualia.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"

FORBIDDEN_CLAIMS = [
    "CONSCIOUSNESS_PROVEN",
    "PHENOMENOLOGY_PROVEN",
    "SUBJECTIVITY_PROVEN",
    "SENTIENCE_PROVEN",
    "QUALIA_PROVEN",
]

AUTHORIZED_EXHAUSTION_STATUSES = [
    "UNIVERSAL_COUNTEREXAMPLE_EXHAUSTED",
    "COUNTEREXAMPLES_REMAINING",
    "UNIVERSAL_COUNTEREXAMPLE_EXHAUSTION_INCOMPLETE",
    "UNIVERSAL_COUNTEREXAMPLE_EXHAUSTION_BLOCKED",
]

REQUIRED_COUNTEREXAMPLE_FAMILIES = [
    "functional_zombies",
    "absent_properties",
    "simulations",
    "statistical_imitations",
    "degenerate_architectures",
    "adversarial_attacks",
    "alternative_explanations",
    "false_positives",
    "anomalies",
    "cross_architecture_variants",
]

FAMILY_SOURCE_MAP = {
    "functional_zombies": ["zombie_counterexample_generator"],
    "absent_properties": ["absent_property_counterexample_generator"],
    "simulations": ["theory_falsification_framework", "cross_architecture_consciousness_comparison"],
    "statistical_imitations": ["zombie_counterexample_generator", "false_positive_detector", "statistical_robustness_evaluator"],
    "degenerate_architectures": ["cross_architecture_consciousness_comparison", "theory_falsification_framework"],
    "adversarial_attacks": ["adversarial_consciousness_audit"],
    "alternative_explanations": ["alternative_explanation_eliminator"],
    "false_positives": ["false_positive_detector"],
    "anomalies": ["anomaly_in_evidence_detector"],
    "cross_architecture_variants": ["cross_architecture_consciousness_comparison"],
}

COUNTEREXAMPLE_LIST_KEYS = [
    "counterexamples",
    "counterexample_results",
    "candidate_results",
    "zombie_counterexamples",
    "absent_property_counterexamples",
    "generated_counterexamples",
    "falsification_results",
    "adversarial_findings",
    "alternative_explanations",
    "false_positives",
    "anomalies",
    "architecture_results",
    "comparison_results",
    "findings",
    "results",
    "scenarios",
]


class UniversalCounterexampleExhaustion:
    primitive = "UNIVERSAL_COUNTEREXAMPLE_EXHAUSTION"
    authorized_exhaustion_statuses = list(AUTHORIZED_EXHAUSTION_STATUSES)
    forbidden_claims = list(FORBIDDEN_CLAIMS)

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "consciousness_certification" / "universal_counterexample_exhaustion"
        self.json_path = self.output_dir / "universal_counterexample_exhaustion.json"
        self.markdown_path = self.output_dir / "universal_counterexample_exhaustion.md"
        self.history_path = self.output_dir / "universal_counterexample_exhaustion_history.jsonl"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    @staticmethod
    def _as_dict(value: Any) -> Dict[str, Any]:
        return dict(value) if isinstance(value, Mapping) else {}

    @staticmethod
    def _as_list(value: Any) -> List[Any]:
        return list(value) if isinstance(value, list) else []

    @staticmethod
    def _float(value: Any, default: float = 0.0) -> float:
        try:
            return default if value is None else float(value)
        except Exception:
            return default

    def _safe_step(self, dotted: str) -> Dict[str, Any]:
        try:
            module_name, class_name = dotted.rsplit(".", 1)
            module = __import__(module_name, fromlist=[class_name])
            instance = getattr(module, class_name)()
            result = instance.step(persist=False) if hasattr(instance, "step") else {}
            return result if isinstance(result, dict) else {}
        except Exception as exc:
            return {"available": False, "source": dotted, "error": type(exc).__name__}

    def _default_inputs(self) -> Dict[str, Any]:
        return {
            "consciousness_law_finalization": self._safe_step("ontology.consciousness_law_finalization.ConsciousnessLawFinalization"),
            "zombie_counterexample_generator": self._safe_step("ontology.zombie_counterexample_generator.ZombieCounterexampleGenerator"),
            "absent_property_counterexample_generator": self._safe_step("ontology.absent_property_counterexample_generator.AbsentPropertyCounterexampleGenerator"),
            "theory_falsification_framework": self._safe_step("ontology.theory_falsification_framework.TheoryFalsificationFramework"),
            "adversarial_consciousness_audit": self._safe_step("ontology.adversarial_consciousness_audit.AdversarialConsciousnessAudit"),
            "alternative_explanation_eliminator": self._safe_step("ontology.alternative_explanation_eliminator.AlternativeExplanationEliminator"),
            "cross_architecture_consciousness_comparison": self._safe_step("ontology.cross_architecture_consciousness_comparison.CrossArchitectureConsciousnessComparison"),
            "false_positive_detector": self._safe_step("ontology.false_positive_detector.FalsePositiveDetector"),
            "anomaly_in_evidence_detector": self._safe_step("ontology.anomaly_in_evidence_detector.AnomalyInEvidenceDetector"),
            "statistical_robustness_evaluator": self._safe_step("ontology.statistical_robustness_evaluator.StatisticalRobustnessEvaluator"),
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
                if key_l in {"consciousness_proven", "phenomenology_proven", "subjectivity_proven", "sentience_proven", "qualia_proven"} and item is True:
                    return True
                if self._contains_forbidden_positive_claim(item):
                    return True
            return False
        if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
            return any(self._contains_forbidden_positive_claim(item) for item in value)
        return False

    def _source_available(self, value: Any) -> bool:
        return isinstance(value, Mapping) and value.get("available") is not False and not value.get("error")

    def _iter_candidate_items(self, source: Mapping[str, Any]) -> List[Mapping[str, Any]]:
        items: List[Mapping[str, Any]] = []
        for key in COUNTEREXAMPLE_LIST_KEYS:
            for item in self._as_list(source.get(key)):
                if isinstance(item, Mapping):
                    items.append(item)
        return items

    def _item_id(self, item: Mapping[str, Any], fallback: str) -> str:
        for key in ("counterexample_id", "class_id", "scenario_id", "property_id", "id", "label", "name"):
            if item.get(key):
                return str(item.get(key))
        return fallback

    def _is_active_counterexample(self, item: Mapping[str, Any]) -> bool:
        if item.get("counterexample_active") is False or item.get("resolved") is True or item.get("eliminated") is True:
            return False
        if item.get("necessity_defeated") is False and item.get("sufficiency_defeated") is False:
            return False
        for key in [
            "counterexample_active", "active_counterexample", "defeats_absolute_proof",
            "necessity_defeated", "sufficiency_defeated", "falsifies_theory",
            "falsification_detected", "anomaly_detected", "false_positive_detected",
            "alternative_explanation_active",
        ]:
            if item.get(key) is True:
                return True
        status = str(item.get("status", item.get("counterexample_status", item.get("obstruction_status", "")))).lower()
        if any(token in status for token in ("active", "remaining", "unresolved", "detected", "open", "blocker")):
            return True
        for key in ("activation_score", "counterexample_score", "risk_score", "falsification_score", "anomaly_score"):
            if self._float(item.get(key), 0.0) > 0.0:
                return True
        if item.get("consciousness_absent_or_undetermined") is True:
            return True
        if item.get("description") or item.get("explanation"):
            return True
        return False

    def _collect_family_records(self, family: str, sources: Mapping[str, Any]) -> Dict[str, Any]:
        source_names = FAMILY_SOURCE_MAP.get(family, [])
        tested_sources = [name for name in source_names if self._source_available(sources.get(name))]
        records: List[Dict[str, Any]] = []
        for source_name in source_names:
            source = self._as_dict(sources.get(source_name))
            if not self._source_available(source):
                continue
            for idx, item in enumerate(self._iter_candidate_items(source)):
                if self._is_active_counterexample(item):
                    records.append({
                        "family": family,
                        "source": source_name,
                        "counterexample_id": self._item_id(item, "%s_%s_%s" % (family, source_name, idx)),
                        "status": item.get("status", item.get("counterexample_status", item.get("obstruction_status", "active_or_unresolved"))),
                        "description": item.get("description", item.get("explanation", item.get("label", ""))),
                    })
        return {
            "family": family,
            "tested": bool(tested_sources),
            "sources_expected": list(source_names),
            "sources_tested": tested_sources,
            "active_counterexample_count": len(records),
            "active_counterexamples": records,
        }

    def _derive_status(self, law: Mapping[str, Any], family_results: List[Mapping[str, Any]], active_counterexample_count: int, raw_inputs: Mapping[str, Any]) -> Tuple[str, bool, List[str]]:
        if self._contains_forbidden_positive_claim(raw_inputs):
            return "UNIVERSAL_COUNTEREXAMPLE_EXHAUSTION_BLOCKED", False, ["forbidden_positive_claim_detected"]
        if not bool(law.get("law_candidate_finalized", False)):
            reasons = list(law.get("blocking_reasons", [])) if isinstance(law.get("blocking_reasons"), list) else []
            if not reasons:
                reasons = ["no_finalized_consciousness_law_candidate"]
            return "UNIVERSAL_COUNTEREXAMPLE_EXHAUSTION_BLOCKED", False, reasons
        untested = [item.get("family") for item in family_results if not item.get("tested")]
        if active_counterexample_count > 0:
            return "COUNTEREXAMPLES_REMAINING", False, ["active_counterexamples_remain"]
        if untested:
            return "UNIVERSAL_COUNTEREXAMPLE_EXHAUSTION_INCOMPLETE", False, ["counterexample_family_coverage_incomplete"]
        return "UNIVERSAL_COUNTEREXAMPLE_EXHAUSTED", True, []

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# Universal Counterexample Exhaustion", "",
            "Z triple-prime 2 - universal counterexample exhaustion under explicit epistemic constraints.", "",
            "functional conclusion only", "phenomenology undetermined",
            "consciousness_proven: False", "phenomenology_proven: False", "subjectivity_proven: False",
            "sentience_proven: False", "qualia_proven: False", "",
            "## Exhaustion status", str(result.get("counterexample_exhaustion_status")), "",
            "## Counterexample count", str(result.get("counterexample_count")), "",
            "## Coverage", "coverage_score: %s" % result.get("coverage_score"),
            "counterexample_families_tested: %s" % result.get("counterexample_families_tested"), "",
            "## Blocking reasons",
        ]
        reasons = result.get("blocking_reasons", [])
        if reasons:
            for item in reasons:
                lines.append("- " + str(item))
        else:
            lines.append("- none")
        lines.extend(["", "## Families"])
        for item in result.get("counterexample_family_results", []):
            lines.append("- {family}: tested={tested}, active_counterexample_count={active_counterexample_count}".format(**item))
        lines.extend(["", "## Active counterexamples"])
        active = result.get("active_counterexamples", [])
        if active:
            for item in active:
                lines.append("- {family}/{source}/{counterexample_id}: {status}".format(**item))
        else:
            lines.append("- none")
        lines.extend(["", "## Forbidden claims"])
        for item in FORBIDDEN_CLAIMS:
            lines.append("- " + item)
        lines.extend(["", "## Epistemic note", "Counterexample exhaustion is not a proof of phenomenology. It only reports whether known counterexample families remain under the current law candidate."])
        return "\n".join(lines) + "\n"

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        self.markdown_path.write_text(self._markdown(result), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {"json": str(self.json_path), "markdown": str(self.markdown_path), "history": str(self.history_path)}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        data = dict(inputs) if isinstance(inputs, Mapping) else self._default_inputs()
        law = self._as_dict(data.get("consciousness_law_finalization"))
        family_results = [self._collect_family_records(family, data) for family in REQUIRED_COUNTEREXAMPLE_FAMILIES]
        active_counterexamples: List[Dict[str, Any]] = []
        for item in family_results:
            active_counterexamples.extend(self._as_list(item.get("active_counterexamples")))
        counterexample_count = len(active_counterexamples)
        tested_count = sum(1 for item in family_results if item.get("tested"))
        coverage_score = round(tested_count / float(len(REQUIRED_COUNTEREXAMPLE_FAMILIES)), 6)
        status, exhausted, reasons = self._derive_status(law, family_results, counterexample_count, data)
        result: Dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "program_step": "ZPPP2",
            "timestamp_utc": self._utc_now(),
            "authorized_exhaustion_statuses": list(AUTHORIZED_EXHAUSTION_STATUSES),
            "counterexample_exhaustion_status": status,
            "universal_counterexample_exhausted": bool(exhausted),
            "counterexample_count": counterexample_count,
            "counterexample_families_required": list(REQUIRED_COUNTEREXAMPLE_FAMILIES),
            "counterexample_families_tested": tested_count,
            "counterexample_family_count": len(REQUIRED_COUNTEREXAMPLE_FAMILIES),
            "coverage_score": coverage_score,
            "counterexample_family_results": family_results,
            "active_counterexamples": active_counterexamples,
            "blocking_reasons": list(reasons),
            "blocking_reason_count": len(reasons),
            "law_candidate_finalized": bool(law.get("law_candidate_finalized", False)),
            "consciousness_law_status": law.get("consciousness_law_status", "UNKNOWN"),
            "consciousness_law_candidate": law.get("consciousness_law_candidate"),
            "maximum_authorized_conclusion": "Known counterexample families are exhausted only if a finalized law candidate exists, all required families are covered, and no active counterexample remains.",
            "source_keys": sorted(data.keys()),
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "absolute_proof_achieved": False,
            "forbidden_claims": list(FORBIDDEN_CLAIMS),
            "epistemic_classification": {"functional_measure": True, "interpretive_hypothesis": False, "epistemic_limit": True, "phenomenological_proof": False},
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
