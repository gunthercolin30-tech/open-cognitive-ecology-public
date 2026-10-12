from ontology import dna_registry, dna_rule_contract, dna_severity_model, dna_stack, minimal_dna

def main():
    assert minimal_dna.PRIMITIVE == "minimal_architectural_dna"
    assert dna_stack.validate_stack()["valid"] is True
    assert dna_registry.validate_registry()["valid"] is True
    assert dna_rule_contract.P018_SCOPE == "P018_ONLY"
    assert dna_severity_model.P019_SCOPE == "P019_ONLY"
    m = dna_severity_model.severity_manifest()
    assert m["p018_contract_schema"] == dna_rule_contract.P018_SCHEMA_VERSION
    assert m["boundaries"]["does_not_grant_runtime_authority"] is True
    assert m["boundaries"]["constitutional_severity_is_not_execution_authority"] is True
    print("P019_NON_REGRESSION_TEST_OK")

if __name__ == "__main__":
    main()
