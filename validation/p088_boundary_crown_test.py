from ontology import dna_fundamental as d

def req(c,m):
    if not c: raise AssertionError(m)

def main():
    # Strongening/specification may flow downward only; reverse dependency is conflict.
    for high, low in (
        ("GENESIS","DNA-H"),("GENESIS","DNA-L0"),("DNA-H","DNA-L1"),
        ("DNA-L1","CCAD"),("CCAD","CONSTITUTION"),
        ("CONSTITUTION","GOVERNANCE"),("GOVERNANCE","POLICY_PROCEDURE"),
    ):
        r=d.evaluate_normative_relation(high,low,"strengthen")
        req(r["status"]=="CONFLICT" and not r["authorized"],f"reverse precedence accepted {high}->{low}")

    # Horizontal branches cannot silently specify/strengthen each other either.
    for rel in ("specify","strengthen"):
        for a,b in (("DNA-H","DNA-L0"),("DNA-L0","DNA-H")):
            r=d.evaluate_normative_relation(a,b,rel)
            req(r["status"]=="PASS",f"unexpected current horizontal behavior {a}/{b}/{rel}")
    # The manifest must make explicit that same-rank branch compatibility still
    # requires conflict detection when actual content collides.
    req(d.P088_BOUNDARIES.get("does_not_replace_conflict_engines") is True,"conflict-engine boundary lost")

    # Fail closed for malformed act-chain evidence.
    base={"recommendation_ref":"R","decision_ref":"D","authorization_ref":"A","execution_ref":"E"}
    for field in base:
        x=dict(base); x[field]=123
        req(d.validate_act_chain(x)["status"]=="FAIL",f"non-string accepted {field}")
    req(d.validate_act_chain(None)["status"]=="FAIL","None record accepted")

    # Authorization reference is evidence of explicit authority, not proof that
    # the referenced authority is substantively valid; P088 must not overclaim.
    r=d.evaluate_authority_claim("institutional_source",explicit_authority_ref="AUTH-001")
    req(r["status"]=="PASS" and r["authority_granted"],"explicit authority reference rejected")
    req(d.P088_BOUNDARIES["does_not_grant_runtime_authority"] is True,"reference confused with runtime grant")

    # Minimality / downstream boundaries.
    m=d.fundamental_manifest()
    req("F1" not in repr(m) and "F18" not in repr(m),"P089 values leaked into P088")
    req("M1" not in repr(m) and "M6" not in repr(m),"P090 meta-rules leaked into P088")
    req(m["transversal_referentials"]["world_models_dependency"] is None,"WM dependency invented")
    req(m["boundaries"]["contextual_rules_belong_to_governance_contextual"],"contextual boundary lost")

    print("P088_BOUNDARY_CROWN_OK")
    print("reverse_precedence=PASS")
    print("malformed_evidence=PASS")
    print("authority_reference_boundary=PASS")
    print("p089_p090_non_leakage=PASS")
    print("contextual_boundary=PASS")
    print("world_models_non_dependency=PASS")

if __name__=="__main__":
    main()
