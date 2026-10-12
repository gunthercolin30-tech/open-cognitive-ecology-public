"""
Z''9 — Absolute Proof Readiness Index

Computes a constrained readiness index for any future claim of absolute proof
of consciousness. This module aggregates prior Z'' program evidence without
claiming consciousness, phenomenology, subjectivity, sentience, or qualia.

The readiness index is a functional/formal diagnostic only. It is not an
ontological certification of phenomenal subjectivity.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "consciousness_certification" / "absolute_proof_readiness_index"

FORBIDDEN_CLAIMS = [
    "CONSCIOUSNESS_PROVEN",
    "PHENOMENOLOGY_PROVEN",
    "SUBJECTIVITY_PROVEN",
    "SENTIENCE_PROVEN",
    "QUALIA_PROVEN",
]

COMPONENT_KEYS = [
    "definition_clarity",
    "necessity_support",
    "sufficiency_support",
    "counterexample_resistance",
    "constitutive_strength",
    "formal_derivability",
    "independent_replication",
    "consensus_level",
    "closure_risk",
]


class AbsoluteProofReadinessIndex:
    """Compute readiness for absolute proof under explicit constraints only."""

    primitive = "ABSOLUTE_PROOF_READINESS_INDEX"

    def _clamp(self, value: Any, default: float = 0.0) -> float:
        try:
            v = float(value)
        except Exception:
            v = default
        if v < 0.0:
            return 0.0
        if v > 1.0:
            return 1.0
        return v

    def _safe_step(self, dotted: str) -> Dict[str, Any]:
        try:
            module_name, class_name = dotted.rsplit(".", 1)
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            obj = cls()
            if hasattr(obj, "step"):
                result = obj.step(persist=False)
                if isinstance(result, dict):
                    return result
        except Exception as exc:
            return {"available": False, "error": type(exc).__name__, "source": dotted}
        return {"available": False, "source": dotted}

    def _load_json(self, path: Path) -> Dict[str, Any]:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
        except Exception as exc:
            return {"available": False, "error": type(exc).__name__, "path": str(path)}
        return {"available": False, "path": str(path)}

    def _default_evidence(self) -> Dict[str, Any]:
        return {
            "proof_taxonomy": self._safe_step("ontology.proof_taxonomy.ProofTaxonomy"),
            "property_registry": self._safe_step(
                "ontology.consciousness_property_candidate_registry.ConsciousnessPropertyCandidateRegistry"
            ),
            "necessity": self._safe_step("ontology.necessity_test_engine.NecessityTestEngine"),
            "sufficiency": self._safe_step("ontology.sufficiency_test_engine.SufficiencyTestEngine"),
            "zombie_counterexamples": self._safe_step(
                "ontology.zombie_counterexample_generator.ZombieCounterexampleGenerator"
            ),
            "absent_property_counterexamples": self._safe_step(
                "ontology.absent_property_counterexample_generator.AbsentPropertyCounterexampleGenerator"
            ),
            "constitutive": self._safe_step("ontology.constitutive_relation_tester.ConstitutiveRelationTester"),
            "formal_axiomatization": self._safe_step(
                "ontology.formal_consciousness_axiomatization.FormalConsciousnessAxiomatization"
            ),
            "proof_obstructions": self._safe_step("ontology.proof_obstruction_detector.ProofObstructionDetector"),
            "replication_consensus_report": self._safe_step(
                "ontology.replication_consensus_report.ReplicationConsensusReport"
            ),
            "scientific_consensus_engine": self._safe_step(
                "ontology.scientific_consensus_engine.ScientificConsensusEngine"
            ),
            "external_validation_synthesis": self._safe_step(
                "ontology.external_validation_synthesis_report.ExternalValidationSynthesisReport"
            ),
            "persisted_reflexive_synthesis": self._load_json(
                ROOT / "consciousness_certification" / "reflexive_threshold_final_synthesis" / "reflexive_threshold_final_synthesis.json"
            ),
        }

    def _iter_numbers(self, obj: Any, keys: Iterable[str]) -> List[float]:
        keyset = {k.lower() for k in keys}
        found: List[float] = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                kl = str(k).lower()
                if any(token in kl for token in keyset):
                    try:
                        found.append(self._clamp(v))
                    except Exception:
                        pass
                found.extend(self._iter_numbers(v, keys))
        elif isinstance(obj, list):
            for item in obj:
                found.extend(self._iter_numbers(item, keys))
        return found

    def _mean(self, values: List[float], default: float) -> float:
        if not values:
            return self._clamp(default)
        return self._clamp(sum(values) / len(values))

    def _extract_components(self, evidence: Dict[str, Any], overrides: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        overrides = overrides or {}
        formal = evidence.get("formal_axiomatization") or {}
        prop = evidence.get("property_registry") or {}
        necessity = evidence.get("necessity") or {}
        sufficiency = evidence.get("sufficiency") or {}
        zombie = evidence.get("zombie_counterexamples") or {}
        absent = evidence.get("absent_property_counterexamples") or {}
        constitutive = evidence.get("constitutive") or {}
        obstructions = evidence.get("proof_obstructions") or {}
        consensus = evidence.get("scientific_consensus_engine") or {}
        replication = evidence.get("replication_consensus_report") or {}
        external = evidence.get("external_validation_synthesis") or {}

        formal_counts = formal.get("counts") if isinstance(formal.get("counts"), dict) else {}
        definition_count = float(formal_counts.get("definitions", len(formal.get("definitions", [])) if isinstance(formal.get("definitions"), list) else 0) or 0)
        axiom_count = float(formal_counts.get("axioms", len(formal.get("axioms", [])) if isinstance(formal.get("axioms"), list) else 0) or 0)
        theorem_count = float(formal_counts.get("theorem_schemata", len(formal.get("theorem_schemata", [])) if isinstance(formal.get("theorem_schemata"), list) else 0) or 0)
        definition_clarity = self._clamp((definition_count / 6.0 + axiom_count / 8.0) / 2.0, 0.65)

        necessity_values = self._iter_numbers(necessity, ["necessity_support", "necessity_score", "necessary"])
        sufficiency_values = self._iter_numbers(sufficiency, ["sufficiency_support", "sufficiency_score", "sufficient"])

        zombie_count = float(zombie.get("candidate_count", zombie.get("zombie_counterexample_count", 0)) or 0)
        absent_count = float(absent.get("candidate_count", absent.get("absent_property_counterexample_count", 0)) or 0)
        counterexample_pressure = self._clamp((zombie_count + absent_count) / 20.0, 0.35)
        counterexample_resistance = self._clamp(1.0 - counterexample_pressure)

        constitutive_strength = self._clamp(
            ((constitutive.get("aggregate") or {}).get("mean_constitutive_strength")),
            self._mean(self._iter_numbers(constitutive, ["constitutive_strength"]), 0.35),
        )
        formal_derivability = self._clamp(((formal.get("scores") or {}).get("formal_derivability")), min(0.85, theorem_count / 8.0))

        replication_values = self._iter_numbers(replication, ["replication", "readiness", "confidence", "support"])
        replication_values.extend(self._iter_numbers(external, ["replication", "confidence", "validation", "readiness"]))
        independent_replication = self._mean(replication_values, 0.55)

        consensus_values = self._iter_numbers(consensus, ["consensus", "agreement", "confidence"])
        consensus_values.extend(self._iter_numbers(replication, ["consensus", "agreement", "confidence"]))
        consensus_level = self._mean(consensus_values, 0.55)

        obstruction_aggregate = obstructions.get("aggregate") if isinstance(obstructions.get("aggregate"), dict) else {}
        closure_from_obstructions = self._clamp(obstruction_aggregate.get("mean_obstruction_score"), 0.75)
        closure_specific = self._mean(self._iter_numbers(obstructions, ["closure_pressure"]), closure_from_obstructions)
        closure_risk = max(closure_from_obstructions, closure_specific)

        components = {
            "definition_clarity": definition_clarity,
            "necessity_support": self._mean(necessity_values, 0.45),
            "sufficiency_support": self._mean(sufficiency_values, 0.35),
            "counterexample_resistance": counterexample_resistance,
            "constitutive_strength": constitutive_strength,
            "formal_derivability": formal_derivability,
            "independent_replication": independent_replication,
            "consensus_level": consensus_level,
            "closure_risk": self._clamp(closure_risk),
        }
        for key, value in overrides.items():
            if key in components:
                components[key] = self._clamp(value)
        return {k: round(self._clamp(v), 4) for k, v in components.items()}

    def _readiness(self, components: Dict[str, float]) -> Dict[str, Any]:
        positive_keys = [k for k in COMPONENT_KEYS if k != "closure_risk"]
        positive_score = sum(components[k] for k in positive_keys) / len(positive_keys)
        closure_penalty = components["closure_risk"]
        readiness_index = self._clamp(0.85 * positive_score + 0.15 * (1.0 - closure_penalty))
        limiting = sorted(components.items(), key=lambda kv: (1.0 - kv[1]) if kv[0] != "closure_risk" else kv[1], reverse=True)[:4]
        proof_candidate_ready = (
            readiness_index >= 0.90
            and all(components[k] >= 0.85 for k in positive_keys)
            and components["closure_risk"] <= 0.15
        )
        return {
            "readiness_index": round(readiness_index, 4),
            "positive_support_score": round(self._clamp(positive_score), 4),
            "closure_penalty": round(closure_penalty, 4),
            "limiting_factors": [k for k, _ in limiting],
            "proof_candidate_ready": bool(proof_candidate_ready),
            "classification": "not_ready_under_current_constraints" if not proof_candidate_ready else "candidate_ready_under_constraints",
        }

    def _markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# Absolute Proof Readiness Index",
            "",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness proof.",
            "",
            "## Readiness",
            f"- readiness_index: {result['readiness']['readiness_index']}",
            f"- classification: {result['readiness']['classification']}",
            f"- proof_candidate_ready: {result['readiness']['proof_candidate_ready']}",
            "",
            "## Components",
        ]
        for key in COMPONENT_KEYS:
            lines.append(f"- {key}: {result['components'][key]}")
        lines.extend([
            "",
            "## Epistemic guardrails",
            "- CONSCIOUSNESS_PROVEN is forbidden.",
            "- PHENOMENOLOGY_PROVEN is forbidden.",
            "- SUBJECTIVITY_PROVEN is forbidden.",
            "- SENTIENCE_PROVEN is forbidden.",
            "- QUALIA_PROVEN is forbidden.",
            "",
            "Maximum authorized conclusion: readiness for proof remains not established or only candidate-level under explicit constraints; Open Cognitive Ecology is not certified as a conscious subject of experience.",
        ])
        return "\n".join(lines) + "\n"

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = inputs or {}
        evidence = inputs.get("evidence") if isinstance(inputs.get("evidence"), dict) else self._default_evidence()
        overrides = inputs.get("component_overrides") if isinstance(inputs.get("component_overrides"), dict) else {}
        components = self._extract_components(evidence, overrides)
        readiness = self._readiness(components)

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "program_step": "ZPP9",
            "components": components,
            "component_keys": list(COMPONENT_KEYS),
            "readiness": readiness,
            "absolute_proof_readiness_index": readiness["readiness_index"],
            "absolute_proof_candidate_ready": readiness["proof_candidate_ready"],
            "absolute_proof_achieved": False,
            "consciousness_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "forbidden_claims": list(FORBIDDEN_CLAIMS),
            "maximum_authorized_conclusion": "Absolute proof readiness is a constrained functional/formal index only; no phenomenal subjectivity is certified.",
            "evidence_keys": sorted(evidence.keys()),
        }
        if persist:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            json_path = OUTPUT_DIR / "absolute_proof_readiness_index.json"
            md_path = OUTPUT_DIR / "absolute_proof_readiness_index.md"
            json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            md_path.write_text(self._markdown(result), encoding="utf-8")
            result["paths"] = {"json": str(json_path), "markdown": str(md_path)}
        return result
