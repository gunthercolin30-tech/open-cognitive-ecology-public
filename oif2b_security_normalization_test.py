from __future__ import annotations
from oif.interface.models import ComponentSpecification, ModelViolation

keys = (
    "Shell",
    " IMPORT ",
    "Class_Path",
    "JavaScript",
    "Callable",
    "ENTRYPOINT",
)

for key in keys:
    for properties in (
        {key: "x"},
        {"nested": {key: "x"}},
        {"nested": [{key: "x"}]},
        {"nested": ({"deeper": {key: "x"}},)},
    ):
        try:
            ComponentSpecification(
                component_id="security.case",
                component_type="card",
                properties=properties,
            )
            raise AssertionError("normalized forbidden key accepted: %r" % key)
        except ModelViolation:
            pass

print("OIF2B_SECURITY_NORMALIZATION_OK")
