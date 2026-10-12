from __future__ import annotations
import copy
import json
from jsonschema import Draft202012Validator, ValidationError
from oif.schemas import OIF_INTERFACE_SCHEMA_V1
from oif2b_test_support import build_spec
from oif.interface.serialization import specification_to_mapping

schema = json.loads(OIF_INTERFACE_SCHEMA_V1.read_text(encoding="utf-8"))
validator = Draft202012Validator(schema)
base = specification_to_mapping(build_spec())

cases = []
missing = copy.deepcopy(base); missing.pop("interface"); cases.append(missing)
unknown = copy.deepcopy(base); unknown["unexpected"] = True; cases.append(unknown)
bad_id = copy.deepcopy(base); bad_id["interface"]["interface_id"] = "Bad ID"; cases.append(bad_id)
bad_type = copy.deepcopy(base); bad_type["navigation"]["zones"][0]["order"] = True; cases.append(bad_type)
bad_version = copy.deepcopy(base); bad_version["schema_version"] = "oif.interface.v2"; cases.append(bad_version)
duplicate = copy.deepcopy(base); duplicate["components"][0]["operation_ids"] = ["refresh", "refresh"]; cases.append(duplicate)

for case in cases:
    try:
        validator.validate(case)
        raise AssertionError("invalid manifest accepted")
    except ValidationError:
        pass

print("OIF2C_DEGRADATION_OK")
