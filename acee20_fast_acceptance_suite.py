#!/usr/bin/env python3
from ontology.acee_final_certifier import ACEEFinalCertifier, REQUIRED_CAMPAIGNS, evidence_hash
def main():
    evidence=[]
    for name in REQUIRED_CAMPAIGNS:
        item={"campaign":name,"status":"COMPLETE","passed":True,"metrics":{},"thresholds":{},"limitations":[]}
        item["evidence_hash"]=evidence_hash(item); evidence.append(item)
    result=ACEEFinalCertifier().step(inputs={"evidence":evidence},persist=False)
    assert result["status"]=="AUTONOMOUS_COGNITIVE_EVOLUTION_COMPLETE"
    assert result["certification_complete"] is True
    assert result["error_count"]==0
    assert result["epistemic_status"]["functional_conclusion_only"] is True
    print("ACEE20_FAST_ACCEPTANCE_OK")
if __name__=="__main__": main()
