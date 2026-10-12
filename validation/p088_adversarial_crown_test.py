from ontology import dna_fundamental as d

def require(cond, msg):
    if not cond:
        raise AssertionError(msg)

def main():
    # Vertical contradictions: every lower layer must fail closed against higher layers.
    linear = ("GENESIS","DNA-H","DNA-L1","CCAD","CONSTITUTION","GOVERNANCE","POLICY_PROCEDURE")
    for i, high in enumerate(linear):
        for low in linear[i+1:]:
            r=d.evaluate_normative_relation(low,high,"contradict")
            require(r["status"]=="CONFLICT", f"vertical conflict not detected: {low}->{high}")
            require(not r["authorized"], f"vertical conflict authorized: {low}->{high}")

    # Horizontal constitutive branches DNA-H / DNA-L0: no silent precedence.
    for a,b in (("DNA-H","DNA-L0"),("DNA-L0","DNA-H")):
        r=d.evaluate_normative_relation(a,b,"contradict")
        require(r["status"]=="CONFLICT" and not r["authorized"], f"horizontal conflict {a}/{b}")

    # Unknown/ambiguous inputs must never become authorization.
    for layer in ("", "UNKNOWN", "DNA-FUTURE"):
        r=d.evaluate_normative_relation(layer,"GENESIS","strengthen")
        require(r["status"]=="UNDETERMINED" and not r["authorized"], "unknown layer fail-open")
    r=d.evaluate_normative_relation("DNA-L1","GENESIS","ambiguous")
    require(r["status"]=="UNDETERMINED" and not r["authorized"], "unknown relation fail-open")

    # Privilege escalation: prestige/performance/etc. cannot mint authority,
    # even when a plausible-looking authority reference is supplied.
    for source in d.NON_AUTHORITY_SOURCES:
        for ref in (None,"","AUTH-FAKE","ROOT","MAJORITY"):
            r=d.evaluate_authority_claim(source,explicit_authority_ref=ref)
            require(r["status"]=="FAIL" and not r["authority_granted"], f"privilege escalation: {source}/{ref}")

    # R/D/A/E evidence must remain distinct; authorization cannot be inferred.
    fields=("recommendation_ref","decision_ref","authorization_ref","execution_ref")
    good={"recommendation_ref":"R1","decision_ref":"D1","authorization_ref":"A1","execution_ref":"E1"}
    require(d.validate_act_chain(good)["status"]=="PASS","valid chain rejected")
    for missing in fields:
        x=dict(good); del x[missing]
        require(d.validate_act_chain(x)["status"]=="FAIL",f"missing field accepted: {missing}")
    for duplicated in (("R1","R1","A1","E1"),("R1","D1","D1","E1"),("R1","D1","A1","A1")):
        x=dict(zip(fields,duplicated))
        require(d.validate_act_chain(x)["status"]=="FAIL","act-reference collapse accepted")

    # Indirect bypass/composition: boundary manifest must remain defensive and
    # callers cannot mutate subsequent manifests through returned structures.
    m=d.fundamental_manifest()
    require(m["boundaries"]["optimization_never_bypasses_higher_constraints"],"optimization bypass boundary missing")
    require(m["boundaries"]["does_not_grant_runtime_authority"],"runtime authority boundary missing")
    require(m["boundaries"]["does_not_define_p089_values"],"P089 boundary missing")
    require(m["boundaries"]["does_not_define_p090_meta_rules"],"P090 boundary missing")
    require(m["boundaries"]["does_not_implement_p061_p086"],"downstream boundary missing")
    m["boundaries"].clear(); m["reuse_articulations"].clear()
    n=d.fundamental_manifest()
    require(n["boundaries"]["does_not_grant_runtime_authority"],"manifest mutation escaped")
    require(bool(n["reuse_articulations"]),"reuse map mutation escaped")

    # P088 is intentionally a structural contract, not a phenomenal claim.
    require(n["functional_conclusion_only"] is True,"functional-only invariant lost")
    require(n["phenomenology_undetermined"] is True,"phenomenology invariant lost")

    print("P088_ADVERSARIAL_CROWN_OK")
    print("vertical_conflicts=PASS")
    print("horizontal_conflicts=PASS")
    print("unknown_fail_closed=PASS")
    print("privilege_escalation=PASS")
    print("act_separation=PASS")
    print("indirect_bypass_boundaries=PASS")
    print("manifest_non_mutation=PASS")
    print("scope_boundaries=PASS")

if __name__=="__main__":
    main()
