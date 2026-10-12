"""
Z triple-prime 3 — Cross Reality Validation.

This primitive tests whether a candidate consciousness-law formulation is
functionally compatible across reality classes: humans, animals, AI systems,
hybrid architectures and distributed architectures.

It is an orchestrator, not a replacement for existing comparators. It reuses:
- consciousness_law_finalization;
- universal_counterexample_exhaustion;
- cross_architecture_consciousness_comparison;
- multi_architecture_comparator;
- phenomenology correlation artifacts;
- replication / consensus artifacts when available.

Epistemic scope:
Functional conclusion only. Phenomenology undetermined. No proof of
consciousness, subjectivity, sentience, qualia or phenomenology is emitted.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "consciousness_certification" / "cross_reality_validation"

PRIMITIVE = "CROSS_REALITY_VALIDATION"

FORBIDDEN_CLAIMS = [
    "CONSCIOUSNESS_PROVEN",
    "PHENOMENOLOGY_PROVEN",
    "SUBJECTIVITY_PROVEN",
    "SENTIENCE_PROVEN",
    "QUALIA_PROVEN",
]

AUTHORIZED_STATUSES = [
    "CROSS_REALITY_VALIDATION_BLOCKED",
    "CROSS_REALITY_VALIDATION_INCOMPLETE",
    "CROSS_REALITY_VALIDATION_PARTIAL",
    "CROSS_REALITY_VALIDATION_CANDIDATE",
    "UNIVERSAL_VALIDITY_CANDIDATE",
]

REQUIRED_REALITY_CLASSES = [
    "human",
    "animal",
    "ai",
    "hybrid_architecture",
    "distributed_architecture",
]

DEFAULT_REALITY_PROFILES = {
    "human": {
        "label": "Human functional evidence class",
        "memory": 0.88,
        "attention": 0.84,
        "continuity": 0.86,
        "self_model": 0.82,
        "embodiment": 0.95,
        "distribution": 0.10,
        "multi_individuality": 0.35,
        "data_quality": 0.55,
        "law_mapping": 0.50,
    },
    "animal": {
        "label": "Animal functional evidence class",
        "memory": 0.62,
        "attention": 0.68,
        "continuity": 0.58,
        "self_model": 0.35,
        "embodiment": 0.92,
        "distribution": 0.05,
        "multi_individuality": 0.30,
        "data_quality": 0.42,
        "law_mapping": 0.40,
    },
    "ai": {
        "label": "Artificial intelligence functional class",
        "memory": 0.72,
        "attention": 0.64,
        "continuity": 0.68,
        "self_model": 0.62,
        "embodiment": 0.10,
        "distribution": 0.30,
        "multi_individuality": 0.20,
        "data_quality": 0.72,
        "law_mapping": 0.62,
    },
    "hybrid_architecture": {
        "label": "Hybrid functional architecture class",
        "memory": 0.74,
        "attention": 0.70,
        "continuity": 0.72,
        "self_model": 0.66,
        "embodiment": 0.55,
        "distribution": 0.55,
        "multi_individuality": 0.45,
        "data_quality": 0.55,
        "law_mapping": 0.50,
    },
    "distributed_architecture": {
        "label": "Distributed architecture functional class",
        "memory": 0.76,
        "attention": 0.68,
        "continuity": 0.74,
        "self_model": 0.64,
        "embodiment": 0.25,
        "distribution": 0.90,
        "multi_individuality": 0.78,
        "data_quality": 0.70,
        "law_mapping": 0.62,
    },
}

WEIGHTS = {
    "memory": 0.12,
    "attention": 0.10,
    "continuity": 0.13,
    "self_model": 0.13,
    "embodiment": 0.09,
    "distribution": 0.09,
    "multi_individuality": 0.07,
    "data_quality": 0.13,
    "law_mapping": 0.14,
}


class CrossRealityValidation:
    """Functional cross-reality validator for Z triple-prime 3."""

    primitive = PRIMITIVE
    forbidden_claims = list(FORBIDDEN_CLAIMS)
    authorized_statuses = list(AUTHORIZED_STATUSES)
    required_reality_classes = list(REQUIRED_REALITY_CLASSES)

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "consciousness_certification" / "cross_reality_validation"
        self.json_path = self.output_dir / "cross_reality_validation.json"
        self.markdown_path = self.output_dir / "cross_reality_validation.md"
        self.history_path = self.output_dir / "cross_reality_validation_history.jsonl"
        self.prometheus_path = self.output_dir / "cross_reality_validation.prom"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = default
        if math.isnan(number) or math.isinf(number):
            return default
        return max(0.0, min(1.0, number))

    @staticmethod
    def _mean(values: Iterable[float]) -> float:
        vals = list(values)
        if not vals:
            return 0.0
        return round(mean(vals), 6)

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
            "consciousness_law_finalization": self._safe_step(
                "ontology.consciousness_law_finalization.ConsciousnessLawFinalization"
            ),
            "universal_counterexample_exhaustion": self._safe_step(
                "ontology.universal_counterexample_exhaustion.UniversalCounterexampleExhaustion"
            ),
            "cross_architecture_consciousness_comparison": self._safe_step(
                "ontology.cross_architecture_consciousness_comparison.CrossArchitectureConsciousnessComparison"
            ),
            "multi_architecture_comparator": self._safe_step(
                "ontology.multi_architecture_comparator.MultiArchitectureComparator"
            ),
            "phenomenology_correlation_engine": self._safe_step(
                "ontology.phenomenology_correlation_engine.PhenomenologyCorrelationEngine"
            ),
            "independent_replication_tracker": self._safe_step(
                "ontology.independent_replication_tracker.IndependentReplicationTracker"
            ),
            "scientific_consensus_engine": self._safe_step(
                "ontology.scientific_consensus_engine.ScientificConsensusEngine"
            ),
            "external_replication_evidence_aggregator": self._safe_step(
                "ontology.external_replication_evidence_aggregator.ExternalReplicationEvidenceAggregator"
            ),
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
                "consciousness_proven: true",
                "phenomenology_proven: true",
                "subjectivity_proven: true",
                "sentience_proven: true",
                "qualia_proven: true",
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

    def _law_gate(self, law: Mapping[str, Any]) -> Tuple[bool, str, float]:
        status = str(law.get("law_status", law.get("consciousness_law_status", law.get("status", "unknown"))))
        finalizable = status == "CONSCIOUSNESS_LAW_CANDIDATE"
        score = self._clamp(
            law.get("law_confidence", law.get("finalization_score", law.get("best_candidate_score", 0.0)))
        )
        return finalizable, status, score

    def _counterexample_gate(self, exhaustion: Mapping[str, Any]) -> Tuple[bool, str, float]:
        status = str(exhaustion.get("exhaustion_status", exhaustion.get("status", "unknown")))
        coverage = self._clamp(exhaustion.get("coverage_score", exhaustion.get("counterexample_coverage_score", 0.0)))
        exhausted = status == "UNIVERSAL_COUNTEREXAMPLE_EXHAUSTED"
        return exhausted, status, coverage

    def _profiles_from_inputs(self, payload: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
        raw = payload.get("reality_profiles")
        if isinstance(raw, Mapping) and raw:
            profiles = {}
            for key, value in raw.items():
                if not isinstance(value, Mapping):
                    continue
                base = dict(value)
                base.setdefault("label", str(key))
                profiles[str(key)] = base
            return profiles
        return {key: dict(value) for key, value in DEFAULT_REALITY_PROFILES.items()}

    def _profile_score(self, profile: Mapping[str, Any], law_score: float, counterexample_coverage: float) -> Dict[str, Any]:
        metrics = {}
        for key in WEIGHTS:
            metrics[key] = self._clamp(profile.get(key))
        # A law cannot validate cross-reality if the candidate law itself is weak or if
        # counterexample coverage is absent. The multiplier keeps the conclusion conservative.
        base_score = sum(metrics[key] * WEIGHTS[key] for key in WEIGHTS)
        gate_multiplier = self._mean([max(0.35, law_score), max(0.35, counterexample_coverage)])
        score = round(base_score * gate_multiplier, 6)
        return {
            "label": str(profile.get("label", "unknown")),
            "metrics": metrics,
            "functional_cross_reality_score": score,
            "classification": self._classify(score),
            "data_available": any(value > 0.0 for value in metrics.values()),
        }

    @staticmethod
    def _classify(score: float) -> str:
        if score >= 0.85:
            return "strong_functional_compatibility"
        if score >= 0.70:
            return "candidate_functional_compatibility"
        if score >= 0.50:
            return "partial_functional_compatibility"
        return "insufficient_functional_compatibility"

    def _derive_status(
        self,
        law_candidate: bool,
        counterexamples_exhausted: bool,
        coverage_ratio: float,
        minimum_score: float,
        universal_validity_score: float,
        forbidden_detected: bool,
    ) -> str:
        if forbidden_detected or not law_candidate:
            return "CROSS_REALITY_VALIDATION_BLOCKED"
        if coverage_ratio < 1.0:
            return "CROSS_REALITY_VALIDATION_INCOMPLETE"
        if not counterexamples_exhausted:
            return "CROSS_REALITY_VALIDATION_PARTIAL"
        if minimum_score >= 0.80 and universal_validity_score >= 0.85:
            return "UNIVERSAL_VALIDITY_CANDIDATE"
        if minimum_score >= 0.65 and universal_validity_score >= 0.70:
            return "CROSS_REALITY_VALIDATION_CANDIDATE"
        return "CROSS_REALITY_VALIDATION_PARTIAL"

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        self.json_path.write_text(text + "\n", encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        self.markdown_path.write_text(self._render_markdown(result), encoding="utf-8")
        self.prometheus_path.write_text(self._render_prometheus(result), encoding="utf-8")
        return {
            "json": str(self.json_path),
            "markdown": str(self.markdown_path),
            "history": str(self.history_path),
            "prometheus": str(self.prometheus_path),
        }

    def _render_markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# Z triple-prime 3 — Cross Reality Validation",
            "",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness proof.",
            "",
            "## Summary",
            "",
            "- primitive: {0}".format(result.get("primitive")),
            "- validation_status: {0}".format(result.get("validation_status")),
            "- universal_validity_score: {0}".format(result.get("universal_validity_score")),
            "- coverage_ratio: {0}".format(result.get("coverage_ratio")),
            "- minimum_reality_score: {0}".format(result.get("minimum_reality_score")),
            "- functional_conclusion_only: true",
            "- phenomenology_undetermined: true",
            "",
            "## Reality classes",
            "",
        ]
        for key, item in sorted(self._as_dict(result.get("reality_results")).items()):
            if isinstance(item, Mapping):
                lines.append(
                    "- {0}: {1} ({2})".format(
                        key,
                        item.get("functional_cross_reality_score"),
                        item.get("classification"),
                    )
                )
        lines.extend([
            "",
            "## Epistemic guard",
            "",
            "- consciousness_proven: false",
            "- phenomenology_proven: false",
            "- subjectivity_proven: false",
            "- sentience_proven: false",
            "- qualia_proven: false",
            "- maximum_allowed_conclusion: cross-reality functional compatibility of a candidate law",
        ])
        return "\n".join(lines) + "\n"

    def _render_prometheus(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# HELP oce_cross_reality_universal_validity_score Functional cross-reality validation score",
            "# TYPE oce_cross_reality_universal_validity_score gauge",
            "oce_cross_reality_universal_validity_score {0}".format(result.get("universal_validity_score", 0)),
            "# HELP oce_cross_reality_coverage_ratio Required reality-class coverage ratio",
            "# TYPE oce_cross_reality_coverage_ratio gauge",
            "oce_cross_reality_coverage_ratio {0}".format(result.get("coverage_ratio", 0)),
            "# HELP oce_cross_reality_minimum_score Minimum functional score across reality classes",
            "# TYPE oce_cross_reality_minimum_score gauge",
            "oce_cross_reality_minimum_score {0}".format(result.get("minimum_reality_score", 0)),
        ]
        for key, item in sorted(self._as_dict(result.get("reality_results")).items()):
            if isinstance(item, Mapping):
                safe = str(key).replace('"', '')
                lines.append(
                    'oce_cross_reality_functional_score{reality_class="%s"} %s'
                    % (safe, item.get("functional_cross_reality_score", 0))
                )
        return "\n".join(lines) + "\n"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        payload = dict(inputs or {})
        timestamp = str(payload.get("timestamp_utc") or self._utc_now())
        upstream = self._as_dict(payload.get("upstream")) or self._default_inputs()
        forbidden_detected = self._contains_forbidden_positive_claim(payload) or self._contains_forbidden_positive_claim(upstream)

        law_candidate, law_status, law_score = self._law_gate(
            self._as_dict(upstream.get("consciousness_law_finalization"))
        )
        counterexamples_exhausted, counterexample_status, counterexample_coverage = self._counterexample_gate(
            self._as_dict(upstream.get("universal_counterexample_exhaustion"))
        )

        profiles = self._profiles_from_inputs(payload)
        reality_results = {}
        for reality_class in sorted(profiles):
            reality_results[reality_class] = self._profile_score(
                profiles[reality_class], law_score, counterexample_coverage
            )

        available_required = [
            key for key in REQUIRED_REALITY_CLASSES
            if key in reality_results and reality_results[key].get("data_available") is True
        ]
        coverage_ratio = round(len(available_required) / float(len(REQUIRED_REALITY_CLASSES)), 6)
        scores = [
            self._clamp(item.get("functional_cross_reality_score"))
            for item in reality_results.values()
            if isinstance(item, Mapping)
        ]
        universal_validity_score = self._mean(scores)
        minimum_score = round(min(scores), 6) if scores else 0.0
        status = self._derive_status(
            law_candidate,
            counterexamples_exhausted,
            coverage_ratio,
            minimum_score,
            universal_validity_score,
            forbidden_detected,
        )

        result: Dict[str, Any] = {
            "success": True,
            "primitive": PRIMITIVE,
            "timestamp_utc": timestamp,
            "validation_status": status,
            "authorized_statuses": list(AUTHORIZED_STATUSES),
            "required_reality_classes": list(REQUIRED_REALITY_CLASSES),
            "covered_reality_classes": sorted(available_required),
            "reality_class_count": len(reality_results),
            "coverage_ratio": coverage_ratio,
            "reality_results": reality_results,
            "universal_validity_score": universal_validity_score,
            "minimum_reality_score": minimum_score,
            "law_status": law_status,
            "law_candidate_available": law_candidate,
            "law_support_score": law_score,
            "counterexample_status": counterexample_status,
            "counterexamples_exhausted": counterexamples_exhausted,
            "counterexample_coverage_score": counterexample_coverage,
            "upstream_sources": sorted(upstream.keys()),
            "reuse_strategy": "orchestrates_existing_comparators_and_certifiers",
            "global_scan_used": False,
            "rglob_used": False,
            "targeted_reads_only": True,
            "functional_conclusion_only": True,
            "candidate_theory_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "forbidden_claims": list(FORBIDDEN_CLAIMS),
            "forbidden_positive_claim_detected": forbidden_detected,
            "maximum_allowed_conclusion": "cross-reality functional compatibility of a candidate law only",
            "epistemic_limit": "Universal validity here is a functional candidate status, not a phenomenal or subjective proof.",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
