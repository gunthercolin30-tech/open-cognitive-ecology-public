from ontology import dna_rule_contract as c
from validation.p018_dna_rule_contract import sample

def main():
    source = sample()
    normalized = c.normalize_rule(source)
    normalized["rule_id"] = "ATTACKED"
    normalized["tests"] = ("ATTACKED",)
    assert source["rule_id"] == "P018:test-rule"
    assert source["tests"] == ("validation.p018_dna_rule_contract",)

    m = c.contract_manifest()
    m["boundaries"]["does_not_grant_runtime_authority"] = False
    assert c.contract_manifest()["boundaries"]["does_not_grant_runtime_authority"] is True
    print("P018_NON_MUTATION_TEST_OK")

if __name__ == "__main__":
    main()
