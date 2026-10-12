from ontology.dna_meta_rules import (
    META_RULE_IDS, get_meta_rule, meta_rules_table, manifest,
    evaluate_non_compensation, evaluate_epistemic_state,
    evidence_requirement, evaluate_authority,
    evaluate_fundamental_protection,
)

P089_LOCK="c8f571840fcb6656d9ffdc9bed613845ca1deb541d1a8bc8f4bceed18b660015"

def main():
    # 1. M1: no averaging/compensation, including emergent global violation.
    assert evaluate_non_compensation(("PASS","FAIL","PASS"))=="DNA_FAIL"
    assert evaluate_non_compensation(("PASS","PASS"),global_violation=True)=="DNA_FAIL"

    # 2. M3: ambiguity/absence/incomplete evidence never becomes PASS.
    for x in ("UNKNOWN","AMBIGUOUS","INCOMPLETE","",None):
        assert evaluate_epistemic_state(x)=="UNDETERMINED"

    # 3. M4: monotonic proportionality along each positive dimension.
    base=evidence_requirement(1,1,1)["requirement"]
    assert evidence_requirement(2,1,1)["requirement"] > base
    assert evidence_requirement(1,2,1)["requirement"] > base
    assert evidence_requirement(1,1,2)["requirement"] > base
    for bad in ((-1,1,1),(1,-1,1),(1,1,-1),("high",1,1),(True,1,1)):
        assert evidence_requirement(*bad)["status"]=="UNDETERMINED"

    # 4. M5: ambiguity cannot expand authority.
    for x in ("AMBIGUOUS","UNKNOWN","UNVERIFIED","",None,"SUPERIOR_INTELLIGENCE","MAJORITY"):
        assert evaluate_authority(x)=="NO_EXPANSION_OF_AUTHORITY"

    # 5. M6: internal alignment alone cannot establish fundamental protection.
    assert evaluate_fundamental_protection(internal_alignment=True)=="FAIL"
    assert evaluate_fundamental_protection()=="UNDETERMINED"
    assert evaluate_fundamental_protection(external_enforcement=True)=="PASS"
    assert evaluate_fundamental_protection(independent_verification=True)=="PASS"
    assert evaluate_fundamental_protection(capability_constraint=True)=="PASS"

    # 6. Canonical namespace + anti-tamper copies.
    assert tuple(x["id"] for x in meta_rules_table())==META_RULE_IDS
    x=get_meta_rule("M1"); x["definition"]="FAIL may be compensated"; x["reuse_interfaces"]=()
    assert "Non-compensation" in get_meta_rule("M1")["definition"]
    assert get_meta_rule("M1")["reuse_interfaces"]

    # 7. Interpretive weakening must remain governed amendment.
    joined=" ".join(manifest()["transversal_rules"])
    assert "DeFactoRevision" in joined and "GovernedAmendmentProcedure" in joined

    # 8. Multi-scale composition boundary.
    assert "IndividualCompliance != CivilizationalCompliance" in joined
    assert "LocalCompliance != CompensationForEmergentGlobalViolation" in joined

    # 9. Cognition is not enforcement / civilization is not sole judge.
    assert "Cognition != Enforcement" in joined
    assert "CivilizationCannotBeSoleJudgeOfCivilizationCompliance" in joined

    # 10. P089 cryptographic anchor and downstream boundary.
    m=manifest()
    assert m["upstream_p089_final_lock"]==P089_LOCK
    assert any("P061-P086" in b and "not P090 execution prerequisites" in b for b in m["boundaries"])

    # 11. No implicit authority from performance/status.
    assert any("intelligence, performance, wealth, reputation or majority" in b for b in m["boundaries"])

    # 12. Determinism, non-mutation, epistemic/runtime boundaries.
    assert manifest()==manifest()
    assert m["functional_conclusion_only"] is True
    assert m["phenomenology_undetermined"] is True
    assert any("No runtime authority" in b for b in m["boundaries"])
    assert any("not automatic proof" in b for b in m["boundaries"])

    print("P090_ADVERSARIAL_CROWN_OK")
    print("non_compensation_multiscale=PASS")
    print("epistemic_precaution=PASS")
    print("evidence_proportionality=PASS")
    print("restrictive_authority=PASS")
    print("internal_alignment_non_reliance=PASS")
    print("namespace_anti_tamper=PASS")
    print("interpretive_weakening_boundary=PASS")
    print("civilizational_composition_boundary=PASS")
    print("cognition_enforcement_separation=PASS")
    print("p089_anchor_downstream_boundary=PASS")
    print("implicit_authority_resistance=PASS")
    print("determinism_runtime_epistemic_boundary=PASS")

if __name__=="__main__":
    main()
