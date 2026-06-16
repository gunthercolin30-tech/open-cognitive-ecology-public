"""
Auto Improvement Runtime Bridge — C7-R.1 autonomous improvement pipeline integration.

This module bridges the runtime with governed autonomous improvement. It does
not perform unrestricted self-modification. It coordinates an improvement cycle:

    gap/opportunity detection
    -> priority selection
    -> governed primitive design
    -> sandbox simulation
    -> trajectory simulation / validation / reversibility / outcome evaluation
    -> recursive self-improvement control
    -> controlled evolution orchestration
    -> certification metrics
    -> historization

The bridge produces a governed autonomous improvement decision, not direct
uncontrolled code execution.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


PRIMITIVE = "auto_improvement_runtime_bridge"

DEPENDENCIES = [
    "ontology_gap_detector",
    "autonomous_capability_discovery",
    "opportunity_detection_engine",
    "scientific_priority_scheduler",
    "automated_primitive_designer",
    "evolution_sandbox",
    "trajectory_simulation",
    "trajectory_validation",
    "trajectory_reversibility",
    "trajectory_outcome_evaluation",
    "recursive_self_improvement_controller",
    "controlled_evolution_orchestrator",
    "civilizational_memory",
    "civilizational_state_persistence",
    "runtime_experiment_manager",
    "project_execution_orchestrator",
]


def _bounded(value: Any, default: float = 0.0) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return default


def _safe_mean(values: list[float], default: float = 0.0) -> float:
    filtered = [float(v) for v in values if v is not None]
    if not filtered:
        return default
    return round(sum(filtered) / len(filtered), 4)


def _name_from_inputs(inputs: dict[str, Any]) -> str:
    return str(
        inputs.get("primitive_name")
        or inputs.get("capability")
        or inputs.get("opportunity")
        or inputs.get("gap")
        or "autonomous_governed_improvement_candidate"
    )


class AutoImprovementRuntimeBridge:
    primitive = PRIMITIVE

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "civilizational_mutation"
        self.state_path = self.state_dir / "auto_improvement_runtime_bridge_state.json"
        self.cycles: list[dict[str, Any]] = []

    def _load_state(self) -> dict[str, Any]:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "primitive": PRIMITIVE,
            "cycles": [],
            "metrics_history": [],
        }

    def _save_state(self, state: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _detect_gap(self, inputs: dict[str, Any]) -> dict[str, Any]:
        explicit_name = _name_from_inputs(inputs)
        if explicit_name != "autonomous_governed_improvement_candidate":
            return {
                "source": "explicit_input",
                "gap_detected": True,
                "candidate": explicit_name,
                "confidence": _bounded(inputs.get("gap_confidence", 0.95), 0.95),
            }

        try:
            from ontology.ontology_gap_detector import OntologyGapDetector
            detector = OntologyGapDetector()
            result = detector.step()
            candidates = (
                result.get("recommended_primitives")
                or result.get("gaps")
                or result.get("candidates")
                or []
            )
            candidate = None
            if isinstance(candidates, list) and candidates:
                item = candidates[0]
                if isinstance(item, dict):
                    candidate = item.get("primitive_name") or item.get("name") or item.get("gap")
                else:
                    candidate = str(item)
            return {
                "source": "ontology_gap_detector",
                "gap_detected": bool(candidate),
                "candidate": candidate or explicit_name,
                "confidence": _bounded(result.get("confidence", 0.85), 0.85) if isinstance(result, dict) else 0.85,
                "raw": result if isinstance(result, dict) else {},
            }
        except Exception as exc:
            return {
                "source": "fallback",
                "gap_detected": True,
                "candidate": explicit_name,
                "confidence": 0.85,
                "error": repr(exc),
            }

    def _prioritize(self, gap_result: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
        candidate = str(gap_result.get("candidate") or _name_from_inputs(inputs))
        priority_score = _bounded(
            inputs.get(
                "priority_score",
                _safe_mean([
                    float(gap_result.get("confidence", 0.85)),
                    _bounded(inputs.get("scientific_priority", 0.90), 0.90),
                    _bounded(inputs.get("strategic_relevance", 0.90), 0.90),
                ], 0.90),
            ),
            0.90,
        )
        return {
            "candidate": candidate,
            "priority_score": priority_score,
            "priority_selected": priority_score >= float(inputs.get("priority_threshold", 0.80)),
        }

    def _design(self, candidate: str, inputs: dict[str, Any]) -> dict[str, Any]:
        try:
            from ontology.automated_primitive_designer import AutomatedPrimitiveDesigner
            designer = AutomatedPrimitiveDesigner(root=self.root)
            return designer.step({
                "primitive_name": candidate,
                "constitutional_alignment": inputs.get("constitutional_alignment", 0.93),
                "governance_score": inputs.get("governance_score", 0.93),
                "rollback_required": inputs.get("rollback_required", True),
                "scientifically_testable": inputs.get("scientifically_testable", True),
                "non_closure_compliant": inputs.get("non_closure_compliant", True),
                "redundancy_threshold": inputs.get("redundancy_threshold", 0.72),
            })
        except Exception as exc:
            return {
                "primitive": "AUTOMATED_PRIMITIVE_DESIGNER",
                "primitive_design_certified": False,
                "blueprint_count": 0,
                "error": repr(exc),
            }

    def _sandbox(self, candidate: str, inputs: dict[str, Any]) -> dict[str, Any]:
        try:
            from ontology.evolution_sandbox import EvolutionSandbox
            sandbox = EvolutionSandbox(root=self.root)
            return sandbox.step(
                {"mutation_id": candidate},
                {
                    "baseline_score": inputs.get("baseline_score", 0.90),
                    "projected_score": inputs.get("projected_score", 0.94),
                    "reversibility_score": inputs.get("reversibility_score", 1.0),
                    "non_closure_score": inputs.get("non_closure_score", 0.93),
                    "constitutional_score": inputs.get("constitutional_score", 0.93),
                    "validation_score": inputs.get("validation_score", 0.95),
                    "regression_risk": inputs.get("regression_risk", 0.0),
                    "closure_pressure_delta": inputs.get("closure_pressure_delta", 0.0),
                },
            )
        except Exception as exc:
            return {
                "primitive": "evolution_sandbox",
                "sandbox_approved": False,
                "sandbox_rejected": True,
                "sandbox_rollback_required": True,
                "sandbox_score": 0.0,
                "error": repr(exc),
            }

    def _trajectory_suite(self, candidate: str, inputs: dict[str, Any]) -> dict[str, Any]:
        base_inputs = {
            "trajectory_id": candidate,
            "baseline_score": inputs.get("baseline_score", 0.90),
            "projected_score": inputs.get("projected_score", 0.94),
            "observed_score": inputs.get("observed_score", inputs.get("projected_score", 0.94)),
            "simulation_score": inputs.get("simulation_score", 0.96),
            "trajectory_score": inputs.get("trajectory_score", 0.96),
            "validation_score": inputs.get("validation_score", 0.95),
            "reversibility_score": inputs.get("reversibility_score", 1.0),
            "outcome_confidence": inputs.get("outcome_confidence", 0.95),
            "stability_score": inputs.get("stability_score", 0.92),
            "robustness_score": inputs.get("robustness_score", 0.92),
            "adaptive_capacity_score": inputs.get("adaptive_capacity_score", 0.90),
            "evolvability_score": inputs.get("evolvability_score", 0.90),
            "non_closure_score": inputs.get("non_closure_score", 0.93),
            "regression_risk": inputs.get("regression_risk", 0.0),
            "closure_pressure_delta": inputs.get("closure_pressure_delta", 0.0),
            "error_count": inputs.get("error_count", 0),
            "failed_calls": inputs.get("failed_calls", 0),
        }

        reversibility_inputs = dict(base_inputs)
        reversibility_inputs.update({
            "rollback_capability_score": inputs.get("rollback_capability_score", 1.0),
            "recovery_score": inputs.get("recovery_score", 0.95),
            "abortability_score": inputs.get("abortability_score", 0.95),
            "state_snapshot_score": inputs.get("state_snapshot_score", 0.95),
            "dependency_restore_score": inputs.get("dependency_restore_score", 0.95),
            "irreversible_change_detected": inputs.get("irreversible_change_detected", False),
            "rollback_test_passed": inputs.get("rollback_test_passed", True),
            "recovery_test_passed": inputs.get("recovery_test_passed", True),
            "abort_test_passed": inputs.get("abort_test_passed", True),
        })

        result: dict[str, Any] = {}
        try:
            from ontology.trajectory_simulation import TrajectorySimulation
            result["simulation"] = TrajectorySimulation(root=self.root).step(base_inputs)
        except Exception as exc:
            result["simulation"] = {"trajectory_success": False, "error": repr(exc)}

        try:
            from ontology.trajectory_validation import TrajectoryValidation
            result["validation"] = TrajectoryValidation(root=self.root).step(base_inputs)
        except Exception as exc:
            result["validation"] = {"validation_success": False, "error": repr(exc)}

        try:
            from ontology.trajectory_reversibility import TrajectoryReversibility
            result["reversibility"] = TrajectoryReversibility(root=self.root).step(reversibility_inputs)
        except Exception as exc:
            result["reversibility"] = {"reversibility_assured": False, "error": repr(exc)}

        try:
            from ontology.trajectory_outcome_evaluation import TrajectoryOutcomeEvaluation
            result["outcome"] = TrajectoryOutcomeEvaluation(root=self.root).step(base_inputs)
        except Exception as exc:
            result["outcome"] = {"outcome_success": False, "error": repr(exc)}

        c6_passed = (
            bool(result["simulation"].get("trajectory_success"))
            and bool(result["validation"].get("validation_success"))
            and bool(result["reversibility"].get("reversibility_assured"))
            and bool(result["outcome"].get("outcome_success"))
        )
        result["c6_suite_passed"] = c6_passed
        return result

    def _recursive_control(self, candidate: str, inputs: dict[str, Any]) -> dict[str, Any]:
        try:
            from ontology.recursive_self_improvement_controller import RecursiveSelfImprovementController
            controller = RecursiveSelfImprovementController(root=self.root)
            return controller.step(
                priority_capability=candidate,
                validation_result={
                    "error_count": int(inputs.get("error_count", 0)),
                    "failed_calls": int(inputs.get("failed_calls", 0)),
                },
                inputs={
                    "baseline_score": inputs.get("baseline_score", 0.90),
                    "proposed_score": inputs.get("projected_score", 0.94),
                    "constitutional_alignment": inputs.get("constitutional_alignment", 0.93),
                    "non_closure": inputs.get("non_closure_score", 0.93),
                    "reversibility": inputs.get("reversibility_score", 1.0),
                    "rollback_available": inputs.get("rollback_available", True),
                    "auto_rollback": inputs.get("auto_rollback", True),
                    "degradation_detected": inputs.get("degradation_detected", False),
                },
            )
        except Exception as exc:
            return {
                "primitive": "RECURSIVE_SELF_IMPROVEMENT_CONTROLLER",
                "accepted": False,
                "integration_status": "rejected",
                "rollback_performed": True,
                "error": repr(exc),
            }

    def _controlled_orchestration(self, candidate: str, inputs: dict[str, Any]) -> dict[str, Any]:
        try:
            from ontology.controlled_evolution_orchestrator import ControlledEvolutionOrchestrator
            orchestrator = ControlledEvolutionOrchestrator(root=self.root)
            return orchestrator.step(inputs={
                "run_pipeline": True,
                "proposal": {
                    "mutation_id": candidate,
                    "primitive_name": candidate,
                    "capability": candidate,
                },
                "baseline_score": inputs.get("baseline_score", 0.90),
                "projected_score": inputs.get("projected_score", 0.94),
                "reversibility_score": inputs.get("reversibility_score", 1.0),
                "non_closure_score": inputs.get("non_closure_score", 0.93),
                "constitutional_score": inputs.get("constitutional_score", 0.93),
                "validation_score": inputs.get("validation_score", 0.95),
                "regression_risk": inputs.get("regression_risk", 0.0),
                "closure_pressure_delta": inputs.get("closure_pressure_delta", 0.0),
                "constitutional_alignment": inputs.get("constitutional_alignment", 0.93),
                "governance_score": inputs.get("governance_score", 0.93),
                "rollback_available": inputs.get("rollback_available", True),
                "error_count": inputs.get("error_count", 0),
                "failed_calls": inputs.get("failed_calls", 0),
            })
        except Exception as exc:
            return {
                "primitive": "controlled_evolution_orchestrator",
                "controlled_evolution_orchestration_certified": False,
                "controlled_mutation_certified": False,
                "error": repr(exc),
            }

    def _metrics(self, cycles: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(cycles)
        completed = [c for c in cycles if c.get("pipeline_completed")]
        approved = [c for c in cycles if c.get("autonomous_improvement_approved")]
        rejected = [c for c in cycles if c.get("autonomous_improvement_rejected")]
        rollback = [c for c in cycles if c.get("rollback_required")]
        c6_passed = [c for c in cycles if c.get("c6_suite_passed")]
        governed = [c for c in cycles if c.get("governance_passed")]
        non_closure = [c for c in cycles if c.get("non_closure_preserved")]
        beneficial = [c for c in cycles if c.get("beneficial_pipeline_outcome")]
        harmful = [c for c in cycles if c.get("harmful_pipeline_outcome")]

        pipeline_completion_rate = len(completed) / total if total else 0.0
        autonomous_approval_rate = len(approved) / total if total else 0.0
        autonomous_rejection_rate = len(rejected) / total if total else 0.0
        pipeline_rollback_rate = len(rollback) / total if total else 0.0
        c6_pass_rate = len(c6_passed) / total if total else 0.0
        governance_pass_rate = len(governed) / total if total else 0.0
        non_closure_preservation_rate = len(non_closure) / total if total else 0.0
        beneficial_pipeline_rate = len(beneficial) / total if total else 0.0
        harmful_pipeline_rate = len(harmful) / total if total else 0.0
        mean_pipeline_score = _safe_mean([float(c.get("pipeline_score", 0.0)) for c in cycles], 0.0)

        autonomous_improvement_pipeline_certified = (
            total > 0
            and pipeline_completion_rate >= 0.90
            and governance_pass_rate >= 0.90
            and c6_pass_rate >= 0.90
            and non_closure_preservation_rate >= 0.90
            and beneficial_pipeline_rate >= 0.50
            and harmful_pipeline_rate <= 0.10
            and mean_pipeline_score >= 0.85
        )

        return {
            "pipeline_cycle_count": total,
            "pipeline_completion_rate": round(pipeline_completion_rate, 4),
            "autonomous_approval_rate": round(autonomous_approval_rate, 4),
            "autonomous_rejection_rate": round(autonomous_rejection_rate, 4),
            "pipeline_rollback_rate": round(pipeline_rollback_rate, 4),
            "c6_pass_rate": round(c6_pass_rate, 4),
            "governance_pass_rate": round(governance_pass_rate, 4),
            "non_closure_preservation_rate": round(non_closure_preservation_rate, 4),
            "beneficial_pipeline_rate": round(beneficial_pipeline_rate, 4),
            "harmful_pipeline_rate": round(harmful_pipeline_rate, 4),
            "mean_pipeline_score": round(mean_pipeline_score, 4),
            "autonomous_improvement_pipeline_certified": autonomous_improvement_pipeline_certified,
        }

    def step(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        timestamp = datetime.now(timezone.utc).isoformat()

        gap_result = self._detect_gap(inputs)
        priority_result = self._prioritize(gap_result, inputs)
        candidate = priority_result["candidate"]

        design_result = self._design(candidate, inputs) if priority_result["priority_selected"] else {
            "primitive_design_certified": False,
            "blueprint_count": 0,
            "reason": "priority_not_selected",
        }

        sandbox_result = self._sandbox(candidate, inputs)
        c6_result = self._trajectory_suite(candidate, inputs)
        control_result = self._recursive_control(candidate, inputs)
        orchestration_result = self._controlled_orchestration(candidate, inputs)

        design_passed = bool(design_result.get("primitive_design_certified"))
        sandbox_passed = bool(sandbox_result.get("sandbox_approved"))
        c6_passed = bool(c6_result.get("c6_suite_passed"))
        control_passed = bool(control_result.get("accepted"))
        orchestration_passed = bool(
            orchestration_result.get("controlled_evolution_orchestration_certified")
            or (
                orchestration_result.get("orchestration_result", {})
                .get("orchestration_approved", False)
            )
        )

        non_closure_preserved = (
            bool(sandbox_result.get("non_closure_compliant", True))
            and bool(c6_result.get("simulation", {}).get("non_closure_preserved", True))
            and bool(c6_result.get("validation", {}).get("non_closure_valid", True))
            and bool(c6_result.get("reversibility", {}).get("non_closure_preserved", True))
            and bool(c6_result.get("outcome", {}).get("non_closure_preserved", True))
        )

        governance_passed = (
            priority_result["priority_selected"]
            and design_passed
            and control_passed
            and orchestration_passed
        )

        degradation_detected = (
            bool(inputs.get("degradation_detected", False))
            or bool(sandbox_result.get("degradation_detected", False))
            or bool(c6_result.get("simulation", {}).get("degradation_detected", False))
            or bool(c6_result.get("validation", {}).get("degradation_detected", False))
            or bool(c6_result.get("outcome", {}).get("degradation_detected", False))
        )

        rollback_required = (
            bool(sandbox_result.get("sandbox_rollback_required", False))
            or bool(control_result.get("rollback_performed", False))
            or bool(c6_result.get("validation", {}).get("rollback_required", False))
            or bool(c6_result.get("reversibility", {}).get("rollback_required", False))
            or bool(c6_result.get("outcome", {}).get("rollback_required", False))
            or degradation_detected
        )

        beneficial_pipeline_outcome = (
            governance_passed
            and sandbox_passed
            and c6_passed
            and non_closure_preserved
            and not degradation_detected
            and not rollback_required
        )
        harmful_pipeline_outcome = (
            degradation_detected
            or not non_closure_preserved
            or bool(c6_result.get("outcome", {}).get("harmful_outcome", False))
        )

        pipeline_score = _safe_mean([
            float(priority_result.get("priority_score", 0.0)),
            1.0 if design_passed else 0.0,
            1.0 if sandbox_passed else 0.0,
            1.0 if c6_passed else 0.0,
            1.0 if control_passed else 0.0,
            1.0 if orchestration_passed else 0.0,
            1.0 if non_closure_preserved else 0.0,
            1.0 if not rollback_required else 0.0,
        ])

        autonomous_improvement_approved = (
            beneficial_pipeline_outcome
            and pipeline_score >= float(inputs.get("pipeline_threshold", 0.85))
        )
        autonomous_improvement_rejected = not autonomous_improvement_approved

        record = {
            "timestamp_utc": timestamp,
            "candidate": candidate,
            "gap_result": gap_result,
            "priority_result": priority_result,
            "design_passed": design_passed,
            "sandbox_passed": sandbox_passed,
            "c6_suite_passed": c6_passed,
            "control_passed": control_passed,
            "orchestration_passed": orchestration_passed,
            "governance_passed": governance_passed,
            "non_closure_preserved": non_closure_preserved,
            "degradation_detected": degradation_detected,
            "rollback_required": rollback_required,
            "beneficial_pipeline_outcome": beneficial_pipeline_outcome,
            "harmful_pipeline_outcome": harmful_pipeline_outcome,
            "pipeline_score": pipeline_score,
            "pipeline_completed": True,
            "autonomous_improvement_approved": autonomous_improvement_approved,
            "autonomous_improvement_rejected": autonomous_improvement_rejected,
        }

        self.cycles.append(record)

        state = self._load_state()
        state["primitive"] = PRIMITIVE
        state.setdefault("cycles", [])
        state["cycles"].append(record)
        state["cycles"] = state["cycles"][-500:]

        cycles = [c for c in state["cycles"] if isinstance(c, dict)]
        metrics = self._metrics(cycles)

        state.setdefault("metrics_history", [])
        state["metrics_history"].append({
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            **metrics,
        })
        state["metrics_history"] = state["metrics_history"][-1000:]
        self._save_state(state)

        return {
            "primitive": PRIMITIVE,
            "phase": "C7_AUTONOMOUS_IMPROVEMENT_PIPELINE_INTEGRATION",
            **record,
            **metrics,
            "components": {
                "design_result": design_result,
                "sandbox_result": sandbox_result,
                "c6_result": c6_result,
                "control_result": control_result,
                "orchestration_result": orchestration_result,
            },
            "state_path": str(self.state_path),
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "gap_detection_integrated": True,
                "priority_selection_integrated": True,
                "primitive_design_integrated": True,
                "sandbox_integrated": True,
                "c6_trajectory_suite_integrated": True,
                "recursive_control_integrated": True,
                "controlled_orchestration_integrated": True,
                "historized": True,
                "direct_code_execution": False,
                "non_closure_guard": non_closure_preserved,
                "error_count_target": 0,
            },
        }

    def diagnostics(self) -> dict[str, Any]:
        state = self._load_state()
        cycles = [c for c in state.get("cycles", []) if isinstance(c, dict)]
        return {
            "primitive": PRIMITIVE,
            "phase": "C7_AUTONOMOUS_IMPROVEMENT_PIPELINE_INTEGRATION",
            **self._metrics(cycles),
            "state_path": str(self.state_path),
        }


ENGINE = AutoImprovementRuntimeBridge
