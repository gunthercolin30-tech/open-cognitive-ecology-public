from ontology import dna_rule_contract as c

def main():
    b = c.contract_manifest()["boundaries"]
    expected = (
        "contract_structure_only",
        "does_not_define_p019_severity_semantics",
        "does_not_define_p020_inheritance",
        "does_not_define_p021_mutation_protocol",
        "does_not_define_p022_lineage_versioning",
        "does_not_define_p023_fitness_suite",
        "does_not_define_p024_adversarial_campaign",
        "does_not_grant_runtime_authority",
        "does_not_claim_end_to_end_enforcement",
        "unknown_may_not_be_promoted_by_contract",
        "functional_conclusion_only",
        "phenomenology_undetermined",
    )
    for key in expected:
        assert b[key] is True
    refs = c.contract_manifest()["transversal_referentials"]
    assert refs["doctrines"] == ("R3", "R4", "R5", "R10", "R11", "R19", "R21")
    assert refs["artifacts"] == ("A-CANON", "A-R0R21", "A-TRACE")
    assert refs["world_models_dependency"] is None
    print("P018_BOUNDARY_TEST_OK")

if __name__ == "__main__":
    main()
