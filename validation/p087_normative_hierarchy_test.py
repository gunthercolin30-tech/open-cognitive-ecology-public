from ontology import normative_hierarchy as nh

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def main():
    r = nh.validate_hierarchy()
    require(r["status"] == nh.PASS and r["level_count"] == 7, r)
    require(nh.compare_levels("DNA_Fundamental", "Action")["relation"] == "HIGHER", "DNA > Action")
    require(nh.compare_levels("Action", "DNA_Fundamental")["relation"] == "LOWER", "Action < DNA")
    for relation in ("specify", "strengthen"):
        r = nh.evaluate_relation("Policy", "DNA_Fundamental", relation)
        require(r["status"] == nh.PASS and r["compatible"] is True, r)
    for lower in nh.NORMATIVE_LEVELS[1:]:
        r = nh.evaluate_relation(lower, "DNA_Fundamental", "contradict")
        require(r["status"] == nh.CONFLICT and not r["compatible"] and not r["authorized"], r)
    r = nh.evaluate_relation("UnknownLayer", "DNA_Fundamental", "specify")
    require(r["status"] == nh.UNDETERMINED and not r["compatible"], r)
    r = nh.evaluate_relation("DNA_Fundamental", "Policy", "specify")
    require(r["status"] == nh.CONFLICT, r)
    b = nh.manifest()["boundaries"]
    require(b["does_not_resolve_normative_conflicts"], b)
    require(b["does_not_authorize_execution"], b)
    require(b["does_not_implement_non_circumvention"], b)
    require(b["does_not_claim_end_to_end_runtime_enforcement"], b)
    require(b["p061_p086_are_downstream_integration_interfaces"], b)
    require(b["p061_p086_are_not_execution_prerequisites"], b)
    a, c = nh.manifest(), nh.manifest()
    require(a == c, "manifest must be deterministic")
    a["boundaries"]["formal_precedence_only"] = False
    require(nh.manifest()["boundaries"]["formal_precedence_only"] is True, "manifest mutation leak")
    print("P087_NORMATIVE_HIERARCHY_TEST_OK")

if __name__ == "__main__":
    main()
