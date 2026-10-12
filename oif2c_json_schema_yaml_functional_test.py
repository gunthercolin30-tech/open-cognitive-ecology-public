from __future__ import annotations
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from oif.interface.serialization import (
    load_json_mapping, load_yaml_mapping, mapping_to_canonical_json,
    specification_to_json, specification_to_mapping, specification_to_yaml,
)
from oif.schemas import OIF_INTERFACE_SCHEMA_V1
from oif2b_test_support import build_spec

ROOT = Path.home() / "open-cognitive-ecology"
schema = json.loads(OIF_INTERFACE_SCHEMA_V1.read_text(encoding="utf-8"))
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema)

spec = build_spec()
mapping = specification_to_mapping(spec)
validator.validate(mapping)
assert specification_to_json(spec) == spec.canonical_json()

yaml_text = specification_to_yaml(spec)
yaml_mapping = load_yaml_mapping(yaml_text)
validator.validate(yaml_mapping)
assert mapping_to_canonical_json(yaml_mapping) == spec.canonical_json()

for name in ("minimal_interface.json", "complete_interface.json"):
    validator.validate(load_json_mapping(ROOT / "oif" / "schemas" / "examples" / name))
for name in ("minimal_interface.yaml", "complete_interface.yaml"):
    validator.validate(load_yaml_mapping(ROOT / "oif" / "schemas" / "examples" / name))

print("OIF2C_FUNCTIONAL_OK")
