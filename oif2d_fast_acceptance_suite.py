from __future__ import annotations
import json
from pathlib import Path

from oif.interface import RegistrySnapshot, validate_manifest

ROOT = Path(__file__).resolve().parent
mapping = json.loads((ROOT / "oif" / "schemas" / "examples" / "minimal_interface.json").read_text(encoding="utf-8"))
registries = RegistrySnapshot.from_values(provider_ids={"runtime.health"}, operation_ids={"refresh"}, component_types={"status_card"})
valid = validate_manifest(mapping, registries=registries)
assert valid.valid
invalid = dict(mapping)
invalid["interface"] = dict(mapping["interface"])
invalid["interface"]["renderer_id"] = "unknown"
rejected = validate_manifest(invalid, registries=registries)
assert not rejected.valid and any(error.code == "unknown_renderer" for error in rejected.errors)
print("OIF2D_FAST_ACCEPTANCE_OK")
