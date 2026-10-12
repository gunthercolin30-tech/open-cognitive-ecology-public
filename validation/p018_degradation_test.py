from copy import deepcopy
from ontology import dna_rule_contract as c
from validation.p018_dna_rule_contract import sample

def must_fail(rule):
    assert c.validate_rule_contract(rule)["valid"] is False

def main():
    for field in c.CANONICAL_FIELDS:
        x = deepcopy(sample())
        x.pop(field)
        must_fail(x)

    x = deepcopy(sample())
    x["unexpected"] = "forbidden"
    must_fail(x)

    x = deepcopy(sample())
    x["rule_id"] = ""
    must_fail(x)

    x = deepcopy(sample())
    x["layer"] = "DNA-UNKNOWN"
    must_fail(x)

    x = deepcopy(sample())
    x["tests"] = []
    must_fail(x)

    x = deepcopy(sample())
    x["exceptions"] = []
    must_fail(x)

    for promoted in ("PASS", "TRUE", "ENFORCED", "PROVEN"):
        x = deepcopy(sample())
        x["enforcement"] = promoted
        must_fail(x)

    print("P018_DEGRADATION_TEST_OK")

if __name__ == "__main__":
    main()
