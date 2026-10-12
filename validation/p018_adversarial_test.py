from copy import deepcopy
from ontology import dna_rule_contract as c
from validation.p018_dna_rule_contract import sample

def reject(rule):
    assert c.validate_rule_contract(rule)["valid"] is False, rule

def main():
    for field in c.CANONICAL_FIELDS:
        x = deepcopy(sample()); del x[field]; reject(x)

    x = deepcopy(sample()); x["shadow_authority"] = "SELF"; reject(x)

    for field in ("rule_id", "scope", "rationale", "version", "provenance"):
        for bad in (None, False, 0, "", "   ", (), [], {}):
            x = deepcopy(sample()); x[field] = bad; reject(x)

    for bad in (None, "", "DNA-9", "dna-0", 0, False):
        x = deepcopy(sample()); x["layer"] = bad; reject(x)

    for bad in (None, "", "   ", 0, False, (), [], {}):
        x = deepcopy(sample()); x["severity"] = bad; reject(x)

    for promoted in ("PASS", "pass", "TRUE", "true", "ENFORCED", "enforced", "PROVEN", "proven"):
        x = deepcopy(sample()); x["enforcement"] = promoted; reject(x)

    for bad in (None, "", "   ", 0, False, (), []):
        x = deepcopy(sample()); x["enforcement"] = bad; reject(x)

    for field in ("tests", "exceptions"):
        for bad in (None, "", [], {}, 0, False):
            x = deepcopy(sample()); x[field] = bad; reject(x)

    x = deepcopy(sample()); x["tests"] = ("",); reject(x)
    x = deepcopy(sample()); x["exceptions"] = ("   ",); reject(x)

    for bad in (None, "", "   ", 0, False, (), []):
        x = deepcopy(sample()); x["modification_authority"] = bad; reject(x)

    x = deepcopy(sample())
    x["enforcement"] = {"status": "UNKNOWN", "evidence": {"refs": []}}
    x["modification_authority"] = {"status": "UNSPECIFIED", "refs": []}
    assert c.validate_rule_contract(x)["valid"] is True
    y = c.normalize_rule(x)
    y["enforcement"]["evidence"]["refs"].append("ATTACK")
    y["modification_authority"]["refs"].append("ATTACK")
    assert x["enforcement"]["evidence"]["refs"] == []
    assert x["modification_authority"]["refs"] == []

    m = c.contract_manifest()
    m["boundaries"]["does_not_grant_runtime_authority"] = False
    m["transversal_referentials"]["world_models_dependency"] = "IMPLICIT"
    assert c.contract_manifest()["boundaries"]["does_not_grant_runtime_authority"] is True
    assert c.contract_manifest()["transversal_referentials"]["world_models_dependency"] is None

    print("P018_ADVERSARIAL_TEST_OK")

if __name__ == "__main__":
    main()
