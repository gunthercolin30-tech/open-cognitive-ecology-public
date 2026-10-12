from copy import deepcopy
from ontology import dna_severity_model as s
from validation.p018_dna_rule_contract import sample

def main():
    for level in s.SEVERITY_LEVELS:
        rule = deepcopy(sample())
        rule["severity"] = level
        assert s.validate_rule_severity(rule)["valid"] is True
    assert s.compare_severity("ADVISORY", "CONSTITUTIONAL") == -1
    assert s.compare_severity("CONSTITUTIONAL", "STRICT") == 1
    assert s.compare_severity("STANDARD", "STANDARD") == 0
    print("P019_FUNCTIONAL_TEST_OK")

if __name__ == "__main__":
    main()
