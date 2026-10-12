# Official provider composition for the OIF operational shell.
from __future__ import annotations

from pathlib import Path
from typing import Optional

from oif.adapters.civilizational_state_adapter import CivilizationalStateAdapter
from oif.adapters.runtime_health_adapter import RuntimeHealthAdapter
from oif.adapters.validation_report_adapter import ValidationReportAdapter
from oif.application.shell_service import ProviderSpec

DEFAULT_ROOT = Path.home() / "open-cognitive-ecology"


def build_default_provider_specs(
    root: Optional[Path] = None,
) -> tuple[ProviderSpec, ...]:
    governed_root = Path(root) if root is not None else DEFAULT_ROOT
    return (
        ProviderSpec(
            name="validation-report",
            zone="science",
            provider=ValidationReportAdapter(root=governed_root),
        ),
        ProviderSpec(
            name="runtime-health",
            zone="runtime",
            provider=RuntimeHealthAdapter(root=governed_root),
        ),
        ProviderSpec(
            name="civilizational-state",
            zone="memory",
            provider=CivilizationalStateAdapter(root=governed_root),
        ),
    )
