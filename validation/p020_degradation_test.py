from ontology import dna_inheritance as d

bad_edges = (
    (d.CIVILIZATION_DNA, d.ROLE_CONSTRAINTS),
    (d.INSTITUTION_CHARTER, d.INDIVIDUAL_SPECIALIZATION),
    (d.INDIVIDUAL_SPECIALIZATION, d.CIVILIZATION_DNA),
)
for edge in bad_edges:
    try:
        d.validate_inheritance_edge(*edge)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid edge accepted: {edge}")

cap = {
    "capability_id": "cap:test",
    "compatibility": "UNDETERMINED",
    "against_inheritance_id": "P020:test:1",
    "rationale": "insufficient evidence",
    "provenance": "P020-degradation",
    "version": "1",
}
assert d.validate_capability_declaration(cap)
assert d.capability_is_compatible(cap) is False

for invalid in ("PASS", "TRUE", "UNKNOWN", "", "compatible"):
    x = dict(cap)
    x["compatibility"] = invalid
    try:
        d.validate_capability_declaration(x)
    except ValueError:
        pass
    else:
        raise AssertionError(f"invalid compatibility accepted: {invalid!r}")
print("P020_DEGRADATION_TEST_OK")
