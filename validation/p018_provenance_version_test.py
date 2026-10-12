from copy import deepcopy
from ontology import dna_rule_contract as c
from validation.p018_dna_rule_contract import sample

def main():
    for field in ("version", "provenance"):
        x = deepcopy(sample())
        x[field] = ""
        assert c.validate_rule_contract(x)["valid"] is False

    m = c.contract_manifest()
    assert m["version"] == "P018-v1"
    assert m["schema_version"] == "oce.p018.dna_rule_contract.v1"
    assert m["p017_registry_schema"] == "oce.p017.dna_registry.v1"
    assert m["transversal_referentials"]["world_models_dependency"] is None
    print("P018_PROVENANCE_VERSION_TEST_OK")

if __name__ == "__main__":
    main()
