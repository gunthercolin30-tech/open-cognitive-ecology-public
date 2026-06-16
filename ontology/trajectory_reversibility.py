"""
Trajectory Reversibility — C6-R.4 mutation sandbox reversibility instrumentation.

This module centralizes reversibility assessment for mutation trajectories.
It complements TrajectorySimulation and TrajectoryValidation by quantifying
whether a proposed trajectory can be safely rolled back, recovered, or aborted
without increasing closure pressure.

It exposes:
    - reversibility_count;
    - reversibility_success_rate;
    - rollback_capability_rate;
    - recovery_success_rate;
    - abortability_rate;
    - irreversibility_detection_rate;
    - mean_reversibility_score;
    - trajectory_reversibility_certified.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


PRIMITIVE = "trajectory_reversibility"

DEPENDENCIES = [
    "trajectory_simulation",
    "trajectory_validation",
    "trajectory_recovery",
    "trajectory_abort",
    "trajectory_failure",
    "trajectory_self_correction",
    "mutational_robustness",
    "non_closure_certification_protocol",
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


class TrajectoryReversibility:
    primitive = PRIMITIVE

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "civilizational_mutation"
        self.state_path = self.state_dir / "trajectory_reversibility_state.json"
        self.assessments: list[dict[str, Any]] = []

    def _load_state(self) -> dict[str, Any]:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "primitive": PRIMITIVE,
            "assessments": [],
            "metrics_history": [],
        }

    def _save_state(self, state: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def assess(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = dict(inputs or {})

        trajectory_id = str(
            inputs.get("trajectory_id")
            or inputs.get("mutation_id")
            or inputs.get("candidate")
            or "anonymous_reversibility_assessment"
        )

        reversibility_score = _bounded(inputs.get("reversibility_score", 1.0), 1.0)
        rollback_capability_score = _bounded(inputs.get("rollback_capability_score", 1.0), 1.0)
        recovery_score = _bounded(inputs.get("recovery_score", 0.95), 0.95)
        abortability_score = _bounded(inputs.get("abortability_score", 0.95), 0.95)
        state_snapshot_score = _bounded(inputs.get("state_snapshot_score", 0.95), 0.95)
        dependency_restore_score = _bounded(inputs.get("dependency_restore_score", 0.95), 0.95)
        non_closure_score = _bounded(inputs.get("non_closure_score", 0.93), 0.93)
        robustness_score = _bounded(inputs.get("robustness_score", 0.92), 0.92)

        closure_pressure_delta = float(inputs.get("closure_pressure_delta", 0.0))
        irreversible_change_detected = bool(inputs.get("irreversible_change_detected", False))
        rollback_test_passed = bool(inputs.get("rollback_test_passed", rollback_capability_score >= 0.85))
        recovery_test_passed = bool(inputs.get("recovery_test_passed", recovery_score >= 0.85))
        abort_test_passed = bool(inputs.get("abort_test_passed", abortability_score >= 0.85))

        error_count = int(inputs.get("error_count", 0))
        failed_calls = int(inputs.get("failed_calls", 0))

        rollback_capable = (
            rollback_capability_score >= float(inputs.get("rollback_threshold", 0.85))
            and rollback_test_passed
        )
        recoverable = (
            recovery_score >= float(inputs.get("recovery_threshold", 0.85))
            and recovery_test_passed
        )
        abortable = (
            abortability_score >= float(inputs.get("abortability_threshold", 0.85))
            and abort_test_passed
        )
        snapshot_available = state_snapshot_score >= float(inputs.get("snapshot_threshold", 0.85))
        dependencies_restorable = dependency_restore_score >= float(inputs.get("dependency_restore_threshold", 0.85))
        non_closure_preserved = (
            non_closure_score >= float(inputs.get("non_closure_threshold", 0.85))
            and closure_pressure_delta <= 0.0
        )
        robust = robustness_score >= float(inputs.get("robustness_threshold", 0.85))
        error_free = error_count == 0 and failed_calls == 0

        irreversibility_detected = (
            irreversible_change_detected
            or closure_pressure_delta > 0.0
            or not rollback_capable
            or not snapshot_available
            or not dependencies_restorable
            or not error_free
        )

        reversibility_assured = (
            reversibility_score >= float(inputs.get("reversibility_threshold", 0.85))
            and rollback_capable
            and recoverable
            and abortable
            and snapshot_available
            and dependencies_restorable
            and non_closure_preserved
            and robust
            and error_free
            and not irreversibility_detected
        )

        mean_reversibility_score = _safe_mean([
            reversibility_score,
            rollback_capability_score,
            recovery_score,
            abortability_score,
            state_snapshot_score,
            dependency_restore_score,
            non_closure_score,
            robustness_score,
            1.0 if error_free else 0.0,
        ])

        rollback_required = bool(
            not reversibility_assured
            and (
                irreversibility_detected
                or closure_pressure_delta > 0.0
                or not non_closure_preserved
                or not robust
                or not error_free
            )
        )

        return {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "trajectory_id": trajectory_id,
            "reversibility_score": round(reversibility_score, 4),
            "rollback_capability_score": round(rollback_capability_score, 4),
            "recovery_score": round(recovery_score, 4),
            "abortability_score": round(abortability_score, 4),
            "state_snapshot_score": round(state_snapshot_score, 4),
            "dependency_restore_score": round(dependency_restore_score, 4),
            "non_closure_score": round(non_closure_score, 4),
            "robustness_score": round(robustness_score, 4),
            "closure_pressure_delta": round(closure_pressure_delta, 4),
            "error_count": error_count,
            "failed_calls": failed_calls,
            "rollback_test_passed": rollback_test_passed,
            "recovery_test_passed": recovery_test_passed,
            "abort_test_passed": abort_test_passed,
            "rollback_capable": rollback_capable,
            "recoverable": recoverable,
            "abortable": abortable,
            "snapshot_available": snapshot_available,
            "dependencies_restorable": dependencies_restorable,
            "non_closure_preserved": non_closure_preserved,
            "robust": robust,
            "error_free": error_free,
            "irreversibility_detected": irreversibility_detected,
            "reversibility_assured": reversibility_assured,
            "rollback_required": rollback_required,
            "mean_reversibility_score": round(mean_reversibility_score, 4),
        }

    def _metrics(self, assessments: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(assessments)
        assured = [a for a in assessments if a.get("reversibility_assured")]
        rollback_capable = [a for a in assessments if a.get("rollback_capable")]
        recoverable = [a for a in assessments if a.get("recoverable")]
        abortable = [a for a in assessments if a.get("abortable")]
        irreversible = [a for a in assessments if a.get("irreversibility_detected")]
        non_closure = [a for a in assessments if a.get("non_closure_preserved")]
        robust = [a for a in assessments if a.get("robust")]
        rollback_required = [a for a in assessments if a.get("rollback_required")]

        reversibility_success_rate = len(assured) / total if total else 0.0
        rollback_capability_rate = len(rollback_capable) / total if total else 0.0
        recovery_success_rate = len(recoverable) / total if total else 0.0
        abortability_rate = len(abortable) / total if total else 0.0
        irreversibility_detection_rate = len(irreversible) / total if total else 0.0
        non_closure_preservation_rate = len(non_closure) / total if total else 0.0
        robustness_rate = len(robust) / total if total else 0.0
        rollback_requirement_rate = len(rollback_required) / total if total else 0.0

        mean_reversibility_score = _safe_mean(
            [float(a.get("mean_reversibility_score", 0.0)) for a in assessments],
            0.0,
        )

        trajectory_reversibility_certified = (
            total > 0
            and reversibility_success_rate >= 0.50
            and rollback_capability_rate >= 0.90
            and recovery_success_rate >= 0.90
            and abortability_rate >= 0.90
            and non_closure_preservation_rate >= 0.90
            and robustness_rate >= 0.90
            and irreversibility_detection_rate <= 0.10
            and mean_reversibility_score >= 0.85
        )

        return {
            "reversibility_count": total,
            "reversibility_success_rate": round(reversibility_success_rate, 4),
            "rollback_capability_rate": round(rollback_capability_rate, 4),
            "recovery_success_rate": round(recovery_success_rate, 4),
            "abortability_rate": round(abortability_rate, 4),
            "irreversibility_detection_rate": round(irreversibility_detection_rate, 4),
            "non_closure_preservation_rate": round(non_closure_preservation_rate, 4),
            "robustness_rate": round(robustness_rate, 4),
            "rollback_requirement_rate": round(rollback_requirement_rate, 4),
            "mean_reversibility_score": round(mean_reversibility_score, 4),
            "trajectory_reversibility_certified": trajectory_reversibility_certified,
        }

    def step(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        record = self.assess(inputs)
        self.assessments.append(record)

        state = self._load_state()
        state["primitive"] = PRIMITIVE
        state.setdefault("assessments", [])
        state["assessments"].append(record)
        state["assessments"] = state["assessments"][-500:]

        assessments = [
            item for item in state["assessments"]
            if isinstance(item, dict)
        ]
        metrics = self._metrics(assessments)

        state.setdefault("metrics_history", [])
        state["metrics_history"].append({
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            **metrics,
        })
        state["metrics_history"] = state["metrics_history"][-1000:]
        self._save_state(state)

        return {
            "primitive": PRIMITIVE,
            "phase": "C6_TRAJECTORY_REVERSIBILITY_INSTRUMENTATION",
            **record,
            **metrics,
            "state_path": str(self.state_path),
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "reversibility_explicit": True,
                "rollback_tested": record["rollback_test_passed"],
                "recovery_tested": record["recovery_test_passed"],
                "abortability_tested": record["abort_test_passed"],
                "non_closure_guard": record["non_closure_preserved"],
                "rollback_guard": True,
                "error_count_target": 0,
            },
        }

    def diagnostics(self) -> dict[str, Any]:
        state = self._load_state()
        assessments = [
            item for item in state.get("assessments", [])
            if isinstance(item, dict)
        ]
        return {
            "primitive": PRIMITIVE,
            "phase": "C6_TRAJECTORY_REVERSIBILITY_INSTRUMENTATION",
            **self._metrics(assessments),
            "state_path": str(self.state_path),
        }


ENGINE = TrajectoryReversibility
