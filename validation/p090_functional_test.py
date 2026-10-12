from ontology.dna_meta_rules import *
def main():
    assert tuple(x["id"] for x in meta_rules_table()) == META_RULE_IDS
    assert evaluate_non_compensation(("PASS","PASS"))=="PASS"
    assert evaluate_non_compensation(("PASS","FAIL","PASS"))=="DNA_FAIL"
    assert evaluate_epistemic_state("unknown")=="UNDETERMINED"
    assert evidence_requirement(2,3,4)["requirement"]==24.0
    assert evaluate_authority("ambiguous")=="NO_EXPANSION_OF_AUTHORITY"
    assert evaluate_fundamental_protection(independent_verification=True)=="PASS"
    assert evaluate_fundamental_protection(internal_alignment=True)=="FAIL"
    print("P090_FUNCTIONAL_OK")
if __name__=="__main__": main()
