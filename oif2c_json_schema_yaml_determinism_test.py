from __future__ import annotations
import hashlib
from oif.interface.serialization import (
    load_yaml_mapping, mapping_to_canonical_json, specification_to_yaml,
)
from oif2b_test_support import build_spec

spec = build_spec()
first = mapping_to_canonical_json(load_yaml_mapping(specification_to_yaml(spec)))
second = mapping_to_canonical_json(load_yaml_mapping(specification_to_yaml(build_spec())))
assert first == second == spec.canonical_json()
digest = hashlib.sha256(first.encode("utf-8")).hexdigest()
assert digest == spec.sha256()
print("OIF2C_DETERMINISM_OK", digest)
