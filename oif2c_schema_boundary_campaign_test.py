from __future__ import annotations
import copy, json
from jsonschema import Draft202012Validator, ValidationError
from oif.interface.serialization import specification_to_mapping
from oif.schemas import OIF_INTERFACE_SCHEMA_V1
from oif2b_test_support import build_spec

validator = Draft202012Validator(json.loads(OIF_INTERFACE_SCHEMA_V1.read_text(encoding="utf-8")))
base = specification_to_mapping(build_spec())

def reject(value):
    try:
        validator.validate(value)
    except ValidationError:
        return
    raise AssertionError("invalid boundary accepted")

for length in (127, 128):
    case = copy.deepcopy(base); case["interface"]["interface_id"] = "a" * length
    validator.validate(case)
case = copy.deepcopy(base); case["interface"]["interface_id"] = "a" * 129; reject(case)

for length in (8191, 8192):
    case = copy.deepcopy(base); case["interface"]["description"] = "x" * length
    validator.validate(case)
case = copy.deepcopy(base); case["interface"]["description"] = "x" * 8193; reject(case)

for count in (255, 256, 257):
    case = copy.deepcopy(base)
    prototype = case["navigation"]["zones"][0]
    case["navigation"]["zones"] = []
    for index in range(count):
        item = copy.deepcopy(prototype)
        item["zone_id"] = "z%d" % index
        item["layout_id"] = "l%d" % index
        case["navigation"]["zones"].append(item)
    case["navigation"]["default_zone_id"] = "z0"
    if count <= 256:
        validator.validate(case)
    else:
        reject(case)

print("OIF2C_SCHEMA_BOUNDARY_CAMPAIGN_OK")
