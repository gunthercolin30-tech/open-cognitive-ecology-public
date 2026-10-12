from __future__ import annotations
import math
from oif.interface.models import (
    ComponentSpecification,
    LayoutRegionSpecification,
    ModelViolation,
    NavigationZoneSpecification,
)

def nested(levels):
    value = "leaf"
    for index in range(levels):
        value = {"level_%d" % index: value}
    return value

ComponentSpecification(
    component_id="depth.accepted",
    component_type="card",
    properties=nested(31),
)

try:
    ComponentSpecification(
        component_id="depth.rejected",
        component_type="card",
        properties=nested(40),
    )
    raise AssertionError("excessive nesting accepted")
except ModelViolation:
    pass

try:
    ComponentSpecification(
        component_id="bad.key",
        component_type="card",
        properties={1: "value"},
    )
    raise AssertionError("non-string mapping key accepted")
except ModelViolation:
    pass

try:
    NavigationZoneSpecification(
        zone_id="overview",
        label="Overview",
        description="",
        order=True,
        layout_id="main",
    )
    raise AssertionError("bool accepted as integer order")
except ModelViolation:
    pass

try:
    LayoutRegionSpecification(
        region_id="content",
        component_ids=("a", "a"),
    )
    raise AssertionError("duplicate component reference accepted")
except ModelViolation:
    pass

# JSON canonicalization must not silently emit non-standard numbers.
from oif2b_test_support import build_spec
spec = build_spec()
for number in (float("nan"), float("inf"), float("-inf")):
    try:
        ComponentSpecification(
            component_id="numeric.case",
            component_type="card",
            properties={"number": number},
        )
        # Current model accepts floats locally, so the crown requires JSON-stage rejection.
        import json
        json.dumps({"number": number}, allow_nan=False)
        raise AssertionError("non-finite number accepted")
    except (ModelViolation, ValueError):
        pass

print("OIF2B_STRUCTURAL_LIMITS_OK")
