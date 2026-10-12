#!/usr/bin/env python3
from copy import deepcopy
from ontology.acee_final_certifier import ACEEFinalCertifier
def main():
    inputs={"evidence":[]}; before=deepcopy(inputs); ACEEFinalCertifier().step(inputs=inputs); assert inputs==before
    print("ACEE20_NON_REGRESSION_TEST_OK")
if __name__=="__main__": main()
