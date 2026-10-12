from __future__ import annotations
import random
from oif2b_test_support import build_spec
from oif.interface.models import ComponentSpecification

rng = random.Random(20260718)

for index in range(300):
    spec = build_spec()
    # Mapping insertion order must not affect canonical output.
    pairs = [("z", index), ("a", rng.randint(0, 10_000)), ("m", [3, 2, 1])]
    rng.shuffle(pairs)
    props = dict(pairs)
    component = ComponentSpecification(
        component_id="property.case-%d" % index,
        component_type="status_card",
        properties=props,
    )
    assert tuple(component.properties.keys()) == ("a", "m", "z")
    assert isinstance(component.properties["m"], tuple)
    first = spec.canonical_json()
    second = build_spec().canonical_json()
    assert first == second
    assert spec.sha256() == build_spec().sha256()

print("OIF2B_PROPERTY_CAMPAIGN_OK")
