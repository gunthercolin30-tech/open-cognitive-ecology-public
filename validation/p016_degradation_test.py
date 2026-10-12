from copy import deepcopy
from ontology.dna_stack import DNA_STACK,DNA_STACK_ORDER
def valid(x):
    return tuple(x)==DNA_STACK_ORDER and len(x)==9 and all(x[k].get("name") and x[k].get("p015_domains") for k in DNA_STACK_ORDER)
def main():
    x=deepcopy(DNA_STACK); x.pop("DNA-X"); assert valid(x) is False
    x=deepcopy(DNA_STACK); x["DNA-4"]["p015_domains"]=(); assert valid(x) is False
    print("P016_DEGRADATION_TEST_OK")
if __name__=="__main__": main()
