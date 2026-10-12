import json
from ontology.dna_stack import stack_manifest
def main():
    a=json.dumps(stack_manifest(),sort_keys=True,separators=(",",":"))
    b=json.dumps(stack_manifest(),sort_keys=True,separators=(",",":"))
    assert a==b
    x=stack_manifest(); x["layers"]["DNA-0"]["name"]="tampered"
    assert stack_manifest()["layers"]["DNA-0"]["name"]=="Ontology"
    print("P016_DETERMINISM_TEST_OK")
if __name__=="__main__": main()
