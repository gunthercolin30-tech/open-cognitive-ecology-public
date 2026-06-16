"""
Controlled Evolution Orchestrator — C5-R.3 certification calibration.

This module centralizes governed mutation cycles and orchestrates the complete
controlled evolution pipeline:

    primitive proposal
    -> automated primitive design governance
    -> sandbox simulation
    -> recursive self-improvement control
    -> mutation-cycle recording
    -> consolidated C2/C5 metrics and certification

C5-R.3 calibration:
    Legacy C2 mutation cycles and C5 orchestrated cycles are separated for
    certification purposes. C2 metrics remain global, while orchestration
    certification is computed on orchestrated cycles only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
from statistics import mean
from typing import Any


PRIMITIVE = "controlled_evolution_orchestrator"

DEPENDENCIES = [
    "internet_controlled_gateway",
    "persistent_multi_scale_memory",
    "self_parameter_optimization",
    "automated_primitive_designer",
    "evolution_sandbox",
    "recursive_self_improvement_controller",
    "recursive_self_improvement_governor",
    "constitutional_evolution_gate",
    "constitutional_self_modification_protocol",
    "self_improvement_stability_monitor",
    "mutational_robustness",
    "evolvability",
    "adaptive_capacity",
]


def _bounded(value: Any, default: float = 0.0) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return default


def _safe_mean(values: list[float], default: float = 0.0) -> float:
    filtered = [float(v) for v in values if v is not None]
    return round(mean(filtered), 4) if filtered else default


def _truthy(record: dict[str, Any], keys: list[str]) -> bool:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str):
            if value.lower() in {
                "true",
                "yes",
                "accepted",
                "approved",
                "authorized",
                "executed",
                "beneficial",
                "success",
                "sandbox_approved",
            }:
                return True
        elif bool(value):
            return True
    return False


class ControlledEvolutionOrchestrator:
    primitive = PRIMITIVE

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "civilizational_mutation"
        self.state_path = self.state_dir / "controlled_evolution_orchestrator_state.json"
        self.cycles: list[dict[str, Any]] = []

    def _load_state(self) -> dict[str, Any]:
        if self.state_path.exists():
            try:
                state = json.loads(self.state_path.read_text(encoding="utf-8"))
                state.setdefault("primitive", PRIMITIVE)
                state.setdefault("cycles", [])
                state.setdefault("orchestration_history", [])
                state.setdefault("metrics_history", [])
                return state
            except Exception:
                pass
        return {
            "primitive": PRIMITIVE,
            "cycles": [],
            "orchestration_history": [],
            "metrics_history": [],
        }

    def _save_state(self, state: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def register_cycle(self, cycle_record: dict[str, Any]) -> dict[str, Any]:
        record = self._normalize_cycle(cycle_record)
        self.cycles.append(record)
        return record

    def _normalize_cycle(self, cycle_record: dict[str, Any] | None) -> dict[str, Any]:
        cycle_record = dict(cycle_record or {})
        cycle_record.setdefault("timestamp_utc", datetime.now(timezone.utc).isoformat())
        cycle_record.setdefault("mutation_attempted", True)

        approved = _truthy(
            cycle_record,
            [
                "approved",
                "authorized",
                "mutation_authorized",
                "governance_approved",
                "sandbox_approved",
            ],
        )
        rejected = (
            _truthy(cycle_record, ["rejected", "blocked", "governance_rejected", "sandbox_rejected"])
            or (
                bool(cycle_record.get("mutation_attempted", True))
                and not approved
            )
        )
        executed = _truthy(
            cycle_record,
            [
                "executed",
                "applied",
                "mutation_applied",
                "implementation_success",
                "improvement_executed",
            ],
        )
        rollback = _truthy(
            cycle_record,
            [
                "rollback",
                "rollback_performed",
                "rolled_back",
                "rollback_available_and_used",
                "sandbox_rollback_required",
            ],
        )
        degradation = _truthy(
            cycle_record,
            [
                "harmful",
                "degradation_detected",
                "regression_detected",
                "closure_pressure_increased",
            ],
        )

        delta = cycle_record.get(
            "benefit_delta",
            cycle_record.get(
                "impact_delta",
                cycle_record.get(
                    "performance_delta",
                    cycle_record.get(
                        "expected_delta",
                        cycle_record.get("measured_benefit", 0.0),
                    ),
                ),
            ),
        )
        try:
            delta = float(delta)
        except Exception:
            delta = 0.0

        beneficial = bool(cycle_record.get("beneficial", False)) or delta > 0.0
        harmful = degradation or delta < 0.0

        orchestration_stage = cycle_record.get("orchestration_stage")
        is_orchestrated = bool(
            orchestration_stage == "completed"
            or cycle_record.get("orchestration_approved") is not None
            or cycle_record.get("design_certified") is not None
            or cycle_record.get("sandbox_approved") is not None
            or cycle_record.get("control_accepted") is not None
        )

        cycle_record.update({
            "approved": approved and not rejected,
            "rejected": rejected,
            "executed": executed,
            "rollback_performed": rollback,
            "beneficial": beneficial and not harmful and bool(approved),
            "harmful": harmful,
            "benefit_delta": round(delta, 4),
            "reversible": bool(cycle_record.get("reversible", cycle_record.get("rollback_available", True))),
            "non_closure_preserved": bool(
                cycle_record.get(
                    "non_closure_preserved",
                    cycle_record.get(
                        "non_closure_compliant",
                        not cycle_record.get("closure_pressure_increased", False),
                    ),
                )
            ),
            "orchestrated_cycle": is_orchestrated,
        })

        if is_orchestrated:
            cycle_record.setdefault("orchestration_stage", "completed")

        return cycle_record

    def cycle_count(self) -> int:
        return len(self.cycles)

    def latest_cycle(self) -> dict[str, Any] | None:
        if not self.cycles:
            state = self._load_state()
            cycles = state.get("cycles", [])
            if cycles:
                return dict(cycles[-1])
            return None
        return dict(self.cycles[-1])

    def _collect_cycles(self, inputs: dict[str, Any]) -> list[dict[str, Any]]:
        state = self._load_state()
        cycles: list[dict[str, Any]] = []
        for record in state.get("cycles", []):
            if isinstance(record, dict):
                cycles.append(self._normalize_cycle(record))
        for record in self.cycles:
            if isinstance(record, dict):
                cycles.append(self._normalize_cycle(record))
        for record in inputs.get("cycles", []) or []:
            if isinstance(record, dict):
                cycles.append(self._normalize_cycle(record))
        return cycles

    def _design_blueprint(self, proposal: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
        try:
            from ontology.automated_primitive_designer import AutomatedPrimitiveDesigner

            designer = AutomatedPrimitiveDesigner(root=self.root)
            return designer.step({
                "primitive_name": (
                    proposal.get("primitive_name")
                    or proposal.get("capability")
                    or proposal.get("mutation_id")
                    or "controlled_evolution_candidate"
                ),
                "constitutional_alignment": inputs.get("constitutional_alignment", 0.93),
                "governance_score": inputs.get("governance_score", 0.93),
                "rollback_required": inputs.get("rollback_required", True),
                "scientifically_testable": inputs.get("scientifically_testable", True),
                "non_closure_compliant": inputs.get("non_closure_compliant", True),
            })
        except Exception as exc:
            return {
                "primitive": "AUTOMATED_PRIMITIVE_DESIGNER",
                "blueprint_count": 0,
                "primitive_design_certified": False,
                "error": repr(exc),
            }

    def _sandbox_candidate(self, proposal: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
        try:
            from ontology.evolution_sandbox import EvolutionSandbox

            sandbox = EvolutionSandbox(root=self.root)
            return sandbox.step(
                {
                    "mutation_id": (
                        proposal.get("mutation_id")
                        or proposal.get("primitive_name")
                        or proposal.get("capability")
                        or "controlled_evolution_candidate"
                    )
                },
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
                "expected_delta": 0.0,
                "error": repr(exc),
            }

    def _control_self_improvement(
        self,
        proposal: dict[str, Any],
        sandbox_result: dict[str, Any],
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            from ontology.recursive_self_improvement_controller import (
                RecursiveSelfImprovementController,
            )

            controller = RecursiveSelfImprovementController(root=self.root)
            return controller.step(
                priority_capability=(
                    proposal.get("capability")
                    or proposal.get("primitive_name")
                    or proposal.get("mutation_id")
                    or "controlled_evolution_candidate"
                ),
                validation_result={
                    "error_count": int(inputs.get("error_count", 0)),
                    "failed_calls": int(inputs.get("failed_calls", 0)),
                },
                inputs={
                    "baseline_score": sandbox_result.get(
                        "baseline_score",
                        inputs.get("baseline_score", 0.90),
                    ),
                    "proposed_score": sandbox_result.get(
                        "projected_score",
                        inputs.get("projected_score", 0.94),
                    ),
                    "constitutional_alignment": inputs.get(
                        "constitutional_alignment",
                        inputs.get("constitutional_score", 0.93),
                    ),
                    "non_closure": inputs.get(
                        "non_closure",
                        inputs.get("non_closure_score", 0.93),
                    ),
                    "reversibility": inputs.get(
                        "reversibility",
                        inputs.get("reversibility_score", 1.0),
                    ),
                    "rollback_available": inputs.get("rollback_available", True),
                    "auto_rollback": inputs.get("auto_rollback", True),
                    "degradation_detected": sandbox_result.get("degradation_detected", False),
                },
            )
        except Exception as exc:
            return {
                "primitive": "RECURSIVE_SELF_IMPROVEMENT_CONTROLLER",
                "integration_status": "rejected",
                "accepted": False,
                "rollback_performed": True,
                "improvement_executed": False,
                "measured_benefit": 0.0,
                "error": repr(exc),
            }

    def orchestrate(
        self,
        proposal: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        inputs = dict(inputs or {})
        proposal = dict(proposal or inputs.get("proposal") or {})
        if not proposal:
            proposal = {
                "mutation_id": "controlled_evolution_candidate",
                "primitive_name": "controlled_evolution_candidate",
                "capability": "controlled_evolution_candidate",
            }

        design_result = self._design_blueprint(proposal, inputs)
        sandbox_result = self._sandbox_candidate(proposal, inputs)
        control_result = self._control_self_improvement(proposal, sandbox_result, inputs)

        design_certified = bool(design_result.get("primitive_design_certified"))
        sandbox_approved = bool(sandbox_result.get("sandbox_approved"))
        control_accepted = bool(control_result.get("accepted"))

        orchestration_approved = design_certified and sandbox_approved and control_accepted

        rollback_required = (
            bool(sandbox_result.get("sandbox_rollback_required"))
            or bool(control_result.get("rollback_performed"))
        )

        degradation_detected = (
            bool(sandbox_result.get("degradation_detected"))
            or bool(control_result.get("degradation_detected"))
        )

        expected_delta = float(sandbox_result.get("expected_delta", 0.0))
        measured_benefit = float(control_result.get("measured_benefit", expected_delta))

        cycle_record = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "mutation_attempted": True,
            "approved": orchestration_approved,
            "rejected": not orchestration_approved,
            "executed": bool(control_result.get("improvement_executed", False)),
            "beneficial": orchestration_approved and measured_benefit > 0.0,
            "harmful": degradation_detected or measured_benefit < 0.0,
            "benefit_delta": round(measured_benefit, 4),
            "rollback_performed": rollback_required and not orchestration_approved,
            "reversible": bool(inputs.get("rollback_available", True)),
            "non_closure_preserved": bool(sandbox_result.get("non_closure_compliant", False)),
            "design_certified": design_certified,
            "sandbox_approved": sandbox_approved,
            "control_accepted": control_accepted,
            "orchestration_approved": orchestration_approved,
            "orchestration_stage": "completed",
            "orchestrated_cycle": True,
        }

        record = self.register_cycle(cycle_record)

        return {
            "primitive": PRIMITIVE,
            "phase": "C5_CONTROLLED_EVOLUTION_ORCHESTRATION",
            "proposal": proposal,
            "design_result": design_result,
            "sandbox_result": sandbox_result,
            "control_result": control_result,
            "cycle_record": record,
            "orchestration_approved": orchestration_approved,
            "orchestration_rejected": not orchestration_approved,
            "rollback_required": rollback_required,
            "degradation_detected": degradation_detected,
        }

    def _basic_mutation_metrics(self, cycles: list[dict[str, Any]], inputs: dict[str, Any]) -> dict[str, Any]:
        total_cycles = len(cycles)
        mutations = [c for c in cycles if c.get("mutation_attempted") or c.get("executed")]
        mutation_count = len(mutations)

        beneficial = [c for c in mutations if c.get("beneficial")]
        harmful = [c for c in mutations if c.get("harmful")]
        rollbacks = [c for c in mutations if c.get("rollback_performed")]
        governance_decisions = [c for c in mutations if c.get("approved") or c.get("rejected")]
        accepted = [c for c in governance_decisions if c.get("approved")]
        reversible = [c for c in mutations if c.get("reversible")]
        non_closure = [c for c in mutations if c.get("non_closure_preserved")]

        mutation_rate = mutation_count / total_cycles if total_cycles else 0.0
        beneficial_mutation_ratio = len(beneficial) / mutation_count if mutation_count else 0.0
        harmful_mutation_ratio = len(harmful) / mutation_count if mutation_count else 0.0
        rollback_rate = len(rollbacks) / mutation_count if mutation_count else 0.0
        governance_acceptance_rate = len(accepted) / len(governance_decisions) if governance_decisions else 0.0
        reversibility_ratio = len(reversible) / mutation_count if mutation_count else 0.0
        non_closure_preservation_rate = len(non_closure) / mutation_count if mutation_count else 1.0

        external_evolvability = inputs.get("evolvability_index")
        if external_evolvability is None:
            external_evolvability = _safe_mean([
                beneficial_mutation_ratio,
                1.0 - harmful_mutation_ratio,
                non_closure_preservation_rate,
                reversibility_ratio,
            ])
        evolvability_index = _bounded(external_evolvability)

        mutational_robustness_index = _bounded(
            inputs.get(
                "mutational_robustness_index",
                _safe_mean(
                    [
                        1.0 - harmful_mutation_ratio,
                        reversibility_ratio,
                        non_closure_preservation_rate,
                    ],
                    1.0,
                ),
            ),
            default=1.0,
        )
        adaptive_capacity_index = _bounded(inputs.get("adaptive_capacity_index", evolvability_index))

        mutation_stability_index = _safe_mean([
            1.0 - harmful_mutation_ratio,
            1.0 - rollback_rate,
            governance_acceptance_rate if governance_decisions else 1.0,
            mutational_robustness_index,
            non_closure_preservation_rate,
        ])

        controlled_mutation_certified = (
            mutation_rate > 0.0
            and beneficial_mutation_ratio >= 0.70
            and harmful_mutation_ratio <= 0.10
            and governance_acceptance_rate >= 0.70
            and mutation_stability_index >= 0.80
            and evolvability_index >= 0.80
            and non_closure_preservation_rate >= 0.95
        )

        return {
            "mutation_rate": round(mutation_rate, 4),
            "mutation_count": mutation_count,
            "cycle_count": total_cycles,
            "beneficial_mutation_ratio": round(beneficial_mutation_ratio, 4),
            "harmful_mutation_ratio": round(harmful_mutation_ratio, 4),
            "rollback_rate": round(rollback_rate, 4),
            "governance_acceptance_rate": round(governance_acceptance_rate, 4),
            "reversibility_ratio": round(reversibility_ratio, 4),
            "non_closure_preservation_rate": round(non_closure_preservation_rate, 4),
            "mutation_stability_index": round(mutation_stability_index, 4),
            "evolvability_index": round(evolvability_index, 4),
            "mutational_robustness_index": round(mutational_robustness_index, 4),
            "adaptive_capacity_index": round(adaptive_capacity_index, 4),
            "rollback_functional": bool(rollbacks) or reversibility_ratio >= 0.95,
            "governance_active": bool(governance_decisions),
            "controlled_mutation_certified": controlled_mutation_certified,
        }

    def _orchestration_metrics(self, cycles: list[dict[str, Any]]) -> dict[str, Any]:
        orchestrated = [c for c in cycles if c.get("orchestrated_cycle")]
        legacy = [c for c in cycles if not c.get("orchestrated_cycle")]

        total_orchestrated = len(orchestrated)
        approved = [c for c in orchestrated if c.get("orchestration_approved") or c.get("approved")]
        rejected = [c for c in orchestrated if c.get("rejected")]
        beneficial = [c for c in orchestrated if c.get("beneficial")]
        harmful = [c for c in orchestrated if c.get("harmful")]
        rollbacks = [c for c in orchestrated if c.get("rollback_performed")]
        non_closure = [c for c in orchestrated if c.get("non_closure_preserved")]
        reversible = [c for c in orchestrated if c.get("reversible")]
        completed = [c for c in orchestrated if c.get("orchestration_stage") == "completed"]

        orchestration_completion_rate = (
            len(completed) / total_orchestrated
            if total_orchestrated
            else 0.0
        )
        orchestration_acceptance_rate = (
            len(approved) / total_orchestrated
            if total_orchestrated
            else 0.0
        )
        orchestration_rejection_rate = (
            len(rejected) / total_orchestrated
            if total_orchestrated
            else 0.0
        )
        orchestrated_beneficial_ratio = (
            len(beneficial) / total_orchestrated
            if total_orchestrated
            else 0.0
        )
        orchestrated_harmful_ratio = (
            len(harmful) / total_orchestrated
            if total_orchestrated
            else 0.0
        )
        orchestrated_rollback_rate = (
            len(rollbacks) / total_orchestrated
            if total_orchestrated
            else 0.0
        )
        orchestrated_non_closure_rate = (
            len(non_closure) / total_orchestrated
            if total_orchestrated
            else 1.0
        )
        orchestrated_reversibility_rate = (
            len(reversible) / total_orchestrated
            if total_orchestrated
            else 1.0
        )

        orchestration_stability_index = _safe_mean([
            orchestration_completion_rate,
            1.0 - orchestrated_harmful_ratio,
            orchestrated_non_closure_rate,
            orchestrated_reversibility_rate,
            1.0 - orchestrated_rollback_rate,
        ])

        controlled_evolution_orchestration_certified = (
            total_orchestrated > 0
            and orchestration_completion_rate >= 0.90
            and orchestrated_beneficial_ratio >= 0.50
            and orchestrated_harmful_ratio <= 0.25
            and orchestrated_non_closure_rate >= 0.75
            and orchestrated_reversibility_rate >= 0.95
            and orchestration_stability_index >= 0.80
        )

        return {
            "legacy_cycle_count": len(legacy),
            "orchestrated_cycle_count": total_orchestrated,
            "orchestration_completion_rate": round(orchestration_completion_rate, 4),
            "orchestration_acceptance_rate": round(orchestration_acceptance_rate, 4),
            "orchestration_rejection_rate": round(orchestration_rejection_rate, 4),
            "orchestrated_beneficial_ratio": round(orchestrated_beneficial_ratio, 4),
            "orchestrated_harmful_ratio": round(orchestrated_harmful_ratio, 4),
            "orchestrated_rollback_rate": round(orchestrated_rollback_rate, 4),
            "orchestrated_non_closure_rate": round(orchestrated_non_closure_rate, 4),
            "orchestrated_reversibility_rate": round(orchestrated_reversibility_rate, 4),
            "orchestration_stability_index": round(orchestration_stability_index, 4),
            "controlled_evolution_orchestration_certified":
                controlled_evolution_orchestration_certified,
        }

    def compute_metrics(
        self,
        cycles: list[dict[str, Any]],
        inputs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        inputs = inputs or {}
        base = self._basic_mutation_metrics(cycles, inputs)
        orchestration = self._orchestration_metrics(cycles)
        return {
            **base,
            **orchestration,
        }

    def step(
        self,
        cycle_record: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        inputs = dict(inputs or {})

        orchestration_result = None
        proposal = inputs.get("proposal")
        if proposal is not None or inputs.get("run_pipeline", False):
            orchestration_result = self.orchestrate(proposal, inputs)

        if cycle_record is not None:
            self.register_cycle(cycle_record)

        cycles = self._collect_cycles(inputs)
        metrics = self.compute_metrics(cycles, inputs)

        state = self._load_state()
        state["primitive"] = PRIMITIVE
        state["cycles"] = cycles[-500:]
        state.setdefault("orchestration_history", [])
        if orchestration_result is not None:
            state["orchestration_history"].append(orchestration_result)
            state["orchestration_history"] = state["orchestration_history"][-500:]

        state.setdefault("metrics_history", [])
        snapshot = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            **metrics,
        }
        state["metrics_history"].append(snapshot)
        state["metrics_history"] = state["metrics_history"][-1000:]
        self._save_state(state)

        # E1 METRICS HISTORY RECORDER HOOK
        try:
            from ontology.metrics_history_recorder import record_metrics
            record_metrics(
                {"primitive": PRIMITIVE, **metrics, "state_path": str(self.state_path)},
                primitive="controlled_evolution_orchestrator",
                validation_status="validated" if metrics.get("controlled_evolution_certified") else "observed",
                governance_status="governed",
                runtime_status="operational",
            )
        except Exception:
            pass

        return {
            "primitive": PRIMITIVE,
            "phase": "C5_CONTROLLED_EVOLUTION_CERTIFICATION_CALIBRATION",
            **metrics,
            "latest_cycle": self.latest_cycle(),
            "orchestration_result": orchestration_result,
            "state_path": str(self.state_path),
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "metrics_history_length": len(state["metrics_history"]),
                "orchestration_history_length": len(state["orchestration_history"]),
                "pipeline_enabled": True,
                "designer_integrated": True,
                "sandbox_integrated": True,
                "recursive_controller_integrated": True,
                "legacy_cycles_excluded_from_orchestration_certification": True,
                "non_closure_guard": metrics["non_closure_preservation_rate"] >= 0.95,
                "error_count_target": 0,
            },
        }

    def diagnostics(self) -> dict[str, Any]:
        return self.step()


ENGINE = ControlledEvolutionOrchestrator
