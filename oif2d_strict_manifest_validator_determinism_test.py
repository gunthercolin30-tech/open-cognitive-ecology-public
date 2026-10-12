from __future__ import annotations
import json
from pathlib import Path

from oif.interface import RegistrySnapshot, validate_manifest

ROOT = Path.home() / "open-cognitive-ecology"
mapping = json.loads((ROOT / "oif" / "schemas" / "examples" / "minimal_interface.json").read_text(encoding="utf-8"))
registries = RegistrySnapshot.from_values(provider_ids=set(), operation_ids=set(), component_types=set())
reports = [validate_manifest(mapping, registries=registries) for _ in range(5)]
serialized = [tuple(tuple(error.as_mapping().items()) for error in report.errors) for report in reports]
assert len(set(serialized)) == 1
print("OIF2D_DETERMINISM_OK")
