from ontology.dna_f1_f18 import get_rule
def main():
    try:
        get_rule("F19")
    except KeyError:
        pass
    else:
        raise AssertionError("unknown DNA-F must fail closed")
    assert get_rule("F18")["status"] == "CANONICAL"
    x=get_rule("F18"); x["status"]="PROPOSED_PENDING_CANONICAL_REVIEW"
    assert get_rule("F18")["status"] == "CANONICAL"
    print("P089_DEGRADATION_OK")
if __name__ == "__main__": main()
