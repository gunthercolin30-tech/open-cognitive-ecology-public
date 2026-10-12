from __future__ import annotations
from pathlib import Path

from oif.interface import RegistrySnapshot, validate_manifest

ROOT = Path.home() / "open-cognitive-ecology"
registries = RegistrySnapshot.from_values(
    provider_ids={"runtime.health", "governance.proposals"},
    operation_ids={"refresh", "approve.proposal"},
    component_types={"status_card", "proposal_card"},
)
for name, fmt in (("minimal_interface.json", "json"), ("minimal_interface.yaml", "yaml")):
    report = validate_manifest(ROOT / "oif" / "schemas" / "examples" / name, fmt, registries)
    assert report.valid, tuple(error.as_mapping() for error in report.errors)
    assert report.manifest is not None
    assert report.phases_completed == ("parse", "schema", "semantic", "reference", "constitution")
for name, fmt in (("complete_interface.json", "json"), ("complete_interface.yaml", "yaml")):
    report = validate_manifest(ROOT / "oif" / "schemas" / "examples" / name, fmt, registries)
    assert not report.valid
    assert any(error.code == "governance_route_incomplete" for error in report.errors)
print("OIF2D_FUNCTIONAL_OK")
