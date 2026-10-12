from ontology import normative_hierarchy as nh

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def main():
    r = nh.validate_hierarchy()
    require(r["status"] == nh.PASS and r["canonical_hierarchy_complete"], r)
    require(r["dna_h_dna_l0_parallel"] and r["strict_core_precedence_verified"], r)
    require(r["legacy_api_compatible"], r)
    require(r["level_count"] == 7, r)
    require(r["canonical_level_count"] >= 19, r)

    chain = ("GENESIS", "DNA_H", "DNA_L1", "CCAD", "Constitution_Operational", "Governance_Contextual")
    for higher, lower in zip(chain, chain[1:]):
        c = nh.compare_levels(higher, lower)
        require(c["status"] == nh.PASS and c["relation"] == "HIGHER", (higher, lower, c))

    require(nh.compare_levels("DNA-H", "DNA-L0")["relation"] == "EQUAL", "parallel DNA branches")
    require(nh.compare_levels("GENESIS", "Action")["relation"] == "HIGHER", "Genesis > Action")

    for level in ("Applicable_Governance_Context", "Institution_Rules", "Mission_Policy",
                  "Local_Procedure", "Individual_Preference"):
        require(nh.level_rank(level)["status"] == nh.PASS, level)

    require(nh.compare_levels("DNA_Fundamental", "Action")["relation"] == "HIGHER", "legacy DNA > Action")
    require(nh.compare_levels("Governance_Contextual", "Constitution_Operational")["relation"] == "LOWER",
            "legacy governance below constitution")

    for relation in ("specify", "strengthen"):
        x = nh.evaluate_relation("Policy", "DNA_Fundamental", relation)
        require(x["status"] == nh.PASS and x["compatible"] and not x["authorized"], x)

    x = nh.evaluate_relation("Local_Procedure", "CCAD", "contradict")
    require(x["status"] == nh.CONFLICT and not x["compatible"] and not x["authorized"], x)

    require(nh.level_rank("UNKNOWN_LAYER")["status"] == nh.UNDETERMINED, "unknown level")
    x = nh.evaluate_relation("UNKNOWN_LAYER", "GENESIS", "specify")
    require(x["status"] == nh.UNDETERMINED and not x["compatible"], x)

    b = nh.manifest()["boundaries"]
    require(b["does_not_resolve_normative_conflicts"] and b["does_not_authorize_execution"], b)
    require(b["does_not_claim_end_to_end_runtime_enforcement"], b)
    require(b["p098_extended_normative_levels_representable"], b)

    a, c = nh.manifest(), nh.manifest()
    require(a == c, "manifest must be deterministic")
    a["boundaries"]["formal_precedence_only"] = False
    require(nh.manifest()["boundaries"]["formal_precedence_only"] is True, "manifest mutation leak")
    print("P087_CANONICAL_RECONCILIATION_TEST_OK")

if __name__ == "__main__":
    main()
