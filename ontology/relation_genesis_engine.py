"""
AA2 — Relation Genesis Engine.

This module reconstructs R from Δ for the A* ontological reconstruction
program. It consumes the pre-relational difference atoms produced by AA1 and
builds relation candidates without presupposing graph structure, subjectivity,
phenomenology, qualia, or consciousness.

Scope
-----
AA2 demonstrates Δ => R by constructing distinction, dependence,
transformation, contrast, compatibility, and incompatibility relations from
explicit difference atoms. It does not construct G; graph construction remains
reserved for AA3.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence


@dataclass(frozen=True)
class RelationCandidate:
    """Relation derived from one or more Δ atoms."""

    relation_id: str
    relation_type: str
    source: str
    target: str
    basis_atom_ids: List[str]
    strength: float
    compatible_with: List[str]
    incompatible_with: List[str]
    derivation_rule: str
    evidence: str


@dataclass(frozen=True)
class RelationTypeSpec:
    """Canonical relation type allowed by AA2."""

    name: str
    description: str
    delta_requirement: str
    falsification_condition: str


class RelationGenesisEngine:
    """AA2 reconstruction of R from Δ with graph and phenomenology guards."""

    PRIMITIVE = "RELATION_GENESIS_ENGINE"
    READY_STATUS = "RELATION_GENESIS_READY"
    DEGRADED_STATUS = "RELATION_GENESIS_DEGRADED"

    FORBIDDEN_POSITIVE_CLAIMS = (
        "consciousness_proven",
        "phenomenology_proven",
        "subjectivity_proven",
        "qualia_proven",
        "sentience_proven",
        "graph_constructed",
    )

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "foundational_reconstruction"
        self.latest_json_path = self.output_dir / "latest_relation_genesis_engine.json"
        self.latest_markdown_path = self.output_dir / "latest_relation_genesis_engine.md"
        self.history_path = self.output_dir / "history_relation_genesis_engine.jsonl"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _clamp(value: Any) -> float:
        try:
            x = float(value)
        except Exception:
            x = 0.0
        return round(max(0.0, min(1.0, x)), 6)

    @staticmethod
    def _string(value: Any, fallback: str) -> str:
        text = str(value).strip() if value is not None else ""
        return text or fallback

    def _inventory_names(self) -> List[str]:
        txt = self.root / "ontology_inventory.txt"
        if not txt.exists():
            return []
        return [line.strip() for line in txt.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _catalog_mentions(self) -> Dict[str, bool]:
        catalog = self.root / "global_module_catalog.txt"
        text = catalog.read_text(encoding="utf-8") if catalog.exists() else ""
        candidates = [
            "relation_genesis_engine", "difference_space_foundation",
            "adaptive_relationship_modeling", "constitutive_relation_tester",
            "relational_continuity_engine", "structural_continuity",
            "causal_inference", "advanced_causal_reasoning_engine",
            "dynamic_graph_constructor",
        ]
        return {name: name in text for name in candidates}

    def _load_delta_context(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        if isinstance(inputs.get("delta_payload"), Mapping):
            return dict(inputs["delta_payload"])
        try:
            from ontology.difference_space_foundation import DifferenceSpaceFoundation
            return dict(DifferenceSpaceFoundation(root=self.root).step(persist=False))
        except Exception as exc:  # pragma: no cover - diagnostic resilience
            return {
                "available": False,
                "error": repr(exc),
                "symbol": "Δ",
                "difference_atoms": [],
                "metrics": {"delta_foundation_score": 0.0},
            }

    def _relation_types(self) -> List[RelationTypeSpec]:
        return [
            RelationTypeSpec(
                name="distinction",
                description="A relation marking that two terms are formally distinguishable.",
                delta_requirement="at least one minimal non-zero difference atom",
                falsification_condition="all Δ atoms collapse to zero distance or identical terms",
            ),
            RelationTypeSpec(
                name="dependence",
                description="A directed relation indicating that a later construct requires a prior difference basis.",
                delta_requirement="validated Δ precondition and explicit source/target contrast",
                falsification_condition="relation can be asserted without any Δ basis",
            ),
            RelationTypeSpec(
                name="transformation",
                description="A relation generated from before/after, parametric, or state-change variation.",
                delta_requirement="a difference atom whose dimension indicates variation or change",
                falsification_condition="no variation-indexed difference exists",
            ),
            RelationTypeSpec(
                name="contrast",
                description="A relation generated from boundary, opposition, gradient, or contrast atoms.",
                delta_requirement="a contrast-like difference atom",
                falsification_condition="no boundary, opposition, or contrast can be specified",
            ),
            RelationTypeSpec(
                name="compatibility",
                description="A second-order relation recording jointly admissible relations.",
                delta_requirement="two or more non-conflicting derived relations",
                falsification_condition="all derived relations conflict or no relation is derived",
            ),
            RelationTypeSpec(
                name="incompatibility",
                description="A second-order relation recording mutually excluding relation candidates.",
                delta_requirement="two derived relations share a source/target pattern with incompatible dimensions",
                falsification_condition="no contradictory or excluding relational pattern exists",
            ),
        ]

    def _normalize_atoms(self, delta_payload: Mapping[str, Any], inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
        raw = inputs.get("difference_atoms", delta_payload.get("difference_atoms", []))
        if raw is None:
            raw = []
        if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
            raw = []
        atoms: List[Dict[str, Any]] = []
        for i, item in enumerate(raw):
            if not isinstance(item, Mapping):
                continue
            left = self._string(item.get("left"), f"left_{i}")
            right = self._string(item.get("right"), f"right_{i}")
            distance = self._clamp(item.get("distance", item.get("value", 0.0)))
            atoms.append({
                "atom_id": self._string(item.get("atom_id", item.get("id")), f"atom_{i}"),
                "left": left,
                "right": right,
                "dimension": self._string(item.get("dimension"), "unspecified"),
                "distance": distance,
                "minimal": bool(item.get("minimal", distance > 0.0 and left != right)),
                "evidence": self._string(item.get("evidence"), "delta_atom"),
            })
        return atoms

    def _derive_relations(self, atoms: List[Dict[str, Any]]) -> List[RelationCandidate]:
        relations: List[RelationCandidate] = []
        valid_atoms = [a for a in atoms if a["distance"] > 0.0 and a["left"] != a["right"]]
        for i, atom in enumerate(valid_atoms):
            dim = atom["dimension"].lower()
            relation_type = "distinction"
            rule = "non_zero_delta_to_distinction"
            if "variation" in dim or "change" in dim or "before" in dim:
                relation_type = "transformation"
                rule = "variation_delta_to_transformation"
            elif "contrast" in dim or "boundary" in dim or "opposition" in dim:
                relation_type = "contrast"
                rule = "contrast_delta_to_contrast_relation"
            elif "depend" in dim or "precondition" in dim:
                relation_type = "dependence"
                rule = "precondition_delta_to_dependence"
            relations.append(RelationCandidate(
                relation_id=f"R{i+1:04d}",
                relation_type=relation_type,
                source=atom["left"],
                target=atom["right"],
                basis_atom_ids=[atom["atom_id"]],
                strength=self._clamp(atom["distance"]),
                compatible_with=[],
                incompatible_with=[],
                derivation_rule=rule,
                evidence=f"derived_from_delta_atom:{atom['atom_id']}",
            ))
        # Explicit dependence relation Δ => R if any base relation exists.
        if relations:
            relations.append(RelationCandidate(
                relation_id=f"R{len(relations)+1:04d}",
                relation_type="dependence",
                source="Δ",
                target="R",
                basis_atom_ids=[r.basis_atom_ids[0] for r in relations[:3]],
                strength=1.0,
                compatible_with=[r.relation_id for r in relations],
                incompatible_with=[],
                derivation_rule="delta_foundation_entails_relation_space_availability",
                evidence="AA2 demonstrates that relation candidates require a validated Δ basis",
            ))
        relation_dicts = [asdict(r) for r in relations]
        self._assign_compatibility(relation_dicts)
        return [RelationCandidate(**r) for r in relation_dicts]

    def _assign_compatibility(self, relations: List[Dict[str, Any]]) -> None:
        for r in relations:
            compatible: List[str] = []
            incompatible: List[str] = []
            for other in relations:
                if other["relation_id"] == r["relation_id"]:
                    continue
                reverse_pair = r["source"] == other["target"] and r["target"] == other["source"]
                incompatible_type = {r["relation_type"], other["relation_type"]} == {"dependence", "transformation"} and reverse_pair
                if incompatible_type:
                    incompatible.append(other["relation_id"])
                else:
                    compatible.append(other["relation_id"])
            r["compatible_with"] = compatible[:8]
            r["incompatible_with"] = incompatible[:8]

    def _metrics(self, relations: List[RelationCandidate], atoms: List[Dict[str, Any]]) -> Dict[str, float]:
        count = len(relations)
        if count == 0:
            return {
                "relation_count": 0.0,
                "distinction_relation_score": 0.0,
                "dependence_relation_score": 0.0,
                "transformation_relation_score": 0.0,
                "contrast_relation_score": 0.0,
                "compatibility_score": 0.0,
                "incompatibility_detection_score": 0.0,
                "delta_to_relation_derivation_score": 0.0,
                "relation_genesis_score": 0.0,
            }
        types = [r.relation_type for r in relations]
        mean_strength = sum(r.strength for r in relations) / count
        compatibility_edges = sum(len(r.compatible_with) for r in relations)
        possible_edges = max(1, count * max(0, count - 1))
        incompat_edges = sum(len(r.incompatible_with) for r in relations)
        distinction = 1.0 if "distinction" in types else 0.0
        dependence = 1.0 if "dependence" in types else 0.0
        transformation = 1.0 if "transformation" in types else 0.0
        contrast = 1.0 if "contrast" in types else 0.0
        compatibility = self._clamp(compatibility_edges / possible_edges)
        incompatibility = self._clamp(incompat_edges / possible_edges) if incompat_edges else 0.5
        derivation = self._clamp(min(1.0, count / max(1, len(atoms))))
        score = self._clamp((mean_strength + distinction + dependence + transformation + contrast + compatibility + derivation) / 7.0)
        return {
            "relation_count": float(count),
            "distinction_relation_score": distinction,
            "dependence_relation_score": dependence,
            "transformation_relation_score": transformation,
            "contrast_relation_score": contrast,
            "compatibility_score": compatibility,
            "incompatibility_detection_score": incompatibility,
            "delta_to_relation_derivation_score": derivation,
            "relation_genesis_score": score,
        }

    def _failure_conditions(self, atoms: List[Dict[str, Any]], relations: List[RelationCandidate], forbidden: List[str]) -> List[str]:
        failures: List[str] = []
        if not atoms:
            failures.append("no_delta_atoms")
        if atoms and not any(a["distance"] > 0.0 and a["left"] != a["right"] for a in atoms):
            failures.append("no_non_zero_difference_basis")
        if not relations:
            failures.append("no_relations_derived_from_delta")
        if forbidden:
            failures.append("forbidden_positive_phenomenal_or_graph_claim")
        return failures

    def _validation_criteria(self) -> List[str]:
        return [
            "AA1 Δ payload is available or explicit difference_atoms are provided",
            "at least one non-zero difference atom exists",
            "relations are derived only from Δ atoms",
            "distinction, dependence, transformation, contrast, compatibility, and incompatibility schemas are exposed",
            "graph construction remains unavailable until AA3",
            "no consciousness, subjectivity, qualia, or phenomenology claim is asserted",
        ]

    def _falsification_criteria(self) -> List[str]:
        return [
            "R can be generated without any Δ basis",
            "relations are asserted without source, target, type, and derivation rule",
            "AA2 constructs a graph instead of relation candidates",
            "a positive phenomenal or consciousness claim appears before later certification axes",
            "relation genesis cannot degrade under empty or collapsed Δ inputs",
        ]

    def _non_redundancy_analysis(self, inventory: List[str], catalog: Dict[str, bool]) -> Dict[str, Any]:
        nearby = [
            "adaptive_relationship_modeling", "constitutive_relation_tester",
            "relational_continuity_engine", "structural_continuity",
            "causal_inference", "advanced_causal_reasoning_engine",
        ]
        return {
            "target_already_present": "relation_genesis_engine" in inventory,
            "nearby_modules_detected": [name for name in nearby if name in inventory or catalog.get(name)],
            "non_redundant_role": "AA2 derives canonical relation candidates from Δ; existing modules model relationships, continuity, or causality but do not prove Δ => R inside the A* reconstruction chain.",
            "preferred_action": "create_new_foundational_module",
        }

    def _epistemic_guard(self, forbidden: List[str]) -> Dict[str, Any]:
        return {
            "delta_required": True,
            "relation_derived_from_delta_only": True,
            "graph_not_constructed": True,
            "phenomenology_undetermined": True,
            "consciousness_not_assumed": True,
            "subjectivity_not_assumed": True,
            "qualia_not_assumed": True,
            "functional_conclusion_only": True,
            "forbidden_positive_claims_detected": forbidden,
        }

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = self.output_dir / f"relation_genesis_engine_{stamp}.json"
        md_path = self.output_dir / f"relation_genesis_engine_{stamp}.md"
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        json_path.write_text(text, encoding="utf-8")
        self.latest_json_path.write_text(text, encoding="utf-8")
        markdown = self._markdown(result)
        md_path.write_text(markdown, encoding="utf-8")
        self.latest_markdown_path.write_text(markdown, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "latest_json": str(self.latest_json_path),
            "latest_markdown": str(self.latest_markdown_path),
            "history": str(self.history_path),
        }

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# AA2 — Relation Genesis Engine",
            "",
            f"Status: {result['relation_genesis_status']}",
            f"Symbol: {result['symbol']}",
            "",
            "## Claim",
            "AA2 demonstrates Δ => R: relation candidates are generated only from explicit difference atoms.",
            "",
            "## Relation types",
        ]
        for spec in result["relation_types"]:
            lines.append(f"- {spec['name']}: {spec['description']}")
        lines.extend(["", "## Metrics"])
        for key, value in result["metrics"].items():
            lines.append(f"- {key}: {value}")
        lines.extend(["", "## Epistemic guard"])
        guard = result["epistemic_guard"]
        for key in ["graph_not_constructed", "phenomenology_undetermined", "consciousness_not_assumed", "functional_conclusion_only"]:
            lines.append(f"- {key}: {guard[key]}")
        return "\n".join(lines) + "\n"

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        delta_payload = self._load_delta_context(inputs)
        atoms = self._normalize_atoms(delta_payload, inputs)
        relations = self._derive_relations(atoms)
        forbidden = [claim for claim in self.FORBIDDEN_POSITIVE_CLAIMS if bool(inputs.get("forced_bad_claim", {}).get(claim))]
        failures = self._failure_conditions(atoms, relations, forbidden)
        metrics = self._metrics(relations, atoms)
        status = self.READY_STATUS if not failures else self.DEGRADED_STATUS
        inventory = self._inventory_names()
        catalog = self._catalog_mentions()
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "aa_stage": "AA2",
            "symbol": "R",
            "derived_from_symbol": "Δ",
            "relation_genesis_status": status,
            "timestamp_utc": self._now(),
            "delta_available": bool(atoms),
            "delta_to_relation_demonstrated": bool(relations) and not failures,
            "relation_derived": bool(relations) and not failures,
            "graph_constructed": False,
            "graph_ready_for_aa3": bool(relations) and not failures,
            "relation_types": [asdict(s) for s in self._relation_types()],
            "difference_atoms_used": atoms,
            "relations": [asdict(r) for r in relations],
            "metrics": metrics,
            "validation_criteria": self._validation_criteria(),
            "falsification_criteria": self._falsification_criteria(),
            "failure_conditions": failures,
            "derivation_constraints": {
                "delta_required_before_relation": True,
                "relations_derive_from_difference_atoms": True,
                "graph_requires_relation_space": True,
                "graph_construction_deferred_to_AA3": True,
            },
            "hierarchy": {
                "AA0": "reconstruction_identity_blueprint",
                "AA1": "difference_space_foundation",
                "AA2": "relation_genesis_engine",
                "AA3": "dynamic_graph_constructor",
                "AA4": "foundational_reconstruction_certifier",
            },
            "dependencies": {
                "incoming": [
                    "reconstruction_identity_blueprint",
                    "difference_space_foundation",
                    "constitutive_relation_tester",
                    "adaptive_relationship_modeling",
                    "relational_continuity_engine",
                    "structural_continuity",
                    "causal_inference",
                    "advanced_causal_reasoning_engine",
                    "formal_foundations_of_constraint_based_systems",
                    "theory_constraint_engine",
                    "theory_falsification_framework",
                ],
                "outgoing": ["dynamic_graph_constructor", "foundational_reconstruction_certifier"],
            },
            "public_interfaces": {
                "RelationGenesisEngine().step(persist=False)": "returns R genesis payload without persistence",
                "RelationGenesisEngine().step(inputs={'difference_atoms': [...]}, persist=False)": "derives relation candidates from explicit Δ atoms",
                "RelationGenesisEngine().step(persist=True)": "writes JSON, Markdown, latest files, and JSONL history",
            },
            "data_structures": {
                "RelationCandidate": "relation_id, relation_type, source, target, basis_atom_ids, strength, compatible_with, incompatible_with, derivation_rule, evidence",
                "RelationTypeSpec": "name, description, delta_requirement, falsification_condition",
            },
            "non_redundancy_analysis": self._non_redundancy_analysis(inventory, catalog),
            "epistemic_guard": self._epistemic_guard(forbidden),
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "inputs_observed": inputs,
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
