from ontology import minimal_dna, dna_stack, dna_registry, dna_rule_contract, dna_severity_model
from ontology import dna_inheritance as d

assert getattr(minimal_dna, "PRIMITIVE", None) == "minimal_architectural_dna"
assert dna_stack.validate_stack()
assert dna_registry.validate_registry()

# P018 non-regression: verify the public contract behavior rather than relying
# on a non-public/non-existent constant name.
p018_fixture = {
    "rule_id": "P018:p020-non-regression",
    "layer": "DNA-0",
    "scope": "fixture",
    "severity": "UNSPECIFIED_PENDING_P019",
    "rationale": "P020 predecessor contract check",
    "enforcement": "UNKNOWN",
    "tests": (),
    "exceptions": (),
    "modification_authority": "UNKNOWN",
    "version": "1",
    "provenance": "P020-non-regression",
}
assert dna_rule_contract.validate_rule_contract(p018_fixture)

assert dna_severity_model.SEVERITY_LEVELS == (
    "ADVISORY", "STANDARD", "STRICT", "CONSTITUTIONAL",
)
assert d.P020_BOUNDARIES["does_not_define_p021_mutation_protocol"] is True
assert d.P020_BOUNDARIES["inheritance_does_not_grant_authority"] is True
assert d.P020_BOUNDARIES["does_not_grant_runtime_authority"] is True

print("P020_NON_REGRESSION_TEST_OK")
