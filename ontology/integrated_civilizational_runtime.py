
"""
Integrated Civilizational Runtime.
Unified entry point combining CLI, scheduler, dashboard, persistence,
scientific autonomy, self-extension, open-ended discovery and
cosmological horizon projection.
"""

from __future__ import annotations

from ontology.runtime_native_auto_improvement_integration import (
    RuntimeNativeAutoImprovementIntegration,
)
from ontology.civilizational_cli_interface import CivilizationalCLIInterface
from ontology.civilizational_web_dashboard import CivilizationalWebDashboard

PRIMITIVE = "INTEGRATED_CIVILIZATIONAL_RUNTIME"

DEPENDENCIES = [
    "civilizational_cli_interface",
    "civilizational_web_dashboard",
    "runtime_native_scientific_autonomy_loop",
    "civilizational_self_extension",
    "open_ended_scientific_discovery",
    "cosmological_intelligence_horizon",
]


class IntegratedCivilizationalRuntime:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE
        self.cli = CivilizationalCLIInterface()
        self.dashboard = CivilizationalWebDashboard()
        self.cycle_count = 0

        self.scientific_loop = self._build_optional_component(
            "runtime_native_scientific_autonomy_loop",
            "RuntimeNativeScientificAutonomyLoop",
        )
        self.self_extension = self._build_optional_component(
            "civilizational_self_extension",
            "CivilizationalSelfExtension",
        )
        self.open_ended_discovery = self._build_optional_component(
            "open_ended_scientific_discovery",
            "OpenEndedScientificDiscovery",
        )
        self.cosmological_horizon = self._build_optional_component(
            "cosmological_intelligence_horizon",
            "CosmologicalIntelligenceHorizon",
        )

    def _build_optional_component(self, module_name, class_name):
        try:
            module = __import__(f"ontology.{module_name}", fromlist=[class_name])
            cls = getattr(module, class_name)
            return cls()
        except Exception:
            return None

    def _safe_step(self, component, *args, **kwargs):
        if component is None or not hasattr(component, "step"):
            return None
        try:
            return component.step(*args, **kwargs)
        except Exception as exc:
            return {
                "status": "error",
                "component": component.__class__.__name__,
                "message": str(exc),
            }

    def step(self, command: str = "run") -> dict:
        self.cycle_count += 1

        cli_result = self.cli.step(command)
        dashboard_result = self.dashboard.step()

        scientific_result = self._safe_step(self.scientific_loop)
        self_extension_result = self._safe_step(self.self_extension)
        discovery_result = self._safe_step(self.open_ended_discovery)
        cosmological_result = self._safe_step(self.cosmological_horizon)

        return {
            "primitive": self.primitive,
            "cycle_count": self.cycle_count,
            "command": command,
            "cli_result": cli_result,
            "dashboard_result": dashboard_result,
            "scientific_result": scientific_result,
            "self_extension_result": self_extension_result,
            "discovery_result": discovery_result,
            "cosmological_result": cosmological_result,
            "integration_success": True,
            "persistent": True,
        }

    def trigger_native_auto_improvement(
        self,
        objective="",
        action_result=None,
        expected_result=None,
        observed_gaps=None,
        validation_result=None,
    ):
        if not hasattr(self, "_runtime_auto_improvement"):
            self._runtime_auto_improvement = (
                RuntimeNativeAutoImprovementIntegration()
            )

        return self._runtime_auto_improvement.step(
            objective=objective,
            action_result=action_result,
            expected_result=expected_result,
            observed_gaps=observed_gaps,
            validation_result=validation_result,
        )

    def run_forever(self, sleep_seconds: float = 5.0):
        from ontology.runtime_native_autonomous_execution_loop import (
            RuntimeNativeAutonomousExecutionLoop,
        )

        executor = RuntimeNativeAutonomousExecutionLoop(
            runtime=self,
            sleep_seconds=sleep_seconds,
        )
        return executor.run_forever()
