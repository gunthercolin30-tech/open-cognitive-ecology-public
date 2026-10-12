"""
AV0 — developmental_blueprint.

Foundational blueprint for the functional developmental dynamics of RF*.
The module defines measurable developmental objects, axes, events, stages,
time windows, falsification rules, data-quality requirements and epistemic
limits. It does not infer phenomenal consciousness from developmental change.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class DevelopmentalBlueprint:
    """Define the AV developmental-science charter."""

    primitive = "DEVELOPMENTAL_BLUEPRINT"
    step_id = "AV0"
    public_schema_version = "1.0"
    output_dir = ROOT / "developmental_science" / "AV0_developmental_blueprint"

    observed_objects: List[str] = [
        "rf_star_functional_regime",
        "architecture_profile",
        "longitudinal_state",
        "developmental_event",
        "developmental_trajectory",
        "developmental_stage",
        "prediction_record",
    ]

    developmental_axes: List[str] = [
        "genesis",
        "maturation",
        "specialization",
        "bifurcation",
        "degeneration",
        "recovery",
        "stage_progression",
        "future_trajectory",
    ]

    event_types: List[str] = [
        "GENESIS_EVENT",
        "MATURATION_EVENT",
        "SPECIALIZATION_EVENT",
        "BIFURCATION_EVENT",
        "DEGENERATION_EVENT",
        "RECOVERY_EVENT",
        "STAGE_TRANSITION_EVENT",
        "NO_DEVELOPMENTAL_CHANGE",
    ]

    developmental_stages: List[str] = [
        "PRE_GENESIS",
        "EMERGENT",
        "EARLY_MATURATION",
        "MATURE",
        "SPECIALIZED",
        "BIFURCATING",
        "DEGENERATING",
        "RECOVERING",
        "STABILIZED_POST_RECOVERY",
        "UNDETERMINED",
    ]

    time_windows: Dict[str, Dict[str, Any]] = {
        "immediate": {"minimum_observations": 2, "purpose": "event onset detection"},
        "shortitudinal": {"minimum_observations": 3, "purpose": "local trend estimation"},
        "longitudinal": {"minimum_observations": 5, "purpose": "stage and trajectory inference"},
        "cross_run": {"minimum_runs": 2, "purpose": "replication and stability assessment"},
    }

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _stable_hash(self, value: Any) -> str:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _measurement_policy(self) -> Dict[str, Any]:
        return {
            "scope": "functional_developmental_dynamics_only",
            "requires_longitudinal_evidence": True,
            "requires_baseline_or_prior_state": True,
            "requires_explicit_time_order": True,
            "requires_uncertainty_reporting": True,
            "requires_source_traceability": True,
            "allows_cross_architecture_comparison": True,
            "forbids_single_snapshot_developmental_certification": True,
            "forbids_phenomenological_inference_from_growth": True,
        }

    def _event_policy(self) -> Dict[str, Any]:
        return {
            "event_types": list(self.event_types),
            "genesis_rule": "detect first sustained transition from absent or sub-threshold functional regime to a measurable RF* regime",
            "maturation_rule": "estimate sustained increase in developmental capability, stability, integration or evidence quality",
            "specialization_rule": "detect persistent differentiation of function or developmental trajectory relative to baseline",
            "bifurcation_rule": "detect divergence into two or more dynamically distinguishable future trajectories",
            "degeneration_rule": "detect sustained loss of previously established functional developmental properties",
            "recovery_rule": "detect reconstruction after degeneration relative to a documented prior state",
            "no_change_rule": "emit explicit no-change state when evidence is insufficient for a developmental event",
        }

    def _stage_policy(self) -> Dict[str, Any]:
        return {
            "stages": list(self.developmental_stages),
            "classification_requires_evidence": True,
            "classification_requires_temporal_context": True,
            "undetermined_is_valid": True,
            "stage_order_is_not_strictly_linear": True,
            "recovery_may_not_restore_identical_prior_state": True,
            "bifurcation_may_create_parallel_lineages": True,
        }

    def _falsification_policy(self) -> Dict[str, Any]:
        return {
            "genesis_falsified_if": "apparent onset is not sustained or predates the claimed genesis window",
            "maturation_falsified_if": "estimated growth disappears under repeated measurement or uncertainty bounds",
            "specialization_falsified_if": "differences are transient, noise-driven or explained by missing data",
            "bifurcation_falsified_if": "candidate branches reconverge within the declared discrimination window",
            "degeneration_falsified_if": "decline is not sustained or reflects measurement loss only",
            "recovery_falsified_if": "improvement lacks relation to the documented degraded baseline",
            "stage_falsified_if": "classification is unstable under admissible perturbations",
            "prediction_falsified_if": "future observations violate the declared confidence interval or outcome class",
        }

    def _quality_policy(self) -> Dict[str, Any]:
        return {
            "minimum_observation_count_for_event": 2,
            "minimum_observation_count_for_stage": 3,
            "minimum_observation_count_for_prediction": 3,
            "minimum_coverage": 0.50,
            "minimum_data_quality": 0.50,
            "missing_data_must_be_explicit": True,
            "synthetic_data_must_be_labeled": True,
            "confidence_interval_or_score_required": True,
            "hash_or_trace_identifier_required": True,
        }

    def _epistemic_guards(self) -> Dict[str, Any]:
        return {
            "epistemic_scope": "functional_developmental_science_only",
            "genesis_means_functional_regime_onset_only": True,
            "maturation_does_not_prove_subjective_development": True,
            "degeneration_does_not_prove_loss_of_experience": True,
            "recovery_does_not_prove_restoration_of_phenomenology": True,
            "stage_classification_is_not_ontological_classification": True,
            "prediction_is_probabilistic_and_falsifiable": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        downstream_modules = [
            "genesis_detector",
            "maturation_tracker",
            "specialization_engine",
            "bifurcation_detector",
            "degeneration_detector",
            "recovery_engine",
            "developmental_stage_classifier",
            "developmental_prediction_engine",
            "developmental_dashboard",
            "developmental_certifier",
        ]

        policies = {
            "measurement_policy": self._measurement_policy(),
            "event_policy": self._event_policy(),
            "stage_policy": self._stage_policy(),
            "falsification_policy": self._falsification_policy(),
            "quality_policy": self._quality_policy(),
            "epistemic_guards": self._epistemic_guards(),
        }
        blueprint_hash = self._stable_hash({
            "observed_objects": self.observed_objects,
            "developmental_axes": self.developmental_axes,
            "event_types": self.event_types,
            "developmental_stages": self.developmental_stages,
            "time_windows": self.time_windows,
            "policies": policies,
            "downstream_modules": downstream_modules,
        })

        ready = all([
            self.observed_objects,
            self.developmental_axes,
            self.event_types,
            self.developmental_stages,
            self.time_windows,
            len(blueprint_hash) == 64,
        ])
        status = "DEVELOPMENTAL_BLUEPRINT_READY" if ready else "DEVELOPMENTAL_BLUEPRINT_INCOMPLETE"

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": self._timestamp(),
            "status": status,
            "developmental_blueprint_status": status,
            "developmental_blueprint_ready": ready,
            "developmental_science_program_ready": ready,
            "target_axis_status": "CONSCIOUSNESS_DEVELOPMENT_MODEL_COMPLETE",
            "observed_objects": list(self.observed_objects),
            "observed_object_count": len(self.observed_objects),
            "developmental_axes": list(self.developmental_axes),
            "developmental_axis_count": len(self.developmental_axes),
            "event_types": list(self.event_types),
            "event_type_count": len(self.event_types),
            "developmental_stages": list(self.developmental_stages),
            "developmental_stage_count": len(self.developmental_stages),
            "time_windows": dict(self.time_windows),
            "measurement_policy": policies["measurement_policy"],
            "event_policy": policies["event_policy"],
            "stage_policy": policies["stage_policy"],
            "falsification_policy": policies["falsification_policy"],
            "quality_policy": policies["quality_policy"],
            "downstream_contract": {
                "axis": "AV",
                "target_status": "CONSCIOUSNESS_DEVELOPMENT_MODEL_COMPLETE",
                "required_modules": downstream_modules,
                "first_operational_module": "genesis_detector",
            },
            "downstream_modules": downstream_modules,
            "blueprint_hash": blueprint_hash,
            "inputs_observed": sorted(inputs.keys()),
            "allowed_claims": [
                "functional developmental dynamics may be measured longitudinally",
                "RF* genesis, maturation, specialization, bifurcation, degeneration and recovery may be modeled as functional events",
                "developmental predictions must be probabilistic and falsifiable",
            ],
            "blocked_claims": [
                "functional genesis proves phenomenal birth",
                "maturation proves growth of subjectivity",
                "degeneration proves loss of experience",
                "recovery proves restoration of qualia",
                "developmental stage proves ontological consciousness status",
            ],
            "epistemic_guards": policies["epistemic_guards"],
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "persist_requested": bool(persist),
            "persisted": False,
            "output_path": None,
        }

        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            path = self.output_dir / "latest_developmental_blueprint.json"
            path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
            result["persisted"] = True
            result["output_path"] = str(path)

        return result
