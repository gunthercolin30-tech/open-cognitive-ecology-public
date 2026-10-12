from __future__ import annotations
import copy
import json
from jsonschema import Draft202012Validator, ValidationError
from oif.interface.serialization import SerializationViolation, load_yaml_mapping
from oif.schemas import OIF_INTERFACE_SCHEMA_V1
from oif2b_test_support import build_spec
from oif.interface.serialization import specification_to_mapping

schema = json.loads(OIF_INTERFACE_SCHEMA_V1.read_text(encoding="utf-8"))
validator = Draft202012Validator(schema)
for key in ("shell", " IMPORT ", "JavaScript", "class_path"):
    manifest = copy.deepcopy(specification_to_mapping(build_spec()))
    manifest["components"][0]["properties"] = {"nested": {key: "x"}}
    try:
        validator.validate(manifest)
        raise AssertionError("forbidden declarative key accepted: %r" % key)
    except ValidationError:
        pass

unsafe = "value: !!python/object/apply:os.system ['echo forbidden']\n"
try:
    load_yaml_mapping(unsafe)
    raise AssertionError("unsafe YAML tag accepted")
except SerializationViolation:
    pass

print("OIF2C_SECURITY_OK")
