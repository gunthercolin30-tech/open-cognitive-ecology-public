#!/usr/bin/env python3
from ontology.acee_final_certifier import ACEEFinalCertifier
def main():
    result=ACEEFinalCertifier().step(inputs={"evidence":[{"campaign":"unknown","passed":True,"evidence_hash":"bad"}]})
    assert result["certification_complete"] is False
    assert result["unknown_campaigns"]==["unknown"]
    print("ACEE20_DEGRADATION_TEST_OK")
if __name__=="__main__": main()
