"""Renderer-independent composition service for OIF2-2."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Callable, Mapping

from ontology.oif2_operational_interface_blueprint import (
    OIF2OperationalInterfaceBlueprint,
)

SCHEMA_VERSION = "oif2.read-only-shell.v1"
PRIMITIVE = "OIF2_READ_ONLY_APPLICATION_SHELL"

EPISTEMIC_INVARIANTS = MappingProxyType({
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
})

Provider = Callable[[], Mapping[str, Any]]


@dataclass(frozen=True)
class ProviderSpec:
    name: str
    zone: str
    provider: Provider


class OIF2ReadOnlyApplicationService:
    """Compose the official read-only shell from injectable providers."""

    def __init__(
        self,
        providers: tuple[ProviderSpec, ...] = (),
        blueprint: OIF2OperationalInterfaceBlueprint | None = None,
    ) -> None:
        self._providers = tuple(providers)
        self._blueprint = blueprint or OIF2OperationalInterfaceBlueprint()
        names = [spec.name for spec in self._providers]
        if len(names) != len(set(names)):
            raise ValueError("provider names must be unique")

    @staticmethod
    def _safe_mapping(value: Mapping[str, Any], provider_name: str) -> dict[str, Any]:
        if not isinstance(value, Mapping):
            raise TypeError(f"provider {provider_name} must return a mapping")
        return deepcopy(dict(value))

    def snapshot(self) -> dict[str, Any]:
        blueprint = self._blueprint.step(
            inputs={
                "mode": "local_read_only",
                "nicegui_available": True,
                "ui_environment": "isolated_.venv-oif",
            },
            persist=False,
        )
        zones = blueprint["architecture"]["zones"]
        cards: list[dict[str, Any]] = []
        degraded: list[dict[str, str]] = []

        for spec in self._providers:
            if spec.zone not in zones:
                raise ValueError(f"unknown OIF zone: {spec.zone}")
            try:
                payload = self._safe_mapping(spec.provider(), spec.name)
            except Exception as exc:
                payload = {
                    "status": "unavailable",
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                }
                degraded.append({
                    "provider": spec.name,
                    "zone": spec.zone,
                    "error_type": type(exc).__name__,
                })
            cards.append({
                "provider": spec.name,
                "zone": spec.zone,
                "access": zones[spec.zone]["access"],
                "payload": payload,
            })

        return {
            "primitive": PRIMITIVE,
            "schema_version": SCHEMA_VERSION,
            "status": "degraded" if degraded else "ready",
            "read_only": True,
            "renderer_replaceable": True,
            "direct_persistence_from_renderer": False,
            "shell_execution_from_renderer": False,
            "zones": deepcopy(zones),
            "cards": cards,
            "degraded_providers": degraded,
            "provider_count": len(self._providers),
            "epistemic_invariants": dict(EPISTEMIC_INVARIANTS),
        }
