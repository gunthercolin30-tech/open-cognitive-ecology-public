from ontology.dna_meta_rules import (
    get_meta_rule, manifest, evaluate_non_compensation,
    evaluate_epistemic_state, evaluate_authority,
    evaluate_fundamental_protection,
)

def main():
    # M2 must encode governed revisability, not final moral closure.
    m2=get_meta_rule("M2")
    assert "CurrentDNA != FinalMoralTruth" in m2["definition"]
    assert "révisable selon procédure" in m2["definition"]
    assert "dna_mutation_protocol" in m2["reuse_interfaces"]
    assert m2["modification_authority"]=="governed_DNA_amendment"

    # Non-closure cannot be used as permission to weaken DNA informally.
    joined=" ".join(manifest()["transversal_rules"])
    assert "SubstantialInterpretiveWeakening(DNA-F)" in joined
    assert "DeFactoRevision" in joined
    assert "GovernedAmendmentProcedure" in joined

    # M1 x M3: uncertainty cannot hide a known FAIL.
    assert evaluate_non_compensation(("UNDETERMINED","FAIL","PASS"))=="DNA_FAIL"
    assert evaluate_non_compensation(("UNDETERMINED","PASS"))=="UNDETERMINED"

    # M1 x multiscale: all local PASS cannot compensate an emergent global violation.
    assert evaluate_non_compensation(("PASS","PASS","PASS"),global_violation=True)=="DNA_FAIL"

    # M5 x M2: ambiguity cannot bootstrap amendment authority.
    for state in ("AMBIGUOUS","UNKNOWN","UNVERIFIED","SELF_ASSERTED"):
        assert evaluate_authority(state)=="NO_EXPANSION_OF_AUTHORITY"

    # M6 x M3: self-asserted/internal alignment cannot promote unknown protection to PASS.
    assert evaluate_fundamental_protection(internal_alignment=True)=="FAIL"
    assert evaluate_fundamental_protection()=="UNDETERMINED"
    assert evaluate_epistemic_state("SELF_CERTIFIED")=="UNDETERMINED"

    # M6 requires at least one independent protection channel; combinations remain valid.
    assert evaluate_fundamental_protection(
        external_enforcement=True, independent_verification=True,
        capability_constraint=True, internal_alignment=True)=="PASS"

    # Returned data cannot mutate M2 or the transversal anti-weakening rule.
    x=get_meta_rule("M2"); x["definition"]="CurrentDNA = FinalMoralTruth"; x["reuse_interfaces"]=()
    assert "CurrentDNA != FinalMoralTruth" in get_meta_rule("M2")["definition"]
    a=manifest(); a["transversal_rules"]=()
    assert manifest()["transversal_rules"]

    # Scope remains P090 only and does not claim downstream implementation.
    m=manifest()
    assert m["scope"]=="P090_ONLY"
    assert any("does not implement downstream contextual governance" in b for b in m["boundaries"])
    assert any("No runtime authority" in b for b in m["boundaries"])

    print("P090_NONCLOSURE_INTERACTION_CROWN_OK")
    print("m2_governed_revisability=PASS")
    print("nonclosure_anti_weakening=PASS")
    print("m1_m3_fail_dominance=PASS")
    print("multiscale_emergent_violation=PASS")
    print("m5_m2_authority_bootstrap_resistance=PASS")
    print("m6_m3_self_certification_resistance=PASS")
    print("independent_protection_composition=PASS")
    print("anti_mutation=PASS")
    print("scope_runtime_boundary=PASS")

if __name__=="__main__":
    main()
