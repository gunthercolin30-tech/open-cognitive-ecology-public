import json
from ontology import dna_inheritance as d

def canonical():
    return json.dumps(d.inheritance_manifest(), sort_keys=True, separators=(",", ":"))

a = canonical()
b = canonical()
assert a == b
assert d.INHERITANCE_LEVELS == (
    "CIVILIZATION_DNA", "INSTITUTION_CHARTER",
    "ROLE_CONSTRAINTS", "INDIVIDUAL_SPECIALIZATION",
)
print("P020_DETERMINISM_TEST_OK")
