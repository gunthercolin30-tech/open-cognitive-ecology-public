from ontology import dna_rule_contract as c

def sample():
    return {
        "rule_id": "P018:test-rule",
        "layer": "DNA-0",
        "scope": "test-only",
        "severity": "UNSPECIFIED_PENDING_P019",
        "rationale": "P018 structural validation fixture.",
        "enforcement": "UNKNOWN",
        "tests": ("validation.p018_dna_rule_contract",),
        "exceptions": (),
        "modification_authority": "UNSPECIFIED_PENDING_GOVERNANCE",
        "version": "fixture-v1",
        "provenance": "P018 validation fixture",
    }

def main():
    assert c.validate_rule_contract(sample())["valid"] is True
    assert tuple(c.normalize_rule(sample())) == c.CANONICAL_FIELDS
    assert c.contract_manifest()["scope"] == "P018_ONLY"
    print("P018_DNA_RULE_CONTRACT_OK")

if __name__ == "__main__":
    main()
