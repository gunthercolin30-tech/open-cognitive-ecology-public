import json
from ontology import dna_rule_contract as c
from validation.p018_dna_rule_contract import sample

def stable(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))

def main():
    a = c.normalize_rule(sample())
    b = c.normalize_rule(sample())
    assert stable(a) == stable(b)
    assert stable(c.contract_manifest()) == stable(c.contract_manifest())
    print("P018_DETERMINISM_TEST_OK")

if __name__ == "__main__":
    main()
