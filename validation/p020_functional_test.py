from ontology import dna_inheritance as d

record = {
    "inheritance_id": "P020:test:1",
    "source_level": d.CIVILIZATION_DNA,
    "target_level": d.INSTITUTION_CHARTER,
    "rule_id": "P018:test",
    "severity": "CONSTITUTIONAL",
    "scope": "fixture",
    "provenance": "P020-functional",
    "version": "1",
}
assert d.validate_inheritance_record(record)

cap = {
    "capability_id": "cap:test",
    "compatibility": "COMPATIBLE",
    "against_inheritance_id": record["inheritance_id"],
    "rationale": "fixture",
    "provenance": "P020-functional",
    "version": "1",
}
assert d.validate_capability_declaration(cap)
assert d.capability_is_compatible(cap) is True
print("P020_FUNCTIONAL_TEST_OK")
