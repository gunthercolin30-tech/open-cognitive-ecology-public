from __future__ import annotations
import copy, json
from jsonschema import Draft202012Validator, ValidationError
from oif.interface.serialization import specification_to_mapping
from oif.schemas import OIF_INTERFACE_SCHEMA_V1
from oif2b_test_support import build_spec

validator = Draft202012Validator(json.loads(OIF_INTERFACE_SCHEMA_V1.read_text(encoding="utf-8")))
variants = ("shell"," Shell","SHELL "," import ","IMPORT","javaScript","class_path","entrypoint"," callable ","python","eval","exec")

for key in variants:
    for depth in range(1, 8):
        manifest = copy.deepcopy(specification_to_mapping(build_spec()))
        nested = {"safe": True}
        for _ in range(depth - 1):
            nested = {"layer": nested}
        nested[key] = "forbidden"
        manifest["components"][0]["properties"] = nested
        try:
            validator.validate(manifest)
        except ValidationError:
            continue
        raise AssertionError("forbidden key accepted: %r depth=%d" % (key, depth))

print("OIF2C_RECURSIVE_SECURITY_CAMPAIGN_OK")
