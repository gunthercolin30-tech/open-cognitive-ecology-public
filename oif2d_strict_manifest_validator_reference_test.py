from __future__ import annotations
import json
from pathlib import Path

from oif.interface import RegistrySnapshot, validate_manifest

ROOT = Path.home() / "open-cognitive-ecology"
mapping = json.loads((ROOT / "oif" / "schemas" / "examples" / "minimal_interface.json").read_text(encoding="utf-8"))
registries = RegistrySnapshot.from_values(provider_ids=set(), operation_ids=set(), component_types=set())
report = validate_manifest(mapping, registries=registries)
codes = {error.code for error in report.errors}
assert {"unknown_provider", "unknown_operation", "unknown_component"}.issubset(codes), codes
print("OIF2D_REFERENCE_OK")
