from ontology import dna_registry, dna_rule_contract, dna_stack, minimal_dna

def main():
    # Validate only public properties actually exposed by locked predecessors.
    assert minimal_dna.PRIMITIVE == "minimal_architectural_dna"
    assert dna_stack.P016_SCOPE == "P016_ONLY"
    assert dna_registry.P017_SCOPE == "P017_ONLY"
    assert dna_rule_contract.P018_SCOPE == "P018_ONLY"

    assert dna_stack.validate_stack()["valid"] is True
    assert dna_registry.validate_registry()["valid"] is True

    manifest = dna_rule_contract.contract_manifest()
    assert manifest["p017_registry_schema"] == dna_registry.P017_SCHEMA_VERSION
    assert manifest["scope"] == "P018_ONLY"

    boundaries = manifest["boundaries"]
    assert boundaries["does_not_define_p019_severity_semantics"] is True
    assert boundaries["does_not_grant_runtime_authority"] is True
    assert boundaries["unknown_may_not_be_promoted_by_contract"] is True
    assert boundaries["functional_conclusion_only"] is True
    assert boundaries["phenomenology_undetermined"] is True

    print("P018_NON_REGRESSION_TEST_OK")

if __name__ == "__main__":
    main()
