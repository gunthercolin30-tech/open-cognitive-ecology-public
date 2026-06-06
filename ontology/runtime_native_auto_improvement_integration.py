"""
RUNTIME_NATIVE_AUTO_IMPROVEMENT_INTEGRATION

Provides a lightweight adapter that can be embedded into high-level runtimes
to trigger the auto-improvement pipeline after each operational cycle.
"""

from typing import Any, Dict, List, Optional

from ontology.auto_improvement_runtime_bridge import AutoImprovementRuntimeBridge


class RuntimeNativeAutoImprovementIntegration:
    primitive_name = "RUNTIME_NATIVE_AUTO_IMPROVEMENT_INTEGRATION"

    def __init__(self) -> None:
        self.bridge = AutoImprovementRuntimeBridge()
        self.cycle_count = 0

    def step(
        self,
        objective: str = "",
        action_result: Optional[Dict[str, Any]] = None,
        expected_result: Optional[Dict[str, Any]] = None,
        observed_gaps: Optional[List[str]] = None,
        validation_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self.cycle_count += 1

        auto_improvement = self.bridge.step(
            objective=objective,
            action_result=action_result,
            expected_result=expected_result,
            observed_gaps=observed_gaps,
            validation_result=validation_result,
        )

        return {
            "primitive": self.primitive_name,
            "cycle_count": self.cycle_count,
            "auto_improvement_triggered": True,
            "approved": auto_improvement.get("approved", False),
            "auto_improvement": auto_improvement,
        }


__all__ = ["RuntimeNativeAutoImprovementIntegration"]
