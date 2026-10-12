from ontology.dna_f1_f18 import canonical_table, get_rule, manifest
def main():
    assert canonical_table() == canonical_table()
    x=get_rule("F17"); x["status"]="MUTATED"
    assert get_rule("F17")["status"] == "CANONICAL"
    assert manifest() == manifest()
    print("P089_DETERMINISM_NON_MUTATION_OK")
if __name__ == "__main__": main()
