#!/usr/bin/env python3
from copy import deepcopy
from ontology.acee_final_certifier import ACEEFinalCertifier, REQUIRED_CAMPAIGNS, evidence_hash
def make(name,passed=True):
    item={"campaign":name,"status":"COMPLETE","passed":passed,"metrics":{},"thresholds":{},"limitations":[]}; item["evidence_hash"]=evidence_hash(item); return item
def main():
    good=[make(x) for x in REQUIRED_CAMPAIGNS]
    assert ACEEFinalCertifier().step(inputs={"evidence":good})["certification_complete"] is True
    bad=deepcopy(good); bad[0]["passed"]=False; bad[0]["evidence_hash"]=evidence_hash(bad[0])
    result=ACEEFinalCertifier().step(inputs={"evidence":bad})
    assert result["certification_complete"] is False and result["failed_campaigns"]
    print("ACEE20_FUNCTIONAL_TEST_OK")
if __name__=="__main__": main()
