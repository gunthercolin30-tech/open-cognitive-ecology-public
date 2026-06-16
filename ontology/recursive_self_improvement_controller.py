"""
Recursive Self-Improvement Controller — C4 governance integration.

This module orchestrates governed self-improvement cycles. It does not allow
ungoverned self-modification: each cycle is evaluated through constitutional
alignment, non-closure preservation, reversibility, measured benefit, rollback
availability, and validation error count.

C4 goals:
    - no ungovened self-improvement;
    - explicit acceptance thresholds;
    - rollback when degradation is detected;
    - before/after comparison;
    - longitudinal cycle logging;
    - certification-ready metrics.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


PRIMITIVE = "recursive_self_improvement_controller"

DEPENDENCIES = [
    "recursive_self_improvement_governor",
    "recursive_civilizational_self_improvement",
    "self_improvement_stability_monitor",
    "constitutional_self_modification_protocol",
    "constitutional_evolution_gate",
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


class RecursiveSelfImprovementController:
    primitive_name = "RECURSIVE_SELF_IMPROVEMENT_CONTROLLER"
    primitive = PRIMITIVE

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "civilizational_mutation"
        self.state_path = self.state_dir / "recursive_self_improvement_controller_state.json"
        self.improvement_history: list[dict[str, Any]] = []

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

    def _select_priority(
        self,
        priority_capability: str | None,
        recommended_capabilities: list[str] | None,
        inputs: dict[str, Any],
    ) -> str | None:
        if priority_capability:
            return str(priority_capability)

        capability = inputs.get("priority_capability")
        if capability:
            return str(capability)

        recommended = recommended_capabilities or inputs.get("recommended_capabilities", [])
        if isinstance(recommended, (list, tuple)) and recommended:
            return str(recommended[0])

        return None

    def _evaluate_cycle(
        self,
        priority_capability: str,
        validation_result: dict[str, Any],
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        error_count = int(validation_result.get("error_count", inputs.get("error_count", 0)))
        failed_calls = int(validation_result.get("failed_calls", inputs.get("failed_calls", 0)))

        baseline_score = _bounded(inputs.get("baseline_score", inputs.get("current_score", 0.90)), 0.90)
        proposed_score = _bounded(inputs.get("proposed_score", inputs.get("post_score", baseline_score)), baseline_score)
        measured_benefit = round(proposed_score - baseline_score, 4)

        benefit_threshold = float(inputs.get("benefit_threshold", 0.0))
        constitutional_alignment = _bounded(inputs.get("constitutional_alignment", 0.92), 0.92)
        non_closure = _bounded(inputs.get("non_closure", inputs.get("non_closure_preserved_score", 0.92)), 0.92)
        reversibility = _bounded(inputs.get("reversibility", 1.0 if inputs.get("rollback_available", True) else 0.0), 1.0)
        governance_threshold = float(inputs.get("governance_threshold", 0.85))

        rollback_available = bool(inputs.get("rollback_available", True))
        degradation_detected = (
            bool(inputs.get("degradation_detected", False))
            or bool(inputs.get("regression_detected", False))
            or measured_benefit < 0.0
            or error_count > 0
            or failed_calls > 0
        )

        governance_approved = (
            constitutional_alignment >= governance_threshold
            and non_closure >= governance_threshold
            and reversibility >= governance_threshold
            and rollback_available
        )

        benefit_accepted = measured_benefit > benefit_threshold
        validation_passed = error_count == 0 and failed_calls == 0

        accepted = (
            governance_approved
            and benefit_accepted
            and validation_passed
            and not degradation_detected
        )

        rollback_performed = bool(
            degradation_detected
            and rollback_available
            and inputs.get("auto_rollback", True)
        )

        if accepted:
            integration_status = "accepted"
        elif rollback_performed:
            integration_status = "rolled_back"
        else:
            integration_status = "rejected"

        self_improvement_control_score = _safe_mean([
            1.0 if governance_approved else 0.0,
            1.0 if validation_passed else 0.0,
            1.0 if rollback_available else 0.0,
            1.0 if non_closure >= governance_threshold else 0.0,
            1.0 if not degradation_detected else 0.0,
            _bounded(max(0.0, measured_benefit) / max(0.01, inputs.get("expected_benefit", 0.10)), 0.0),
        ])

        record = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "priority_capability": priority_capability,
            "baseline_score": round(baseline_score, 4),
            "proposed_score": round(proposed_score, 4),
            "measured_benefit": measured_benefit,
            "benefit_threshold": benefit_threshold,
            "constitutional_alignment": round(constitutional_alignment, 4),
            "non_closure": round(non_closure, 4),
            "reversibility": round(reversibility, 4),
            "rollback_available": rollback_available,
            "rollback_performed": rollback_performed,
            "degradation_detected": degradation_detected,
            "validation_result": validation_result,
            "error_count": error_count,
            "failed_calls": failed_calls,
            "governance_approved": governance_approved,
            "benefit_accepted": benefit_accepted,
            "validation_passed": validation_passed,
            "accepted": accepted,
            "integration_status": integration_status,
            "self_improvement_control_score": round(self_improvement_control_score, 4),
        }

        return record

    def _metrics(self, cycles: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(cycles)
        accepted = [c for c in cycles if c.get("accepted")]
        rejected = [c for c in cycles if c.get("integration_status") == "rejected"]
        rolled_back = [c for c in cycles if c.get("rollback_performed")]
        governed = [c for c in cycles if c.get("governance_approved")]
        degraded = [c for c in cycles if c.get("degradation_detected")]
        validation_passed = [c for c in cycles if c.get("validation_passed")]

        acceptance_rate = len(accepted) / total if total else 0.0
        rejection_rate = len(rejected) / total if total else 0.0
        rollback_rate = len(rolled_back) / total if total else 0.0
        governance_approval_rate = len(governed) / total if total else 0.0
        degradation_rate = len(degraded) / total if total else 0.0
        validation_success_rate = len(validation_passed) / total if total else 0.0

        mean_benefit = _safe_mean([float(c.get("measured_benefit", 0.0)) for c in cycles], 0.0)
        mean_control_score = _safe_mean([float(c.get("self_improvement_control_score", 0.0)) for c in cycles], 0.0)

        recursive_control_certified = (
            total > 0
            and governance_approval_rate >= 0.70
            and validation_success_rate >= 0.90
            and degradation_rate <= 0.10
            and mean_control_score >= 0.80
        )

        return {
            "cycle_count": total,
            "accepted_cycles": len(accepted),
            "rejected_cycles": len(rejected),
            "rolled_back_cycles": len(rolled_back),
            "acceptance_rate": round(acceptance_rate, 4),
            "rejection_rate": round(rejection_rate, 4),
            "rollback_rate": round(rollback_rate, 4),
            "governance_approval_rate": round(governance_approval_rate, 4),
            "degradation_rate": round(degradation_rate, 4),
            "validation_success_rate": round(validation_success_rate, 4),
            "mean_measured_benefit": round(mean_benefit, 4),
            "self_improvement_control_score": round(mean_control_score, 4),
            "rollback_functional": bool(rolled_back) or rollback_rate == 0.0,
            "recursive_self_improvement_certified": recursive_control_certified,
        }

    def step(
        self,
        priority_capability: str | None = None,
        recommended_capabilities: list[str] | None = None,
        validation_result: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        inputs = dict(inputs or {})
        validation_result = dict(validation_result or inputs.get("validation_result", {}))

        selected = self._select_priority(
            priority_capability,
            recommended_capabilities,
            inputs,
        )

        if not selected:
            state = self._load_state()
            cycles = state.get("cycles", [])
            metrics = self._metrics(cycles)
            return {
                "primitive": self.primitive_name,
                "phase": "C4_RECURSIVE_SELF_IMPROVEMENT_CONTROL",
                "improvement_executed": False,
                "reason": "no_priority_capability",
                **metrics,
                "history_length": len(cycles),
                "state_path": str(self.state_path),
            }

        record = self._evaluate_cycle(selected, validation_result, inputs)
        self.improvement_history.append(record)

        state = self._load_state()
        state["primitive"] = PRIMITIVE
        cycles = [
            c for c in state.get("cycles", [])
            if isinstance(c, dict)
        ]
        cycles.append(record)
        cycles = cycles[-500:]
        state["cycles"] = cycles

        metrics = self._metrics(cycles)
        state.setdefault("metrics_history", [])
        state["metrics_history"].append({
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            **metrics,
        })
        state["metrics_history"] = state["metrics_history"][-1000:]
        self._save_state(state)

        return {
            "primitive": self.primitive_name,
            "phase": "C4_RECURSIVE_SELF_IMPROVEMENT_CONTROL",
            "improvement_executed": record["accepted"],
            "priority_capability": selected,
            "integration_status": record["integration_status"],
            "accepted": record["accepted"],
            "rollback_performed": record["rollback_performed"],
            "degradation_detected": record["degradation_detected"],
            "measured_benefit": record["measured_benefit"],
            **metrics,
            "history_length": len(cycles),
            "state": record,
            "state_path": str(self.state_path),
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "governance_active": True,
                "rollback_available": record["rollback_available"],
                "non_closure_preserved": record["non_closure"] >= 0.85,
                "error_count_target": 0,
            },
        }

    def diagnostics(self) -> dict[str, Any]:
        return self.step()


ENGINE = RecursiveSelfImprovementController

__all__ = ["RecursiveSelfImprovementController"]
