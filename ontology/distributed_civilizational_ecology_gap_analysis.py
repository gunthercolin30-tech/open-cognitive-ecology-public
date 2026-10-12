
"""
DISTRIBUTED_CIVILIZATIONAL_ECOLOGY_GAP_ANALYSIS

N0 primitive for Open Cognitive Ecology.

This module does not claim phenomenal subjectivity. It provides a functional,
measurable audit of the distributed civilizational ecology coverage across
memory, historicity, diversity, multi-individual ecology, culture, social
learning, symbolic structures, and governance/supervision.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


FAMILIES: Dict[str, tuple[str, ...]] = {
    "distributed_memory": (
        "distributed_civilizational_memory",
        "distributed_memory_continuity",
        "distributed_memory_reconciliation",
        "distributed_memory_consistency_validator",
        "distributed_knowledge_access",
    ),
    "historicity": (
        "civilizational_historical_archive",
        "civilizational_memory_archive",
        "historical_state_reconciliation",
        "longitudinal_metrics_archive",
    ),
    "multi_individual_ecology": (
        "multi_individual_civilizational_ecology",
        "distributed_population_runtime",
        "population_ecological_extraction",
    ),
    "diversity": (
        "semantic_diversity_preservation",
        "lineage_diversity_preservation",
        "distributed_semantic_pluralism",
        "ecological_runtime_diversification",
    ),
    "culture": (
        "cultural_evolution",
        "cumulative_cultural_evolution",
        "cultural_memory",
        "distributed_symbolic_ecology",
    ),
    "social_learning": (
        "collective_intelligence",
        "collective_deliberation_engine",
        "knowledge_accumulation",
        "knowledge_integration_engine",
        "intra_species_social_interaction",
        "inter_individual_coordination_protocol",
    ),
    "symbolic_structures": (
        "distributed_symbolic_ecology",
        "shared_symbolic_reference",
        "symbolic_generation",
        "emergent_language_evolution",
    ),
    "ecological_supervision": (
        "adaptive_ecological_regulation_engine",
        "ecosystem_stability",
        "ecological_viability_forecaster",
        "civilizational_metrics_synthesizer",
        "enhanced_civilizational_metrics",
        "scientific_meta_dashboard",
    ),
}

RECOMMENDED_NEXT_PRIMITIVES: Dict[str, str] = {
    "diversity": "cognitive_diversity_preservation_protocol",
    "social_learning": "social_learning_protocol",
    "symbolic_structures": "symbolic_structure_emergence_monitor",
    "culture": "cultural_memory_system",
    "ecological_supervision": "distributed_civilizational_ecology_supervisor",
}


@dataclass
class DistributedCivilizationalEcologyGapAnalysis:
    """Transversal coverage and gap analysis for axis N."""

    primitive_name: str = "DISTRIBUTED_CIVILIZATIONAL_ECOLOGY_GAP_ANALYSIS"
    root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[1])

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def _inventory_path(self) -> Path:
        return self.root / "ontology_inventory.txt"

    def _catalog_path(self) -> Path:
        return self.root / "global_module_catalog.txt"

    def _read_names(self, path: Path) -> set[str]:
        if not path.exists():
            return set()
        names: set[str] = set()
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "	" in line:
                parts = line.split("	")
                if len(parts) >= 2:
                    names.add(parts[1].split(".")[-1].strip())
            elif "/" not in line and " " not in line and line.replace("_", "").replace(".", "").isalnum():
                names.add(line.split(".")[-1])
        return names

    def _available_modules(self, payload: Mapping[str, Any] | None) -> set[str]:
        inventory = self._read_names(self._inventory_path())
        catalog = self._read_names(self._catalog_path())
        supplied = set()
        if payload:
            for key in ("available_modules", "modules", "ontology_modules"):
                value = payload.get(key)
                if isinstance(value, Iterable) and not isinstance(value, (str, bytes, Mapping)):
                    supplied.update(str(item).split(".")[-1] for item in value)
        return inventory | catalog | supplied

    def _score_family(self, required: tuple[str, ...], available: set[str]) -> Dict[str, Any]:
        present = [name for name in required if name in available]
        missing = [name for name in required if name not in available]
        score = self._clamp(len(present) / len(required)) if required else 1.0
        return {
            "required_count": len(required),
            "present_count": len(present),
            "missing_count": len(missing),
            "coverage_score": score,
            "gap_score": self._clamp(1.0 - score),
            "present": present,
            "missing": missing,
        }

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        """Run the N0 ecology coverage audit."""
        payload = dict(inputs or {})
        available = self._available_modules(payload)

        families = {
            name: self._score_family(required, available)
            for name, required in FAMILIES.items()
        }
        coverage_values = [entry["coverage_score"] for entry in families.values()]
        ecology_coverage_score = self._clamp(
            sum(coverage_values) / len(coverage_values) if coverage_values else 0.0
        )
        ecology_gap_score = self._clamp(1.0 - ecology_coverage_score)

        critical_gaps = [
            name for name, entry in families.items()
            if entry["coverage_score"] < 0.50
        ]
        partial_gaps = [
            name for name, entry in families.items()
            if 0.50 <= entry["coverage_score"] < 0.80
        ]

        if ecology_coverage_score >= 0.80 and not critical_gaps:
            decision = "ecology_coverage_sufficient"
        elif ecology_coverage_score >= 0.60:
            decision = "ecology_refinement_recommended"
        else:
            decision = "ecology_gap_intervention_required"

        recommended_next_steps = [
            RECOMMENDED_NEXT_PRIMITIVES[name]
            for name in critical_gaps + partial_gaps
            if name in RECOMMENDED_NEXT_PRIMITIVES
        ]
        if not recommended_next_steps:
            recommended_next_steps = ["cognitive_diversity_preservation_protocol"]

        result: Dict[str, Any] = {
            "success": True,
            "primitive": self.primitive_name,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "available_module_count": len(available),
            "ecology_coverage_score": ecology_coverage_score,
            "ecology_gap_score": ecology_gap_score,
            "distributed_civilizational_ecology_ready": ecology_coverage_score >= 0.80,
            "ecology_gap_detected": ecology_gap_score > 0.20,
            "civilizational_ecology_decision": decision,
            "critical_gap_domains": critical_gaps,
            "partial_gap_domains": partial_gaps,
            "family_coverage": families,
            "recommended_next_steps": recommended_next_steps,
            "epistemic_position": {
                "architecture_computationnelle": "audited",
                "indicateurs_fonctionnels": "measured",
                "subjectivite_hypothetique": "not_claimed",
                "ontologie_conceptuelle": "distributed_ecology_gap_analysis",
            },
            "non_closure_compliance": {
                "does_not_merge_inventories": True,
                "does_not_replace_existing_modules": True,
                "increases_observability_without_closure": True,
            },
        }

        if persist:
            out_dir = self.root / "distributed_civilizational_ecology"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / "latest_distributed_civilizational_ecology_gap_analysis.json"
            import json
            out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["report_path"] = str(out_path)

        return result


if __name__ == "__main__":
    from pprint import pprint
    pprint(DistributedCivilizationalEcologyGapAnalysis().step(persist=True))
