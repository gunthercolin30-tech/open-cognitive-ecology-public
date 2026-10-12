from copy import deepcopy

from ontology import dna_severity_model as s
from validation.p018_dna_rule_contract import sample

def main():
    manifest = s.severity_manifest()
    b = manifest["boundaries"]

    assert b["does_not_grant_runtime_authority"] is True
    assert b["constitutional_severity_is_not_execution_authority"] is True
    assert b["does_not_claim_end_to_end_enforcement"] is True
    assert b["unknown_may_not_be_promoted_by_severity"] is True

    # Classification must not mutate or promote enforcement/authority.
    rule = deepcopy(sample())
    rule["severity"] = "CONSTITUTIONAL"
    rule["enforcement"] = "UNKNOWN"
    rule["modification_authority"] = "UNSPECIFIED_PENDING_GOVERNANCE"

    before = deepcopy(rule)
    assert s.validate_rule_severity(rule)["valid"] is True
    assert rule == before
    assert rule["enforcement"] == "UNKNOWN"
    assert rule["modification_authority"] == "UNSPECIFIED_PENDING_GOVERNANCE"

    # Ranking a constitutional rule is classification only.
    assert s.severity_rank(rule["severity"]) == 3
    assert rule["enforcement"] == "UNKNOWN"

    print("P019_AUTHORITY_BOUNDARY_TEST_OK")

if __name__ == "__main__":
    main()
