from ontology.dna_meta_rules import *
def main():
    assert meta_rules_table()==meta_rules_table()
    m1=manifest(); m2=manifest(); assert m1==m2
    x=get_meta_rule("M5"); x["definition"]="tampered"; x["reuse_interfaces"]=()
    assert get_meta_rule("M5")["definition"]!="tampered"
    assert get_meta_rule("M5")["reuse_interfaces"]
    print("P090_DETERMINISM_NON_MUTATION_OK")
if __name__=="__main__": main()
