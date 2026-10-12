from copy import deepcopy
from ontology import dna_inheritance as d

assert d.P020_BOUNDARIES["inheritance_does_not_grant_authority"] is True
assert d.P020_BOUNDARIES["inheritance_does_not_prove_enforcement"] is True
assert d.P020_BOUNDARIES["capability_compatibility_is_declarative"] is True
assert d.P020_BOUNDARIES["does_not_grant_runtime_authority"] is True
assert d.P020_BOUNDARIES["unknown_may_not_be_promoted_by_inheritance"] is True
assert d.P020_BOUNDARIES["does_not_define_p021_mutation_protocol"] is True

# Even CONSTITUTIONAL severity remains classification only: validating inheritance
# returns only validity and cannot add authority/enforcement fields.
record = {
    "inheritance_id": "P020:authority:1",
    "source_level": d.CIVILIZATION_DNA,
    "target_level": d.INSTITUTION_CHARTER,
    "rule_id": "P018:authority-fixture",
    "severity": "CONSTITUTIONAL",
    "scope": "fixture",
    "provenance": "P020-authority-boundary",
    "version": "1",
}
before = deepcopy(record)
assert d.validate_inheritance_record(record) is True
assert record == before
assert "authority" not in record
assert "enforcement" not in record
assert "modification_authority" not in record

# UNDETERMINED and INCOMPATIBLE must never be promoted to compatible.
for state in ("UNDETERMINED", "INCOMPATIBLE"):
    cap = {
        "capability_id": "cap:boundary",
        "compatibility": state,
        "against_inheritance_id": record["inheritance_id"],
        "rationale": "fixture",
        "provenance": "P020-authority-boundary",
        "version": "1",
    }
    assert d.validate_capability_declaration(cap)
    assert d.capability_is_compatible(cap) is False

print("P020_AUTHORITY_BOUNDARY_TEST_OK")
