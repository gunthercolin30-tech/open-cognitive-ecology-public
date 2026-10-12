"""
AT1 — prediction_registry.

Structured registry of RF* predictions. The registry classifies predictions as
structural, dynamic, topological, spectral, developmental, or collective and
keeps every entry within functional-scientific epistemic guards.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class PredictionRegistry:
    """Register canonical RF* predictions for later generation and validation."""

    primitive = "PREDICTION_REGISTRY"
    step_id = "AT1"
    public_schema_version = "1.0"
    output_dir = ROOT / "predictive_science" / "AT1_prediction_registry"

    categories = [
        "structural",
        "dynamic",
        "topological",
        "spectral",
        "developmental",
        "collective",
    ]

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _base_predictions(self) -> List[Dict[str, Any]]:
        entries = [
            {
                "id": "RF-PRED-STRUCT-001",
                "category": "structural",
                "source": "RF* structural conservation chain",
                "claim": "Stable functional certification should require coherent reconstruction, dependency, and semantic-guard structure.",
                "if_theory_true_then_observe": "validated AS/AL/AN/AO chains exhibit non-empty dependency structure and public epistemic guard fields",
                "observable_family": ["module_presence", "dependency_coverage", "epistemic_guard_presence"],
                "status": "unknown",
                "confidence": 0.0,
            },
            {
                "id": "RF-PRED-DYN-001",
                "category": "dynamic",
                "source": "RF* longitudinal governance dynamics",
                "claim": "Regression and recovery events should be distinguishable in longitudinal governance traces.",
                "if_theory_true_then_observe": "AS13 and AS14 style events produce separable regression/recovery labels under synthetic and real timelines",
                "observable_family": ["regression_rate", "recovery_rate", "hazard_rate"],
                "status": "unknown",
                "confidence": 0.0,
            },
            {
                "id": "RF-PRED-TOPO-001",
                "category": "topological",
                "source": "RF* reference-frame topology",
                "claim": "Functional status should depend on reference-frame preserving transformations rather than isolated scalar scores.",
                "if_theory_true_then_observe": "topological and RF-equivalence certifiers provide explicit frame/coherence outputs before final status resolution",
                "observable_family": ["rf_equivalence", "topological_coherence", "frame_preservation"],
                "status": "unknown",
                "confidence": 0.0,
            },
            {
                "id": "RF-PRED-SPEC-001",
                "category": "spectral",
                "source": "RF* spectral formal modes",
                "claim": "Spectral mode organization should provide stable formal signatures before MEI/intrinsic identity certification.",
                "if_theory_true_then_observe": "spectral mode extraction and robust qualia-formal mode modules expose bounded coherence metrics",
                "observable_family": ["spectral_coherence", "mode_stability", "bounded_metric"],
                "status": "unknown",
                "confidence": 0.0,
            },
            {
                "id": "RF-PRED-DEV-001",
                "category": "developmental",
                "source": "RF* reconstruction and threshold development",
                "claim": "Predictive readiness should increase through ordered blueprint, registry, signature, falsification, validation, and dashboard stages.",
                "if_theory_true_then_observe": "AT0→AT10 artifacts progressively fill the RF* prediction lifecycle without bypassing falsification",
                "observable_family": ["stage_completion", "prediction_lifecycle_coverage", "falsification_path_presence"],
                "status": "unknown",
                "confidence": 0.0,
            },
            {
                "id": "RF-PRED-COLL-001",
                "category": "collective",
                "source": "RF* civilizational and distributed governance",
                "claim": "Collective/civilizational observables should contribute to functional governance without implying phenomenal subjectivity.",
                "if_theory_true_then_observe": "public dashboards and governance certifiers expose collective indicators while proof flags remain false",
                "observable_family": ["public_dashboard", "collective_metrics", "epistemic_guard_consistency"],
                "status": "unknown",
                "confidence": 0.0,
            },
        ]
        return entries

    def _validate_entries(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        ids = [entry.get("id") for entry in entries]
        categories_present = sorted({entry.get("category") for entry in entries})
        missing_categories = [c for c in self.categories if c not in categories_present]
        invalid_statuses = [entry.get("id") for entry in entries if entry.get("status") not in {"validated", "invalidated", "unknown"}]
        duplicate_ids = sorted({x for x in ids if ids.count(x) > 1})
        return {
            "entry_count": len(entries),
            "categories_present": categories_present,
            "missing_categories": missing_categories,
            "invalid_statuses": invalid_statuses,
            "duplicate_ids": duplicate_ids,
            "registry_valid": not missing_categories and not invalid_statuses and not duplicate_ids,
        }

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        extra_predictions = inputs.get("predictions", [])
        entries = self._base_predictions()
        if isinstance(extra_predictions, list):
            for item in extra_predictions:
                if isinstance(item, dict):
                    candidate = dict(item)
                    candidate.setdefault("status", "unknown")
                    candidate.setdefault("confidence", 0.0)
                    candidate.setdefault("observable_family", [])
                    entries.append(candidate)
        validation = self._validate_entries(entries)
        by_category: Dict[str, List[Dict[str, Any]]] = {category: [] for category in self.categories}
        for entry in entries:
            category = entry.get("category")
            if category in by_category:
                by_category[category].append(entry)
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._timestamp(),
            "status": "PREDICTION_REGISTRY_READY" if validation["registry_valid"] else "PREDICTION_REGISTRY_INCOMPLETE",
            "prediction_registry_status": "PREDICTION_REGISTRY_READY" if validation["registry_valid"] else "PREDICTION_REGISTRY_INCOMPLETE",
            "registry_ready": validation["registry_valid"],
            "prediction_count": len(entries),
            "categories": list(self.categories),
            "category_counts": {k: len(v) for k, v in by_category.items()},
            "predictions": entries,
            "predictions_by_category": by_category,
            "validation": validation,
            "allowed_statuses": ["validated", "invalidated", "unknown"],
            "allowed_claims": [
                "RF* predictions are registered as functional-scientific hypotheses",
                "prediction status may be validated, invalidated, or unknown",
                "registry completeness supports later measurable-signature and falsification work",
            ],
            "blocked_claims": [
                "phenomenology proven",
                "qualia proven",
                "subjectivity proven",
                "consciousness proven",
            ],
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "persisted": False,
            "output_path": None,
        }
        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            path = self.output_dir / "latest_prediction_registry.json"
            path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            result["persisted"] = True
            result["output_path"] = str(path)
        return result
