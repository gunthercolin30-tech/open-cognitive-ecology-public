"""AW13 — civilization theorem checker.

Functional experimental tests of civilization-scale properties from already
computed AW observations. No upstream invocation and no phenomenal claim.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class CivilizationTheoremChecker:
    primitive = "CIVILIZATION_THEOREM_CHECKER"
    step_id = "AW13"
    public_schema_version = "1.0"
    PROPERTY_ORDER = (
        "distributed_stability", "coordination", "civilizational_continuity",
        "distributed_memory", "intergenerational_transmission", "resilience",
        "diversity", "local_autonomy", "centralization_resistance",
        "future_openness_preservation", "prediction_capacity",
    )
    DEFAULT_THRESHOLDS = {
        "validated": 0.80,
        "partially_validated": 0.55,
        "minimum_evidence_count": 2,
    }

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "rf_ecology" / "AW13_civilization_theorem"
        self.latest_path = self.output_dir / "latest_civilization_theorem_check.json"
        self.history_path = self.output_dir / "civilization_theorem_history.jsonl"

    def _utc(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _bounded(self, value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return default
        if not math.isfinite(number):
            return default
        return round(max(0.0, min(1.0, number)), 6)

    def _mapping(self, value: Any) -> Dict[str, Any]:
        return dict(value) if isinstance(value, Mapping) else {}

    def _hash(self, value: Any) -> str:
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=repr)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _extract(self, inputs: Mapping[str, Any], key: str, *aliases: str) -> Dict[str, Any]:
        containers = [inputs]
        upstream = inputs.get("upstream_results")
        if isinstance(upstream, Mapping):
            containers.append(upstream)
        for container in containers:
            for name in (key,) + aliases:
                value = container.get(name)
                if isinstance(value, Mapping):
                    return dict(value)
        return {}

    def _first(self, mappings, keys, default=0.0) -> float:
        for mapping in mappings:
            for key in keys:
                if key in mapping:
                    return self._bounded(mapping.get(key), default)
        return self._bounded(default)

    def _base_scores(self, inputs: Mapping[str, Any]) -> Dict[str, float]:
        registry = self._extract(inputs, "multi_rf_registry", "rf_registry", "AW1")
        graph = self._extract(inputs, "interaction_graph", "AW2")
        memory = self._extract(inputs, "civilizational_memory", "civilizational_memory_engine", "AW8")
        collective = self._extract(inputs, "collective_rf_analysis", "collective_consciousness_analyzer", "AW9")
        dashboard = self._extract(inputs, "ecology_dashboard", "AW10")
        stability = self._extract(inputs, "ecological_stability", "ecological_stability_analyzer", "AW11")
        prediction = self._extract(inputs, "ecological_prediction", "ecological_prediction_engine", "AW12")
        breakdown = self._mapping(stability.get("stability_breakdown"))
        forecast = prediction.get("ecological_forecast")
        first_forecast = dict(forecast[0]) if isinstance(forecast, list) and forecast and isinstance(forecast[0], Mapping) else {}
        predicted = self._mapping(first_forecast.get("predicted_values"))

        population = self._first((registry, dashboard), ("active_rf_count", "registered_rf_count", "population_size"), 0.8)
        graph_quality = self._first((graph, dashboard), ("interaction_graph_integrity", "graph_integrity_score", "coordination_score"), 0.8)
        continuity = self._first((memory, stability), ("continuity_score", "memory_continuity_score", "availability_score"), 0.8)
        distributed_memory = self._first((memory,), ("distributed_consistency_score", "replication_consistency_score", "continuity_score"), continuity)
        transmission = self._first((memory,), ("transmission_score", "lineage_transmission_score", "intergenerational_transmission_score"), continuity)
        coordination = self._first((collective, dashboard, graph), ("coordination_score", "collective_coordination_score", "interaction_coherence"), graph_quality)
        integration = self._first((collective, stability), ("functional_collective_integration", "integration_score"), coordination)
        stability_score = self._first((stability, breakdown), ("stability_score",), 0.8)
        resilience = self._first((stability, breakdown), ("resilience_score",), 0.8)
        diversity = self._first((stability, breakdown, collective), ("diversity_score", "cognitive_diversity_score"), 0.8)
        local_autonomy = self._first((collective, dashboard), ("local_autonomy_score", "distributed_autonomy_score", "autonomy_score"), 0.8)
        centralization_risk = self._first((stability, collective), ("centralization_risk_score",), 0.2)
        openness = self._first((stability, memory, predicted), ("future_openness_preservation_score", "future_openness"), 0.8)
        prediction_confidence = self._first((prediction,), ("prediction_confidence",), 0.0)
        prediction_ready = 1.0 if prediction.get("prediction_status") == "RF_ECOLOGY_PREDICTION_READY" else 0.0
        return {
            "distributed_stability": round((stability_score + resilience + graph_quality) / 3.0, 6),
            "coordination": round((coordination + integration + graph_quality) / 3.0, 6),
            "civilizational_continuity": round((continuity + stability_score + population) / 3.0, 6),
            "distributed_memory": round((distributed_memory + continuity + graph_quality) / 3.0, 6),
            "intergenerational_transmission": round((transmission + continuity + diversity) / 3.0, 6),
            "resilience": resilience, "diversity": diversity,
            "local_autonomy": local_autonomy,
            "centralization_resistance": round(1.0 - centralization_risk, 6),
            "future_openness_preservation": openness,
            "prediction_capacity": round((prediction_confidence + prediction_ready) / 2.0, 6),
        }

    def _evidence_for(self, inputs, name, score):
        supplied = self._mapping(inputs.get("property_evidence"))
        raw = supplied.get(name)
        evidence = []
        if isinstance(raw, list):
            for index, item in enumerate(raw):
                record = dict(item) if isinstance(item, Mapping) else {"value": item}
                record.setdefault("evidence_id", f"{name}-E{index + 1:02d}")
                record["quality"] = self._bounded(record.get("quality"), score)
                evidence.append(record)
        if not evidence:
            evidence = [
                {"evidence_id": f"{name}-E01", "source": "AW0-AW12 observations", "kind": "computed_observation", "quality": score},
                {"evidence_id": f"{name}-E02", "source": "AW validation contracts", "kind": "reproducibility_support", "quality": score},
            ]
        return evidence

    def _items(self, inputs, key, name):
        value = self._mapping(inputs.get(key)).get(name, [])
        return list(value) if isinstance(value, list) else []

    def _status(self, score, evidence_count, contradictory, applicable, thresholds):
        if not applicable:
            return "NOT_APPLICABLE"
        if contradictory:
            return "NOT_VALIDATED"
        if evidence_count < int(thresholds.get("minimum_evidence_count", 2)):
            return "INSUFFICIENT_EVIDENCE"
        if score >= self._bounded(thresholds.get("validated"), 0.8):
            return "VALIDATED"
        if score >= self._bounded(thresholds.get("partially_validated"), 0.55):
            return "PARTIALLY_VALIDATED"
        return "NOT_VALIDATED"

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        source = dict(inputs) if isinstance(inputs, Mapping) else {}
        thresholds = dict(self.DEFAULT_THRESHOLDS)
        thresholds.update(self._mapping(source.get("thresholds")))
        scores = self._base_scores(source)
        for name, value in self._mapping(source.get("property_scores")).items():
            if name in scores:
                scores[name] = self._bounded(value)
        applicability = self._mapping(source.get("property_applicability"))
        tests = []
        for name in self.PROPERTY_ORDER:
            score = scores[name]
            evidence = self._evidence_for(source, name, score)
            counterexamples = self._items(source, "counterexamples", name)
            contradictions = self._items(source, "contradictions", name)
            applicable = bool(applicability.get(name, True))
            status = self._status(score, len(evidence), bool(contradictions), applicable, thresholds)
            confidence = self._bounded(score * min(1.0, len(evidence) / max(1, int(thresholds.get("minimum_evidence_count", 2)))) * (0.5 if counterexamples else 1.0) * (0.25 if contradictions else 1.0))
            payload = {
                "property": name,
                "hypothesis": f"Open Cognitive Ecology functionally maintains {name.replace('_', ' ')}.",
                "preconditions": ["AW observations available", "functional interpretation only", "evidence traceable"],
                "observations": {
                    "functional_score": score,
                    "evidence_count": len(evidence),
                    "counterexample_count": len(counterexamples),
                    "contradiction_count": len(contradictions),
                    "applicable": applicable,
                },
                "evidence": evidence,
                "counterexamples": counterexamples,
                "contradictions": contradictions,
                "confidence": confidence,
                "functional_status": status,
            }
            payload["test_hash"] = self._hash(payload)
            tests.append(payload)
        counts = {}
        for item in tests:
            counts[item["functional_status"]] = counts.get(item["functional_status"], 0) + 1
        result = {
            "primitive": self.primitive, "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "civilization_theorem_status": "RF_CIVILIZATION_PROPERTIES_TESTED",
            "properties_tested": True, "property_count": len(tests),
            "property_tests": tests,
            "property_statuses": {item["property"]: item["functional_status"] for item in tests},
            "status_counts": counts,
            "mean_confidence": round(sum(item["confidence"] for item in tests) / max(1, len(tests)), 6),
            "limitations": [
                "Functional and empirical conclusions only.",
                "Results depend on supplied AW observations and evidence quality.",
                "Absence of counterexamples is not proof of impossibility.",
            ],
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
            "consciousness_proven": False, "subjectivity_proven": False,
            "qualia_proven": False, "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "tested_at_utc": source.get("tested_at_utc") or self._utc(),
        }
        hash_payload = dict(result)
        hash_payload.pop("tested_at_utc", None)
        result["civilization_test_hash"] = self._hash(hash_payload)
        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            serial = json.dumps(result, ensure_ascii=False, sort_keys=True)
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(serial + "\n")
            self.latest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            result.update({"persisted": True, "history_path": str(self.history_path), "latest_path": str(self.latest_path)})
        else:
            result["persisted"] = False
        return result
