from ontology import dna_rule_contract as c
from validation.p018_dna_rule_contract import sample

def main():
    rule = sample()
    out = c.normalize_rule(rule)
    assert out == rule
    assert out is not rule
    assert tuple(out.keys()) == c.CANONICAL_FIELDS
    assert c.P018_BOUNDARIES["does_not_define_p019_severity_semantics"] is True
    assert c.P018_BOUNDARIES["does_not_grant_runtime_authority"] is True
    print("P018_FUNCTIONAL_TEST_OK")

if __name__ == "__main__":
    main()
