"""OIF2 operational interface blueprint.

A declarative, read-only architecture contract for the future NiceGUI operational
interface. This primitive does not start services, write state, execute shell
commands, or claim phenomenal consciousness.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping, Optional

PRIMITIVE = "OIF2_OPERATIONAL_INTERFACE_BLUEPRINT"
VERSION = "oif2-operational-interface-blueprint-v1"
DEPENDENCIES = [
    "civilizational_state_persistence",
    "integrated_civilizational_runtime",
    "civilizational_web_dashboard",
    "civilizational_runtime_governance_console",
    "unified_civilizational_control_center",
]


class OIF2OperationalInterfaceBlueprint:
    """Return a deterministic and governance-bounded interface architecture."""

    _ALLOWED_MODES = {"audit", "local_read_only", "governed_operations"}

    def __init__(self) -> None:
        self.primitive = PRIMITIVE

    @staticmethod
    def _normalize_inputs(inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        if inputs is None:
            return {}
        if not isinstance(inputs, Mapping):
            raise TypeError("inputs must be a mapping or None")
        return dict(inputs)

    def step(
        self,
        inputs: Optional[Mapping[str, Any]] = None,
        persist: bool = False,
    ) -> Dict[str, Any]:
        if persist is not False:
            raise ValueError("blueprint is declarative and cannot persist state")

        normalized = self._normalize_inputs(inputs)
        requested_mode = str(normalized.get("mode", "audit")).strip().lower()
        if requested_mode not in self._ALLOWED_MODES:
            requested_mode = "audit"
            degraded = True
            degradation_reason = "unsupported_mode_fell_back_to_audit"
        else:
            degraded = False
            degradation_reason = None

        nicegui_available = bool(normalized.get("nicegui_available", False))
        ui_environment = str(
            normalized.get("ui_environment", "isolated_.venv-oif")
        ).strip() or "isolated_.venv-oif"

        blueprint = {
            "primitive": self.primitive,
            "version": VERSION,
            "status": "OIF2_OPERATIONAL_INTERFACE_BLUEPRINT_READY",
            "functional_scope_only": True,
            "requested_mode": requested_mode,
            "degraded": degraded,
            "degradation_reason": degradation_reason,
            "architecture": {
                "shell": {
                    "framework": "NiceGUI",
                    "deployment": "local_first",
                    "environment": ui_environment,
                    "nicegui_available": nicegui_available,
                    "installation_required": not nicegui_available,
                    "system_python_mutation_allowed": False,
                },
                "layers": [
                    "presentation",
                    "view_models",
                    "governed_application_services",
                    "runtime_adapters",
                    "persistence_and_audit",
                ],
                "zones": {
                    "overview": {
                        "access": "read_only",
                        "purpose": "civilizational status and health synthesis",
                    },
                    "runtime": {
                        "access": "governed_action",
                        "purpose": "start stop restart and cycle supervision",
                    },
                    "experiments": {
                        "access": "governed_action",
                        "purpose": "experiment launch monitoring and history",
                    },
                    "science": {
                        "access": "read_only_plus_review",
                        "purpose": "validation reports evidence and anomalies",
                    },
                    "memory": {
                        "access": "read_only",
                        "purpose": "civilizational and autobiographical continuity",
                    },
                    "governance": {
                        "access": "approval_gated",
                        "purpose": "review decisions permissions and rollback",
                    },
                    "system": {
                        "access": "read_only_plus_safe_controls",
                        "purpose": "dependencies logs backups and diagnostics",
                    },
                },
                "adapters": {
                    "state": "CivilizationalStatePersistenceAdapter",
                    "runtime": "IntegratedCivilizationalRuntimeAdapter",
                    "dashboard": "CivilizationalDashboardAdapter",
                    "governance": "GovernedRuntimeControlAdapter",
                    "validation": "ValidationReportAdapter",
                },
            },
            "permission_model": {
                "read": "allowed_by_default_for_declared_sources",
                "write": "service_mediated_only",
                "execute": "allowlisted_action_only",
                "approval": "required_for_state_mutation",
                "rollback": "required_for_mutating_operations",
                "shell_execution_from_renderer": False,
                "direct_persistence_from_renderer": False,
            },
            "runtime_contract": {
                "renderer_is_pure": True,
                "services_validate_inputs": True,
                "adapters_translate_only": True,
                "timeouts_required": True,
                "process_termination_required": True,
                "audit_event_required": True,
                "idempotency_required": True,
            },
            "operational_states": [
                "initializing",
                "ready",
                "degraded",
                "busy",
                "approval_required",
                "failed_closed",
                "stopped",
            ],
            "epistemic_invariants": {
                "consciousness_proven": False,
                "subjectivity_proven": False,
                "qualia_proven": False,
                "phenomenology_proven": False,
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
            },
            "anti_closure_constraints": {
                "preserve_future_revisability": True,
                "avoid_single_host_dependency": True,
                "avoid_irreversible_ui_coupling": True,
                "retain_cli_and_non_ui_access": True,
                "support_replaceable_frontends": True,
            },
            "implementation_sequence": [
                "OIF2-0 blueprint and contracts",
                "OIF2-1 isolated UI environment",
                "OIF2-2 read-only application shell",
                "OIF2-3 state and validation adapters",
                "OIF2-4 governed runtime controls",
                "OIF2-5 experiments and history",
                "OIF2-6 governance review workflows",
                "OIF2-7 packaging launcher and recovery",
                "OIF2-8 longitudinal validation and final lock",
            ],
        }
        return deepcopy(blueprint)
