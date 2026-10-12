from ontology.dna_f1_f18 import *
def main():
    assert validate_structure()["valid"]
    assert len(canonical_table()) == 18
    assert get_rule("F17")["category"] == "DNA_values"
    assert get_rule("F18")["status"] == "CANONICAL"
    print("P089_FUNCTIONAL_OK")
if __name__ == "__main__": main()
