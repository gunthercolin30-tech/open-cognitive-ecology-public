"""AW11 — ecological stability analyzer.

Functional analysis of RF ecology stability, resilience, diversity, fragility,
robustness, loss tolerance, and future-openness preservation.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class EcologicalStabilityAnalyzer:
    primitive = "ECOLOGICAL_STABILITY_ANALYZER"
    step_id = "AW11"
    public_schema_version = "1.0"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "rf_ecology" / "AW11_ecological_stability"
        self.output_path = self.output_dir / "latest_ecological_stability_analysis.json"

    def _mapping(self, value: Any) -> Dict[str, Any]:
        return dict(value) if isinstance(value, Mapping) else {}

    def _list(self, value: Any) -> List[Any]:
        return list(value) if isinstance(value, list) else []

    def _bounded(self, value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return default
        if not math.isfinite(number):
            return default
        return round(max(0.0, min(1.0, number)), 6)

    def _hash(self, value: Any) -> str:
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=repr)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _utc(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _extract(self, inputs: Mapping[str, Any], key: str, *aliases: str) -> Dict[str, Any]:
        upstream = inputs.get("upstream_results")
        containers = [inputs]
        if isinstance(upstream, Mapping):
            containers.append(upstream)
        for container in containers:
            for name in (key,) + aliases:
                value = container.get(name)
                if isinstance(value, Mapping):
                    return dict(value)
        return {}

    def _records(self, registry: Mapping[str, Any]) -> List[Dict[str, Any]]:
        values = registry.get("registry", registry.get("rf_records", []))
        return [dict(v) for v in self._list(values) if isinstance(v, Mapping)]

    def _diversity(self, records: List[Mapping[str, Any]]) -> Dict[str, float]:
        count = len(records)
        if count < 2:
            return {"nominal_diversity_score": 0.0, "lineage_diversity_score": 0.0, "effective_diversity_score": 0.0}
        lineages = {
            str(r.get("lineage_id", r.get("origin_lineage_id", r.get("rf_id", "")))).strip()
            for r in records
            if str(r.get("lineage_id", r.get("origin_lineage_id", r.get("rf_id", "")))).strip()
        }
        signatures = {
            self._hash({
                "type": r.get("rf_type", r.get("type")),
                "capabilities": sorted(str(x) for x in self._list(r.get("capabilities"))),
                "roles": sorted(str(x) for x in self._list(r.get("roles"))),
            })
            for r in records
        }
        nominal = self._bounded((count - 1) / max(1, count))
        lineage = self._bounded(len(lineages) / count)
        effective = self._bounded((lineage + len(signatures) / count) / 2.0)
        return {
            "nominal_diversity_score": nominal,
            "lineage_diversity_score": lineage,
            "effective_diversity_score": effective,
        }

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        source = dict(inputs) if isinstance(inputs, Mapping) else {}
        registry = self._extract(source, "multi_rf_registry", "rf_registry", "AW1")
        graph = self._extract(source, "interaction_graph", "AW2")
        conflicts = self._extract(source, "conflict_detection", "conflict_detector", "AW5")
        fragmentation = self._extract(source, "reference_frame_fragmentation", "AW7")
        memory = self._extract(source, "civilizational_memory", "civilizational_memory_engine", "AW8")
        collective = self._extract(source, "collective_rf_analysis", "collective_consciousness_analyzer", "AW9")
        dashboard = self._extract(source, "ecology_dashboard", "AW10")

        thresholds = {
            "minimum_population_size": 2,
            "minimum_stability_score": 0.55,
            "minimum_resilience_score": 0.50,
            "minimum_effective_diversity_score": 0.40,
            "minimum_robustness_score": 0.50,
            "maximum_fragility_score": 0.50,
            "minimum_future_openness_score": 0.50,
        }
        custom = source.get("thresholds")
        if isinstance(custom, Mapping):
            for key in thresholds:
                if key in custom:
                    if key == "minimum_population_size":
                        try:
                            thresholds[key] = max(1, int(custom[key]))
                        except (TypeError, ValueError):
                            pass
                    else:
                        thresholds[key] = self._bounded(custom[key], thresholds[key])

        records = self._records(registry)
        population_size = len(records) or int(registry.get("registry_count", registry.get("rf_count", 0)) or 0)
        diversity = self._diversity(records)

        coordination = self._mapping(collective.get("distributed_coordination_structure"))
        collective_structure = self._mapping(collective.get("collective_rf_structure"))
        interaction_density = self._bounded(coordination.get("interaction_density", graph.get("density", 0.0)))
        centralization = self._bounded(collective.get("centralization_risk_score", coordination.get("centralization_risk_score", 1.0)))
        autonomy = self._bounded(collective.get("local_autonomy_score", coordination.get("local_autonomy_score", 1.0 - centralization)))
        conflict_pressure = self._bounded(collective.get("conflict_pressure_score", collective_structure.get("conflict_pressure_score", 0.0)))
        fragmentation_pressure = self._bounded(collective.get("fragmentation_pressure_score", collective_structure.get("fragmentation_pressure_score", 0.0)))
        integration = self._bounded(collective.get("functional_collective_integration", collective.get("integration_score", 0.0)))

        availability = self._bounded(memory.get("availability_score", 0.0))
        loss_tolerance = self._bounded(memory.get("loss_tolerance_score", 0.0))
        lineage_preservation = self._bounded(memory.get("lineage_preservation_score", diversity["lineage_diversity_score"]))
        openness = self._bounded(memory.get("future_openness_preservation_score", 0.0))
        recovery_status = str(memory.get("recovery_status", "")).upper()
        recovery_capacity = self._bounded(memory.get("recovery_score", 1.0 if "READY" in recovery_status else availability * loss_tolerance))

        redundancy_score = self._bounded((interaction_density + availability + loss_tolerance) / 3.0)
        robustness_score = self._bounded(0.30 * loss_tolerance + 0.25 * autonomy + 0.20 * redundancy_score + 0.15 * lineage_preservation + 0.10 * integration)
        resilience_score = self._bounded(0.30 * recovery_capacity + 0.25 * robustness_score + 0.20 * availability + 0.15 * openness + 0.10 * (1.0 - fragmentation_pressure))
        fragility_score = self._bounded(0.30 * centralization + 0.25 * conflict_pressure + 0.25 * fragmentation_pressure + 0.20 * (1.0 - redundancy_score))
        diversity_score = self._bounded(0.45 * diversity["effective_diversity_score"] + 0.35 * lineage_preservation + 0.20 * autonomy)
        protective = self._bounded(0.20 * robustness_score + 0.20 * resilience_score + 0.15 * diversity_score + 0.15 * integration + 0.15 * availability + 0.15 * openness)
        stability_score = self._bounded(protective - 0.35 * fragility_score)

        risk_factors: List[str] = []
        if population_size < thresholds["minimum_population_size"]:
            risk_factors.append("INSUFFICIENT_RF_POPULATION")
        if resilience_score < thresholds["minimum_resilience_score"]:
            risk_factors.append("RESILIENCE_BELOW_THRESHOLD")
        if diversity["effective_diversity_score"] < thresholds["minimum_effective_diversity_score"]:
            risk_factors.append("EFFECTIVE_DIVERSITY_BELOW_THRESHOLD")
        if robustness_score < thresholds["minimum_robustness_score"]:
            risk_factors.append("ROBUSTNESS_BELOW_THRESHOLD")
        if fragility_score > thresholds["maximum_fragility_score"]:
            risk_factors.append("FRAGILITY_ABOVE_THRESHOLD")
        if openness < thresholds["minimum_future_openness_score"]:
            risk_factors.append("FUTURE_OPENNESS_BELOW_THRESHOLD")
        if stability_score < thresholds["minimum_stability_score"]:
            risk_factors.append("ECOLOGICAL_STABILITY_BELOW_THRESHOLD")

        ready = not risk_factors
        status = "ECOLOGICAL_STABILITY_ANALYSIS_READY" if ready else "ECOLOGICAL_STABILITY_ANALYSIS_NOT_READY"
        protective_factors = [name for name, score in {
            "DISTRIBUTED_AUTONOMY": autonomy,
            "MEMORY_AVAILABILITY": availability,
            "LOSS_TOLERANCE": loss_tolerance,
            "LINEAGE_PRESERVATION": lineage_preservation,
            "FUTURE_OPENNESS": openness,
            "FUNCTIONAL_INTEGRATION": integration,
        }.items() if score >= 0.5]

        breakdown = {
            "stability_score": stability_score,
            "resilience_score": resilience_score,
            "diversity_score": diversity_score,
            "effective_diversity_score": diversity["effective_diversity_score"],
            "lineage_diversity_score": diversity["lineage_diversity_score"],
            "fragility_score": fragility_score,
            "robustness_score": robustness_score,
            "loss_tolerance_score": loss_tolerance,
            "recovery_capacity_score": recovery_capacity,
            "redundancy_score": redundancy_score,
            "centralization_risk_score": centralization,
            "conflict_pressure_score": conflict_pressure,
            "fragmentation_pressure_score": fragmentation_pressure,
            "memory_availability_score": availability,
            "local_autonomy_score": autonomy,
            "lineage_preservation_score": lineage_preservation,
            "future_openness_preservation_score": openness,
            "functional_collective_integration": integration,
        }
        hash_payload = {
            "population_size": population_size,
            "thresholds": thresholds,
            "breakdown": breakdown,
            "risk_factors": sorted(risk_factors),
            "protective_factors": sorted(protective_factors),
            "source_hashes": {
                "registry": registry.get("registry_hash"),
                "graph": graph.get("graph_hash"),
                "memory": memory.get("memory_hash"),
                "collective": collective.get("analysis_hash"),
                "dashboard": dashboard.get("dashboard_hash"),
            },
        }
        analysis_hash = self._hash(hash_payload)
        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._utc(),
            "status": status,
            "ecological_stability_status": status,
            "ecological_stability_analysis_ready": ready,
            "population_size": population_size,
            **breakdown,
            "stability_breakdown": breakdown,
            "risk_factors": sorted(risk_factors),
            "protective_factors": sorted(protective_factors),
            "thresholds": thresholds,
            "analysis_hash": analysis_hash,
            "stability_hash": analysis_hash,
            "epistemic_scope": "functional_rf_ecology_stability_only",
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "persisted": False,
            "output_path": None,
        }
        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            result["persisted"] = True
            result["output_path"] = str(self.output_path)
            self.output_path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        return result
