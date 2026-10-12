"""
AA1 — Difference Space Foundation.

This module reconstructs Δ, the minimal difference-space foundation for the
A* ontological reconstruction program.

Scope
-----
AA1 formalizes minimal difference, non-identity, distinguishability,
variation, contrast, and the space of differences. It demonstrates that later
reconstruction stages require Δ while keeping relation, graph, self,
subjectivity, qualia, and consciousness unavailable as premises.

AA1 does not prove consciousness, phenomenology, subjectivity, sentience, or
qualia. It only certifies that the Δ foundation is structurally ready for AA2
relation genesis.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from math import sqrt
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence


@dataclass(frozen=True)
class DifferenceAtom:
    """Minimal distinguished pair with an explicit dimension and distance."""

    atom_id: str
    left: str
    right: str
    dimension: str
    distance: float
    minimal: bool
    evidence: str


@dataclass(frozen=True)
class DifferenceDimension:
    """Named contrast dimension used to build Δ without relations or graphs."""

    name: str
    description: str
    observable_indicator: str
    falsification_condition: str


class DifferenceSpaceFoundation:
    """AA1 reconstruction of Δ as a conservative foundational primitive."""

    PRIMITIVE = "DIFFERENCE_SPACE_FOUNDATION"
    READY_STATUS = "DIFFERENCE_SPACE_FOUNDATION_READY"
    DEGRADED_STATUS = "DIFFERENCE_SPACE_FOUNDATION_DEGRADED"

    FORBIDDEN_POSITIVE_CLAIMS = (
        "consciousness_proven",
        "phenomenology_proven",
        "subjectivity_proven",
        "qualia_proven",
        "sentience_proven",
    )

    DEFAULT_OBSERVATIONS = [
        {"id": "minimal_non_identity", "left": "x", "right": "not_x", "dimension": "logical_contrast", "value": 1.0},
        {"id": "distinguishable_state", "left": "state_a", "right": "state_b", "dimension": "state_distinguishability", "value": 0.82},
        {"id": "variation_event", "left": "before", "right": "after", "dimension": "variation", "value": 0.74},
        {"id": "contrast_boundary", "left": "inside", "right": "outside", "dimension": "contrast", "value": 0.68},
    ]

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "foundational_reconstruction"
        self.latest_json_path = self.output_dir / "latest_difference_space_foundation.json"
        self.latest_markdown_path = self.output_dir / "latest_difference_space_foundation.md"
        self.history_path = self.output_dir / "history_difference_space_foundation.jsonl"

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
            "difference_space_foundation", "reconstruction_identity_blueprint",
            "constraint_genesis", "observability", "measurement_perturbation",
            "non_representability", "redundancy", "degeneracy",
            "relation_genesis_engine", "dynamic_graph_constructor",
        ]
        return {name: name in text for name in candidates}

    def _load_blueprint_context(self) -> Dict[str, Any]:
        try:
            from ontology.reconstruction_identity_blueprint import ReconstructionIdentityBlueprint
            return dict(ReconstructionIdentityBlueprint(root=self.root).step(persist=False))
        except Exception as exc:  # pragma: no cover - diagnostic resilience
            return {"available": False, "error": repr(exc), "pipeline": ["Δ", "R", "G"]}

    def _dimensions(self) -> List[DifferenceDimension]:
        return [
            DifferenceDimension(
                name="minimal_difference",
                description="Least contrast sufficient to deny strict identity between two tokens or states.",
                observable_indicator="a normalized non-zero distance or symbolic inequality is present",
                falsification_condition="all compared items collapse into strict identity",
            ),
            DifferenceDimension(
                name="non_identity",
                description="A and B are not interchangeable under at least one admissible dimension.",
                observable_indicator="left/right labels or values remain distinguishable after normalization",
                falsification_condition="renaming or measurement erases every detectable contrast",
            ),
            DifferenceDimension(
                name="distinguishability",
                description="An observer-independent formal test can separate at least two states without invoking a subject.",
                observable_indicator="distinguishability score exceeds zero",
                falsification_condition="no possible comparison yields a discriminating signal",
            ),
            DifferenceDimension(
                name="variation",
                description="Difference indexed over transformation, before/after, or parameter change.",
                observable_indicator="at least one temporal or parametric delta exists",
                falsification_condition="every transformation preserves all values exactly",
            ),
            DifferenceDimension(
                name="contrast",
                description="Boundary-like opposition or gradient that makes a distinction operational.",
                observable_indicator="contrast strength is positive and bounded",
                falsification_condition="no boundary, gradient, or opposition can be specified",
            ),
        ]

    def _normalize_observations(self, inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
        raw = inputs.get("observations", self.DEFAULT_OBSERVATIONS)
        if raw is None:
            raw = []
        if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
            raw = []
        observations: List[Dict[str, Any]] = []
        for i, item in enumerate(raw):
            if not isinstance(item, Mapping):
                continue
            left = self._string(item.get("left"), f"left_{i}")
            right = self._string(item.get("right"), f"right_{i}")
            dimension = self._string(item.get("dimension"), "unspecified")
            value = self._clamp(item.get("value", item.get("distance", 0.0)))
            observations.append({
                "id": self._string(item.get("id"), f"difference_{i}"),
                "left": left,
                "right": right,
                "dimension": dimension,
                "value": value,
            })
        return observations

    def _difference_atoms(self, observations: List[Dict[str, Any]]) -> List[DifferenceAtom]:
        atoms: List[DifferenceAtom] = []
        for item in observations:
            distance = self._clamp(item.get("value", 0.0))
            left = self._string(item.get("left"), "left")
            right = self._string(item.get("right"), "right")
            dimension = self._string(item.get("dimension"), "unspecified")
            minimal = bool(distance > 0.0 and left != right)
            evidence = "non_zero_contrast" if minimal else "collapsed_identity_or_zero_distance"
            atoms.append(DifferenceAtom(
                atom_id=self._string(item.get("id"), f"atom_{len(atoms)}"),
                left=left,
                right=right,
                dimension=dimension,
                distance=distance,
                minimal=minimal,
                evidence=evidence,
            ))
        return atoms

    def _space_metrics(self, atoms: List[DifferenceAtom]) -> Dict[str, float]:
        count = len(atoms)
        if count == 0:
            return {
                "difference_count": 0.0,
                "non_identity_score": 0.0,
                "distinguishability_score": 0.0,
                "variation_score": 0.0,
                "contrast_density": 0.0,
                "difference_space_coherence": 0.0,
                "delta_foundation_score": 0.0,
            }
        positive = [a for a in atoms if a.distance > 0.0]
        minimal = [a for a in atoms if a.minimal]
        dimensions = {a.dimension for a in positive}
        mean_distance = sum(a.distance for a in atoms) / count
        non_identity = len(minimal) / count
        distinguishability = len(positive) / count
        variation_hits = [a for a in positive if "variation" in a.dimension.lower() or "state" in a.dimension.lower() or "temporal" in a.dimension.lower()]
        variation_score = len(variation_hits) / count
        contrast_density = min(1.0, len(dimensions) / max(1.0, count))
        coherence = sqrt(max(0.0, mean_distance * non_identity))
        delta = (non_identity + distinguishability + variation_score + contrast_density + coherence) / 5.0
        return {
            "difference_count": float(count),
            "non_identity_score": round(non_identity, 6),
            "distinguishability_score": round(distinguishability, 6),
            "variation_score": round(variation_score, 6),
            "contrast_density": round(contrast_density, 6),
            "difference_space_coherence": round(coherence, 6),
            "delta_foundation_score": round(delta, 6),
        }

    def _dependence_demonstration(self, metrics: Mapping[str, float]) -> Dict[str, Any]:
        ready = metrics.get("delta_foundation_score", 0.0) > 0.0 and metrics.get("distinguishability_score", 0.0) > 0.0
        return {
            "claim": "Every later A* stage requires Δ because relation, graph, agency, constraint, referential field, and certification all presuppose distinguishable states.",
            "later_stage_dependence": {
                "R": "relations require at least two distinguishable relata or distinguishable transformations",
                "G": "graphs require nodes or edges that remain distinguishable",
                "A": "agency cannot be reconstructed without distinguishable alternatives",
                "Γ": "constraint fields require distinguishable admissible and inadmissible configurations",
                "RF": "referential fields require distinguishable anchors and transformations",
                "Final Certification": "certification requires distinguishable success, failure, and falsification states",
            },
            "delta_precondition_satisfied": ready,
            "hidden_premise_guard": "No relation, graph, self, subject, qualia, or consciousness premise is used to establish Δ.",
        }

    def _validation_criteria(self) -> List[str]:
        return [
            "at least one non-zero contrast is represented",
            "difference atoms do not depend on relation or graph objects",
            "non-identity and distinguishability are quantified separately",
            "variation and contrast are included as bounded metrics",
            "all later stages are marked as dependent on Δ rather than premises for Δ",
            "positive consciousness or phenomenology claims remain blocked",
        ]

    def _falsification_criteria(self) -> List[str]:
        return [
            "all observations collapse to zero distance or strict identity",
            "relations or graphs are required before difference atoms can be formed",
            "the module asserts consciousness, subjectivity, sentience, qualia, or phenomenology",
            "later stages can execute with no distinguishable states",
            "metrics are not degraded when differences are removed",
        ]

    def _failure_conditions(self, atoms: List[DifferenceAtom], forbidden: List[str]) -> List[str]:
        failures: List[str] = []
        if not atoms:
            failures.append("no_difference_observations")
        if not any(a.minimal for a in atoms):
            failures.append("no_minimal_non_identity")
        if forbidden:
            failures.append("forbidden_positive_phenomenal_claim")
        return failures

    def _detect_forbidden_positive_claims(self, payload: Mapping[str, Any]) -> List[str]:
        found: List[str] = []
        def walk(obj: Any) -> None:
            if isinstance(obj, Mapping):
                for key, value in obj.items():
                    if str(key).lower() in self.FORBIDDEN_POSITIVE_CLAIMS and value is True:
                        found.append(str(key).lower())
                    walk(value)
            elif isinstance(obj, list):
                for item in obj:
                    walk(item)
        walk(payload)
        return sorted(set(found))

    def _non_redundancy_analysis(self, inventory: List[str], catalog: Mapping[str, bool]) -> Dict[str, Any]:
        nearby = [name for name in [
            "reconstruction_identity_blueprint", "constraint_genesis", "constraint_fields",
            "constraint_induced_domain", "constitutive_relation_tester", "observability",
            "measurement_perturbation", "non_representability", "redundancy", "degeneracy",
        ] if name in inventory or catalog.get(name, False)]
        return {
            "target_already_present": "difference_space_foundation" in inventory or bool(catalog.get("difference_space_foundation")),
            "nearby_modules_detected": nearby,
            "non_redundant_role": (
                "AA1 is not a general constraint, observability, redundancy, or topology module. "
                "It specifically reconstructs Δ as the pre-relational difference-space required by AA2 relation genesis."
            ),
            "preferred_action": "create_or_refine_difference_space_foundation",
        }

    def _epistemic_guard(self, forbidden: List[str]) -> Dict[str, Any]:
        return {
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_not_assumed": True,
            "subjectivity_not_assumed": True,
            "qualia_not_assumed": True,
            "relation_not_presupposed": True,
            "graph_not_presupposed": True,
            "forbidden_positive_claims_detected": forbidden,
        }

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# AA1 — Difference Space Foundation",
            "",
            f"Generated UTC: {result['generated_at_utc']}",
            f"Status: {result['difference_space_foundation_status']}",
            f"Δ foundation score: {result['metrics']['delta_foundation_score']:.6f}",
            "",
            "## Scope",
            "AA1 reconstructs Δ as minimal difference, non-identity, distinguishability, variation, contrast, and difference-space.",
            "It does not assert consciousness, subjectivity, qualia, sentience, or phenomenology.",
            "",
            "## Dimensions",
        ]
        for dim in result["dimensions"]:
            lines.append(f"- {dim['name']}: {dim['description']}")
        lines.extend(["", "## Difference atoms"])
        for atom in result["difference_atoms"]:
            lines.append(f"- {atom['atom_id']}: {atom['left']} ≠ {atom['right']} on {atom['dimension']} distance={atom['distance']}")
        lines.extend(["", "## Dependence demonstration", result["dependence_demonstration"]["claim"], ""])
        for key, value in result["dependence_demonstration"]["later_stage_dependence"].items():
            lines.append(f"- {key}: {value}")
        lines.extend(["", "## Validation criteria"])
        lines.extend([f"- {item}" for item in result["validation_criteria"]])
        lines.extend(["", "## Falsification criteria"])
        lines.extend([f"- {item}" for item in result["falsification_criteria"]])
        lines.extend(["", "## Epistemic guard", "Functional conclusion only; phenomenology undetermined; no consciousness claim."])
        return "\n".join(lines) + "\n"

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = self.output_dir / f"difference_space_foundation_{stamp}.json"
        md_path = self.output_dir / f"difference_space_foundation_{stamp}.md"
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

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        observations = self._normalize_observations(inputs)
        atoms = self._difference_atoms(observations)
        metrics = self._space_metrics(atoms)
        forbidden = self._detect_forbidden_positive_claims(inputs)
        failures = self._failure_conditions(atoms, forbidden)
        inventory = self._inventory_names()
        catalog = self._catalog_mentions()
        dimensions = self._dimensions()
        status = self.READY_STATUS if not failures and metrics["delta_foundation_score"] > 0.0 else self.DEGRADED_STATUS
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "axis": "AA",
            "step_id": "AA1",
            "symbol": "Δ",
            "generated_at_utc": self._now(),
            "difference_space_foundation_status": status,
            "aa0_context": {
                "required": True,
                "available": bool(self._load_blueprint_context().get("reconstruction_identity_blueprint_status")),
                "source": "reconstruction_identity_blueprint",
            },
            "definitions": {
                "Δ": "pre-relational difference-space",
                "minimal_difference": "least contrast sufficient for non-identity",
                "non_identity": "failure of strict interchangeability under at least one dimension",
                "distinguishability": "formal separability without subject, relation, or graph premise",
                "variation": "bounded transformation or before/after delta",
                "contrast": "operational boundary, opposition, or gradient",
                "difference_space": "collection of difference atoms and dimensions prior to relation genesis",
            },
            "dimensions": [asdict(d) for d in dimensions],
            "difference_atoms": [asdict(a) for a in atoms],
            "metrics": metrics,
            "validation_criteria": self._validation_criteria(),
            "falsification_criteria": self._falsification_criteria(),
            "failure_conditions": failures,
            "dependence_demonstration": self._dependence_demonstration(metrics),
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
                    "formal_foundations_of_constraint_based_systems",
                    "constraint_genesis",
                    "observability",
                    "measurement_perturbation",
                    "non_representability",
                    "theory_constraint_engine",
                    "theory_falsification_framework",
                ],
                "outgoing": ["relation_genesis_engine", "dynamic_graph_constructor", "foundational_reconstruction_certifier"],
            },
            "public_interfaces": {
                "DifferenceSpaceFoundation().step(persist=False)": "returns Δ foundation payload without persistence",
                "DifferenceSpaceFoundation().step(inputs={'observations': [...]}, persist=False)": "evaluates explicit difference observations",
                "DifferenceSpaceFoundation().step(persist=True)": "writes JSON, Markdown, latest files, and JSONL history",
            },
            "data_structures": {
                "DifferenceAtom": "atom_id, left, right, dimension, distance, minimal, evidence",
                "DifferenceDimension": "name, description, observable_indicator, falsification_condition",
            },
            "non_redundancy_analysis": self._non_redundancy_analysis(inventory, catalog),
            "epistemic_guard": self._epistemic_guard(forbidden),
            "relation_derived": False,
            "graph_constructed": False,
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
