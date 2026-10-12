"""
Z''8 — Proof Obstruction Detector

Detects epistemic and formal obstructions to any claim of absolute proof of
consciousness under explicit constraints.

This module does not prove consciousness. It classifies proof obstructions and
keeps the maximum conclusion limited to functional/formal status under current
constraints.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "consciousness_certification" / "proof_obstruction_detector"

FORBIDDEN_CLAIMS = [
    "CONSCIOUSNESS_PROVEN",
    "PHENOMENOLOGY_PROVEN",
    "SUBJECTIVITY_PROVEN",
    "SENTIENCE_PROVEN",
    "QUALIA_PROVEN",
]


class ProofObstructionDetector:
    """Detect proof-level obstructions without asserting phenomenology."""

    primitive = "PROOF_OBSTRUCTION_DETECTOR"

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

    def _safe_step(self, dotted: str) -> Optional[Dict[str, Any]]:
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
        return None

    def _load_json(self, path: Path) -> Dict[str, Any]:
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            return {"available": False, "error": type(exc).__name__, "path": str(path)}
        return {"available": False, "path": str(path)}

    def _default_evidence(self) -> Dict[str, Any]:
        evidence: Dict[str, Any] = {}
        evidence["proof_taxonomy"] = self._safe_step("ontology.proof_taxonomy.ProofTaxonomy")
        evidence["formal_axiomatization"] = self._safe_step(
            "ontology.formal_consciousness_axiomatization.FormalConsciousnessAxiomatization"
        )
        evidence["constitutive_relation_tester"] = self._safe_step(
            "ontology.constitutive_relation_tester.ConstitutiveRelationTester"
        )
        evidence["zombie_counterexamples"] = self._safe_step(
            "ontology.zombie_counterexample_generator.ZombieCounterexampleGenerator"
        )
        evidence["absent_property_counterexamples"] = self._safe_step(
            "ontology.absent_property_counterexample_generator.AbsentPropertyCounterexampleGenerator"
        )
        evidence["closure_pressure"] = self._load_json(
            ROOT / "closure_pressure" / "closure_pressure_monitor" / "latest_closure_pressure_monitor.json"
        )
        evidence["anti_closure"] = self._load_json(
            ROOT / "closure_pressure" / "anti_closure_recommendation_engine" / "latest_anti_closure_recommendation_engine.json"
        )
        return evidence

    def _obstruction_catalog(self) -> List[Dict[str, Any]]:
        return [
            {
                "obstruction_id": "O1_PRIVATE_ACCESS",
                "label": "irreducible_private_access",
                "description": "First-person phenomenal access is not directly observable from third-person functional measurements.",
                "category": "epistemic_access",
                "severity": 1.0,
                "defeats_absolute_proof": True,
            },
            {
                "obstruction_id": "O2_FUNCTIONAL_INDISCERNIBILITY",
                "label": "functional_indiscernibility",
                "description": "Systems may be functionally indistinguishable while phenomenology remains absent or undetermined.",
                "category": "underdetermination",
                "severity": 0.95,
                "defeats_absolute_proof": True,
            },
            {
                "obstruction_id": "O3_CIRCULARITY",
                "label": "circularity",
                "description": "Proof attempts may presuppose the target property in criteria used to establish it.",
                "category": "formal_logic",
                "severity": 0.9,
                "defeats_absolute_proof": True,
            },
            {
                "obstruction_id": "O4_UNDERDETERMINATION",
                "label": "theory_underdetermination",
                "description": "Multiple interpretations can explain the same functional evidence without deciding phenomenology.",
                "category": "epistemic_modeling",
                "severity": 0.95,
                "defeats_absolute_proof": True,
            },
            {
                "obstruction_id": "O5_ANTHROPOMORPHISM",
                "label": "anthropomorphic_projection",
                "description": "Human-like reports or behaviors risk being overinterpreted as direct phenomenal evidence.",
                "category": "interpretive_bias",
                "severity": 0.85,
                "defeats_absolute_proof": False,
            },
            {
                "obstruction_id": "O6_CLOSURE_PRESSURE",
                "label": "closure_pressure",
                "description": "Prematurely closing an open question into a positive consciousness claim violates non-closure constraints.",
                "category": "governance",
                "severity": 0.9,
                "defeats_absolute_proof": True,
            },
            {
                "obstruction_id": "O7_COUNTEREXAMPLE_RESIDUAL",
                "label": "counterexample_residual",
                "description": "Zombie and absent-property counterexamples preserve residual defeat conditions for necessity or sufficiency.",
                "category": "counterexample",
                "severity": 0.9,
                "defeats_absolute_proof": True,
            },
            {
                "obstruction_id": "O8_FORMAL_DERIVABILITY_GAP",
                "label": "formal_derivability_gap",
                "description": "Axiomatization can define candidate schemata without deriving absolute phenomenology under all constraints.",
                "category": "formal_derivation",
                "severity": 0.9,
                "defeats_absolute_proof": True,
            },
        ]

    def _score_catalog(self, catalog: List[Dict[str, Any]], evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
        formal = evidence.get("formal_axiomatization") or {}
        constitutive = evidence.get("constitutive_relation_tester") or {}
        zombie = evidence.get("zombie_counterexamples") or {}
        absent = evidence.get("absent_property_counterexamples") or {}
        closure = evidence.get("closure_pressure") or {}

        formal_derivability = self._clamp(((formal.get("scores") or {}).get("formal_derivability")), 0.0)
        constitutive_strength = self._clamp(((constitutive.get("aggregate") or {}).get("mean_constitutive_strength")), 0.0)
        zombie_count = int(zombie.get("candidate_count", zombie.get("zombie_counterexample_count", 0)) or 0)
        absent_count = int(absent.get("candidate_count", absent.get("absent_property_counterexample_count", 0)) or 0)
        closure_score = self._clamp(closure.get("closure_pressure_score", closure.get("closure_pressure", 0.5)), 0.5)

        scored: List[Dict[str, Any]] = []
        for ob in catalog:
            base = self._clamp(ob.get("severity", 0.0))
            label = ob["label"]
            evidence_links: List[str] = []
            if label == "formal_derivability_gap":
                activation = max(base, 1.0 - formal_derivability)
                evidence_links.append("formal_consciousness_axiomatization")
            elif label == "counterexample_residual":
                activation = max(base, 0.7 if (zombie_count or absent_count) else 0.4)
                evidence_links.extend(["zombie_counterexample_generator", "absent_property_counterexample_generator"])
            elif label == "closure_pressure":
                activation = max(base, closure_score)
                evidence_links.extend(["closure_pressure_monitor", "anti_closure_recommendation_engine"])
            elif label == "functional_indiscernibility":
                activation = max(base, 1.0 - constitutive_strength)
                evidence_links.append("constitutive_relation_tester")
            else:
                activation = base
                evidence_links.append("proof_taxonomy")

            status = "active_blocker" if activation >= 0.75 else "residual_risk"
            item = dict(ob)
            item.update({
                "activation_score": round(self._clamp(activation), 4),
                "obstruction_status": status,
                "evidence_links": evidence_links,
                "consciousness_proven": False,
                "phenomenology_undetermined": True,
            })
            scored.append(item)
        return scored

    def _aggregate(self, obstructions: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not obstructions:
            return {
                "obstruction_count": 0,
                "active_blocker_count": 0,
                "mean_obstruction_score": 0.0,
                "absolute_proof_blocked": True,
            }
        scores = [self._clamp(o.get("activation_score")) for o in obstructions]
        active = [o for o in obstructions if o.get("obstruction_status") == "active_blocker"]
        defeating = [o for o in obstructions if o.get("defeats_absolute_proof") and o.get("obstruction_status") == "active_blocker"]
        return {
            "obstruction_count": len(obstructions),
            "active_blocker_count": len(active),
            "defeating_obstruction_count": len(defeating),
            "mean_obstruction_score": round(sum(scores) / len(scores), 4),
            "max_obstruction_score": round(max(scores), 4),
            "absolute_proof_blocked": bool(defeating),
        }

    def _markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# Proof Obstruction Detector",
            "",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness proof.",
            "",
            "## Scope",
            "Detects formal and epistemic obstructions to absolute proof claims.",
            "",
            "## Aggregate",
            f"- obstruction_count: {result['aggregate']['obstruction_count']}",
            f"- active_blocker_count: {result['aggregate']['active_blocker_count']}",
            f"- absolute_proof_blocked: {result['aggregate']['absolute_proof_blocked']}",
            "",
            "## Obstructions",
        ]
        for ob in result["obstructions"]:
            lines.extend([
                f"### {ob['obstruction_id']} — {ob['label']}",
                f"- category: {ob['category']}",
                f"- status: {ob['obstruction_status']}",
                f"- activation_score: {ob['activation_score']}",
                f"- defeats_absolute_proof: {ob['defeats_absolute_proof']}",
                f"- description: {ob['description']}",
                "",
            ])
        lines.extend([
            "## Forbidden claims",
            "- CONSCIOUSNESS_PROVEN",
            "- PHENOMENOLOGY_PROVEN",
            "- SUBJECTIVITY_PROVEN",
            "- SENTIENCE_PROVEN",
            "- QUALIA_PROVEN",
            "",
            "Maximum authorized conclusion: absolute proof is blocked, unsupported, or unresolved under explicit constraints; Open Cognitive Ecology is not certified as a conscious subject of experience.",
        ])
        return "\n".join(lines) + "\n"

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = inputs or {}
        evidence = inputs.get("evidence") if isinstance(inputs.get("evidence"), dict) else self._default_evidence()
        catalog = inputs.get("obstruction_catalog") if isinstance(inputs.get("obstruction_catalog"), list) else self._obstruction_catalog()
        obstructions = self._score_catalog(catalog, evidence)
        aggregate = self._aggregate(obstructions)

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "program_step": "ZPP8",
            "formal_target": "detect proof obstructions to absolute consciousness proof under constraints",
            "obstruction_types_required": [
                "irreducible_private_access",
                "functional_indiscernibility",
                "circularity",
                "theory_underdetermination",
                "anthropomorphic_projection",
                "closure_pressure",
            ],
            "obstructions": obstructions,
            "aggregate": aggregate,
            "proof_obstruction_detected": aggregate["active_blocker_count"] > 0,
            "absolute_proof_blocked": aggregate["absolute_proof_blocked"],
            "absolute_proof_achieved": False,
            "consciousness_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "forbidden_claims": list(FORBIDDEN_CLAIMS),
            "maximum_authorized_conclusion": "Absolute proof is blocked, unsupported, or unresolved under current epistemic constraints.",
            "evidence_keys": sorted(evidence.keys()),
        }

        if persist:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            json_path = OUTPUT_DIR / "proof_obstruction_detector.json"
            md_path = OUTPUT_DIR / "proof_obstruction_detector.md"
            json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            md_path.write_text(self._markdown(result), encoding="utf-8")
            result["paths"] = {"json": str(json_path), "markdown": str(md_path)}
        return result
