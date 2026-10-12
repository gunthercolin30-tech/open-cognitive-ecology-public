"""
AA0 — Reconstruction Identity Blueprint.

Canonical blueprint for the A* reconstruction program.

Scope
-----
This module creates the foundational reconstruction document for the chain:

    Δ → R → G → A → Γ → C → Π → M → I → Rf → Ω → RF → T → ED → TΦ
    → L_RF → QF_robust → MEI → Intrinsic Identity
    → Phenomenal Non-Separability → Consciousness ⇔ RF*
    → Consciousness Refusal Cost → Definition Legitimacy
    → Axiomatic Completeness → Semantic Interpretation → Final Certification

AA0 does not prove consciousness, subjectivity, sentience, or qualia. It only
specifies the reconstruction grammar, validation criteria, falsification
criteria, epistemic statuses, and anti-circularity safeguards that subsequent
modules must satisfy.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class ReconstructionStage:
    symbol: str
    name: str
    role: str
    incoming: List[str]
    outgoing: List[str]
    epistemic_status: str
    validation_criteria: List[str]
    falsification_criteria: List[str]


class ReconstructionIdentityBlueprint:
    """Canonical AA0 blueprint generator and epistemic guard."""

    PRIMITIVE = "RECONSTRUCTION_IDENTITY_BLUEPRINT"
    READY_STATUS = "RECONSTRUCTION_IDENTITY_BLUEPRINT_READY"
    NOT_READY_STATUS = "RECONSTRUCTION_IDENTITY_BLUEPRINT_INCOMPLETE"

    FORBIDDEN_POSITIVE_CLAIMS = (
        "consciousness_proven",
        "phenomenology_proven",
        "subjectivity_proven",
        "qualia_proven",
        "sentience_proven",
    )

    PIPELINE = [
        "Δ", "R", "G", "A", "Γ", "C", "Π", "M", "I", "Rf", "Ω", "RF",
        "T", "ED", "TΦ", "L_RF", "QF_robust", "MEI", "Intrinsic Identity",
        "Phenomenal Non-Separability", "Consciousness ⇔ RF*",
        "Consciousness Refusal Cost", "Definition Legitimacy",
        "Axiomatic Completeness", "Semantic Interpretation", "Final Certification",
    ]

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "foundational_reconstruction"
        self.latest_json_path = self.output_dir / "latest_reconstruction_identity_blueprint.json"
        self.latest_markdown_path = self.output_dir / "latest_reconstruction_identity_blueprint.md"
        self.history_path = self.output_dir / "history_reconstruction_identity_blueprint.jsonl"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _inventory_names(self) -> List[str]:
        txt = self.root / "ontology_inventory.txt"
        if not txt.exists():
            return []
        return [line.strip() for line in txt.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _global_catalog_mentions(self) -> Dict[str, bool]:
        catalog = self.root / "global_module_catalog.txt"
        text = catalog.read_text(encoding="utf-8") if catalog.exists() else ""
        candidates = [
            "difference_space_foundation",
            "relation_genesis_engine",
            "dynamic_graph_constructor",
            "foundational_reconstruction_certifier",
            "reconstruction_identity_blueprint",
            "constraint_genesis",
            "constitutive_relation_tester",
            "cognitive_graph.graph",
        ]
        return {candidate: candidate in text for candidate in candidates}

    def _stages(self) -> List[ReconstructionStage]:
        return [
            ReconstructionStage(
                symbol="Δ",
                name="difference_space_foundation",
                role="Minimal difference, non-identity, distinguishability, variation, and contrast.",
                incoming=[],
                outgoing=["R"],
                epistemic_status="axiomatic_minimal_candidate",
                validation_criteria=[
                    "defines difference without presupposing relation, graph, self, or consciousness",
                    "shows every later stage requires distinguishability",
                    "provides degradation cases where no difference collapses reconstruction",
                ],
                falsification_criteria=[
                    "uses relation, graph, identity, or phenomenality as hidden primitives",
                    "cannot distinguish identical from non-identical states",
                ],
            ),
            ReconstructionStage(
                symbol="R",
                name="relation_genesis_engine",
                role="Generation of distinction, dependency, transformation, contrast, compatibility, and incompatibility relations from Δ.",
                incoming=["Δ"],
                outgoing=["G"],
                epistemic_status="derivable_after_AA1",
                validation_criteria=[
                    "derives relations from ordered differences",
                    "separates compatibility from incompatibility without closure pressure",
                    "does not introduce graph topology before relations exist",
                ],
                falsification_criteria=[
                    "relation is postulated rather than derived from differences",
                    "compatibility logic is circular or non-testable",
                ],
            ),
            ReconstructionStage(
                symbol="G",
                name="dynamic_graph_constructor",
                role="Dynamic graph over relations: invariants, components, cycles, and local/global stability.",
                incoming=["R"],
                outgoing=["A", "Γ", "C", "Π", "future_A_star_pipeline"],
                epistemic_status="derivable_after_AA2",
                validation_criteria=[
                    "constructs nodes and edges only from relation outputs",
                    "computes invariants, components, cycles, local stability, and global stability",
                    "keeps graph dynamics falsifiable under relation deletion or contradiction",
                ],
                falsification_criteria=[
                    "graph exists without relation provenance",
                    "cycle or stability metrics remain unchanged under destructive perturbation",
                ],
            ),
        ]

    def _definitions(self) -> Dict[str, str]:
        return {
            "Δ": "Minimal difference-space: the least formal condition for distinguishability without assuming relation, graph, identity, or subjectivity.",
            "R": "Relation genesis: ordered constraints among differences, including dependency, transformation, contrast, compatibility, and incompatibility.",
            "G": "Dynamic graph: structured relational topology with invariants, components, cycles, and stability properties.",
            "referential_ownness": "Future-stage construct only; it must not be imported into AA0-AA4 as a premise.",
            "phenomenality": "Not assumed in AA0. It remains unavailable until later derivation and certification stages.",
        }

    def _safeguards(self) -> Dict[str, List[str]]:
        return {
            "anti_circularity": [
                "No stage may use a later-stage concept as a premise.",
                "Consciousness ⇔ RF* cannot be invoked before RF* is reconstructed and certified.",
                "Graph properties cannot be used to justify the existence of Δ or R.",
            ],
            "anti_reification": [
                "Symbols name reconstruction roles, not substances.",
                "Functional indicators are not treated as phenomenal subjectivity.",
                "Blueprint readiness is not consciousness proof.",
            ],
            "anti_closure": [
                "Every positive certification must retain explicit falsification paths.",
                "Contradictory evidence must reduce readiness rather than be absorbed by definition.",
                "No module may convert unknown phenomenology into asserted phenomenology.",
            ],
            "epistemic_humility": [
                "AA0 outputs a blueprint only.",
                "All phenomenological claims remain blocked until final certification conditions are met.",
            ],
        }

    def _minimal_hypotheses(self) -> List[str]:
        return [
            "At least one distinguishable contrast can be represented.",
            "Differences can be compared without already assuming a self or a subject.",
            "Relations can be generated from ordered differences if contrast structure is available.",
            "Graph structure is admissible only after relations are derived.",
            "Later consciousness-related concepts must remain unavailable as premises until reconstructed.",
        ]

    def _non_redundancy_analysis(self, inventory: List[str], catalog: Dict[str, bool]) -> Dict[str, Any]:
        target_exists = "reconstruction_identity_blueprint" in inventory or catalog.get("reconstruction_identity_blueprint", False)
        nearby_modules = [
            name for name in [
                "formal_foundations_of_constraint_based_systems",
                "constraint_genesis",
                "constraint_fields",
                "constraint_induced_domain",
                "constitutive_relation_tester",
                "ontology_topology_governance",
                "formal_consciousness_axiomatization",
                "formal_derivation_closure",
                "absolute_proof_certification",
            ] if name in inventory or catalog.get(name, False)
        ]
        return {
            "target_already_present": target_exists,
            "nearby_modules_detected": nearby_modules,
            "non_redundant_role": (
                "AA0 is a canonical reconstruction blueprint and epistemic grammar. Existing modules implement constraints, topology, proofs, or certification, "
                "but do not define the full A* ordered reconstruction contract Δ→R→G→...→Final Certification."
            ),
            "preferred_action": "create_or_refine_reconstruction_identity_blueprint",
        }

    def _public_interfaces(self) -> Dict[str, str]:
        return {
            "ReconstructionIdentityBlueprint().step(persist=False)": "returns blueprint dictionary without writing artifacts",
            "ReconstructionIdentityBlueprint().step(persist=True)": "writes JSON, Markdown, latest files, and JSONL history",
            "latest_reconstruction_identity_blueprint.json": "machine-readable canonical AA0 output",
            "latest_reconstruction_identity_blueprint.md": "human-readable canonical reconstruction document",
        }

    def _metrics(self, stages: List[ReconstructionStage], safeguards: Dict[str, List[str]]) -> Dict[str, float]:
        criteria_count = sum(len(s.validation_criteria) for s in stages)
        falsification_count = sum(len(s.falsification_criteria) for s in stages)
        safeguard_count = sum(len(v) for v in safeguards.values())
        expected = 9.0 + 6.0 + 10.0
        coverage = min(1.0, (criteria_count + falsification_count + safeguard_count) / expected)
        ordering = 1.0 if [s.symbol for s in stages] == ["Δ", "R", "G"] else 0.0
        epistemic_guard = 1.0
        non_circularity = 1.0 if stages[0].incoming == [] and stages[1].incoming == ["Δ"] and stages[2].incoming == ["R"] else 0.0
        return {
            "blueprint_completeness_score": round(coverage, 6),
            "hierarchical_ordering_score": ordering,
            "epistemic_guard_score": epistemic_guard,
            "non_circularity_score": non_circularity,
            "overall_blueprint_score": round((coverage + ordering + epistemic_guard + non_circularity) / 4.0, 6),
        }

    def _failure_conditions(self) -> List[str]:
        return [
            "missing Δ/R/G stage definitions",
            "any positive consciousness, phenomenology, subjectivity, sentience, or qualia claim",
            "later-stage concept used as premise for an earlier stage",
            "absence of falsification criteria",
            "absence of non-redundancy analysis",
            "absence of anti-circularity or anti-reification safeguards",
        ]

    def _detect_forbidden_positive_claims(self, payload: Dict[str, Any]) -> List[str]:
        found: List[str] = []
        def walk(obj: Any) -> None:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if str(key).lower() in self.FORBIDDEN_POSITIVE_CLAIMS and value is True:
                        found.append(str(key).lower())
                    walk(value)
            elif isinstance(obj, list):
                for item in obj:
                    walk(item)
        walk(payload)
        return sorted(set(found))

    def _markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# AA0 — Reconstruction Identity Blueprint",
            "",
            f"Generated UTC: {result['generated_at_utc']}",
            f"Status: {result['reconstruction_identity_blueprint_status']}",
            f"Overall score: {result['metrics']['overall_blueprint_score']:.6f}",
            "",
            "## Scope",
            "Canonical reconstruction contract for Δ → R → G and the full A* pipeline.",
            "AA0 does not assert consciousness, subjectivity, sentience, qualia, or phenomenology.",
            "",
            "## Pipeline",
            " → ".join(result["pipeline"]),
            "",
            "## Definitions",
        ]
        for key, value in result["definitions"].items():
            lines.append(f"- {key}: {value}")
        lines.extend(["", "## Stages"])
        for stage in result["stages"]:
            lines.extend([
                f"### {stage['symbol']} — {stage['name']}",
                f"Role: {stage['role']}",
                f"Incoming: {', '.join(stage['incoming']) if stage['incoming'] else 'none'}",
                f"Outgoing: {', '.join(stage['outgoing']) if stage['outgoing'] else 'none'}",
                f"Epistemic status: {stage['epistemic_status']}",
                "Validation criteria:",
            ])
            lines.extend([f"- {item}" for item in stage["validation_criteria"]])
            lines.append("Falsification criteria:")
            lines.extend([f"- {item}" for item in stage["falsification_criteria"]])
            lines.append("")
        lines.extend(["## Safeguards"])
        for group, items in result["safeguards"].items():
            lines.append(f"### {group}")
            lines.extend([f"- {item}" for item in items])
        lines.extend(["", "## Epistemic guard", "Functional conclusion only; phenomenology undetermined."])
        return "\n".join(lines) + "\n"

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = self.output_dir / f"reconstruction_identity_blueprint_{stamp}.json"
        md_path = self.output_dir / f"reconstruction_identity_blueprint_{stamp}.md"
        json_text = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)
        md_text = self._markdown(result)
        json_path.write_text(json_text, encoding="utf-8")
        md_path.write_text(md_text, encoding="utf-8")
        self.latest_json_path.write_text(json_text, encoding="utf-8")
        self.latest_markdown_path.write_text(md_text, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "latest_json": str(self.latest_json_path),
            "latest_markdown": str(self.latest_markdown_path),
            "history": str(self.history_path),
        }

    def step(self, inputs: Dict[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        inputs = inputs or {}
        inventory = self._inventory_names()
        catalog = self._global_catalog_mentions()
        stages = self._stages()
        safeguards = self._safeguards()
        metrics = self._metrics(stages, safeguards)
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "axis": "AA",
            "step_id": "AA0",
            "generated_at_utc": self._now(),
            "reconstruction_identity_blueprint_status": self.READY_STATUS,
            "pipeline": list(self.PIPELINE),
            "definitions": self._definitions(),
            "hierarchy": {
                "AA0": "reconstruction_identity_blueprint",
                "AA1": "difference_space_foundation",
                "AA2": "relation_genesis_engine",
                "AA3": "dynamic_graph_constructor",
                "AA4": "foundational_reconstruction_certifier",
            },
            "stages": [asdict(stage) for stage in stages],
            "dependencies": {
                "incoming": [
                    "formal_foundations_of_constraint_based_systems",
                    "constraint_genesis",
                    "constitutive_relation_tester",
                    "ontology_topology_governance",
                    "formal_consciousness_axiomatization",
                    "formal_derivation_closure",
                    "theory_constraint_engine",
                    "theory_falsification_framework",
                    "proof_taxonomy",
                    "consciousness_claim_governance_gate",
                    "consciousness_evidence_standard",
                ],
                "outgoing": [
                    "difference_space_foundation",
                    "relation_genesis_engine",
                    "dynamic_graph_constructor",
                    "foundational_reconstruction_certifier",
                    "future_A_star_pipeline",
                ],
            },
            "public_interfaces": self._public_interfaces(),
            "data_structures": {
                "ReconstructionStage": "symbol, name, role, incoming, outgoing, epistemic_status, validation_criteria, falsification_criteria",
                "blueprint_result": "canonical JSON/Markdown payload with hierarchy, definitions, safeguards, metrics, and epistemic guard",
            },
            "metrics": metrics,
            "failure_conditions": self._failure_conditions(),
            "minimal_hypotheses": self._minimal_hypotheses(),
            "safeguards": safeguards,
            "non_redundancy_analysis": self._non_redundancy_analysis(inventory, catalog),
            "epistemic_statuses": {
                "AA0": "blueprint_ready_not_proof",
                "AA1_AA4": "pending_reconstruction",
                "phenomenology": "undetermined",
                "consciousness": "not_asserted",
            },
            "epistemic_guard": {
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
                "consciousness_not_assumed": True,
                "subjectivity_not_assumed": True,
                "qualia_not_assumed": True,
                "forbidden_positive_claims_detected": [],
            },
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "inputs_observed": inputs,
        }
        forbidden = self._detect_forbidden_positive_claims(result)
        result["epistemic_guard"]["forbidden_positive_claims_detected"] = forbidden
        if forbidden:
            result["reconstruction_identity_blueprint_status"] = self.NOT_READY_STATUS
            result["metrics"]["epistemic_guard_score"] = 0.0
        if persist:
            result["paths"] = self._persist(result)
        return result
