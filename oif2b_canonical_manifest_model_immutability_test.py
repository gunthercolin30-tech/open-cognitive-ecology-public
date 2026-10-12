from dataclasses import FrozenInstanceError
from oif2b_test_support import build_spec
spec = build_spec()
try:
    spec.interface.title = "changed"
    raise AssertionError("frozen dataclass mutated")
except FrozenInstanceError:
    pass
try:
    spec.components[0].properties["compact"] = True
    raise AssertionError("nested mapping mutated")
except TypeError:
    pass
try:
    spec.layout[0].regions[0].component_ids += ("other",)
    raise AssertionError("nested tuple mutated")
except FrozenInstanceError:
    pass
print("OIF2B_IMMUTABILITY_OK")
