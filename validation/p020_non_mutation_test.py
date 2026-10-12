from copy import deepcopy
from ontology import dna_inheritance as d

record = {
    "inheritance_id": "P020:test:immutability",
    "source_level": d.ROLE_CONSTRAINTS,
    "target_level": d.INDIVIDUAL_SPECIALIZATION,
    "rule_id": "P018:test",
    "severity": "STRICT",
    "scope": "fixture",
    "provenance": "P020-non-mutation",
    "version": "1",
}
before = deepcopy(record)
assert d.validate_inheritance_record(record)
assert record == before

m1 = d.inheritance_manifest()
m1["boundaries"]["does_not_grant_runtime_authority"] = False
m2 = d.inheritance_manifest()
assert m2["boundaries"]["does_not_grant_runtime_authority"] is True
print("P020_NON_MUTATION_TEST_OK")
