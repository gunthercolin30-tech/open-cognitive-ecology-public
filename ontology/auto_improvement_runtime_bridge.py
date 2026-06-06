"""
AUTO_IMPROVEMENT_RUNTIME_BRIDGE

Connects the self-improvement pipeline to higher-level runtimes so that
experience can automatically trigger governance-approved improvement cycles.
"""

from typing import Any, Dict, List, Optional

from ontology.experience_integration_loop import ExperienceIntegrationLoop
from ontology.meta_learning_optimizer import MetaLearningOptimizer
from ontology.autonomous_capability_discovery import AutonomousCapabilityDiscovery
from ontology.recursive_self_improvement_controller import (
    RecursiveSelfImprovementController,
)
from ontology.civilizational_meta_governance import CivilizationalMetaGovernance


class AutoImprovementRuntimeBridge:
    primitive_name = "AUTO_IMPROVEMENT_RUNTIME_BRIDGE"

    def __init__(self) -> None:
        self.experience_integration = ExperienceIntegrationLoop()
        self.meta_learning_optimizer = MetaLearningOptimizer()
        self.capability_discovery = AutonomousCapabilityDiscovery()
        self.self_improvement_controller = RecursiveSelfImprovementController()
        self.meta_governance = CivilizationalMetaGovernance()

    def step(
        self,
        objective: str = "",
        action_result: Optional[Dict[str, Any]] = None,
        expected_result: Optional[Dict[str, Any]] = None,
        observed_gaps: Optional[List[str]] = None,
        validation_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        observed_gaps = observed_gaps or []
        validation_result = validation_result or {"error_count": 0}

        experience = self.experience_integration.step(
            objective=objective,
            action_result=action_result,
            expected_result=expected_result,
        )

        experience_records = [experience["state"]]

        meta_learning = self.meta_learning_optimizer.step(experience_records)

        capability = self.capability_discovery.step(
            observed_gaps=observed_gaps,
            performance_metrics=meta_learning,
        )

        improvement = self.self_improvement_controller.step(
            priority_capability=capability.get("priority_capability"),
            recommended_capabilities=capability.get("recommended_capabilities"),
            validation_result=validation_result,
        )

        governance = self.meta_governance.step(
            proposed_change=improvement.get("priority_capability"),
            validation_result=validation_result,
        )

        return {
            "primitive": self.primitive_name,
            "runtime_bridge_completed": True,
            "experience_integration": experience,
            "meta_learning": meta_learning,
            "capability_discovery": capability,
            "self_improvement": improvement,
            "meta_governance": governance,
            "approved": governance.get("approved", False),
        }


__all__ = ["AutoImprovementRuntimeBridge"]
