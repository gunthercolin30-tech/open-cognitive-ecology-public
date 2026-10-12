from ontology.dna_stack import *
def main():
    m=stack_manifest()
    assert len(DNA_STACK_ORDER)==9
    assert tuple(m["layers"])==DNA_STACK_ORDER
    assert validate_stack()["valid"] is True
    print("P016_FUNCTIONAL_TEST_OK")
if __name__=="__main__": main()
