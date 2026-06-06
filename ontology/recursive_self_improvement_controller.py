"""
RECURSIVE_SELF_IMPROVEMENT_CONTROLLER

Orchestrates autonomous selection and execution of prioritized capability
improvements in a traceable and reversible manner.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional


class RecursiveSelfImprovementController:
    primitive_name = "RECURSIVE_SELF_IMPROVEMENT_CONTROLLER"

    def __init__(self) -> None:
        self.improvement_history = []

    def step(
        self,
        priority_capability: Optional[str] = None,
        recommended_capabilities: Optional[List[str]] = None,
        validation_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        recommended_capabilities = recommended_capabilities or []
        validation_result = validation_result or {}

        if not priority_capability:
            priority_capability = (
                recommended_capabilities[0]
                if recommended_capabilities
                else None
            )

        if not priority_capability:
            return {
                "primitive": self.primitive_name,
                "improvement_executed": False,
                "reason": "no_priority_capability",
                "history_length": len(self.improvement_history),
            }

        error_count = int(validation_result.get("error_count", 0))
        integration_status = "accepted" if error_count == 0 else "rejected"

        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "priority_capability": priority_capability,
            "validation_result": validation_result,
            "integration_status": integration_status,
        }

        self.improvement_history.append(record)

        return {
            "primitive": self.primitive_name,
            "improvement_executed": True,
            "priority_capability": priority_capability,
            "integration_status": integration_status,
            "history_length": len(self.improvement_history),
            "state": record,
        }


__all__ = ["RecursiveSelfImprovementController"]
