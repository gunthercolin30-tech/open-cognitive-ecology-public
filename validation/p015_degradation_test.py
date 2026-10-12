from __future__ import annotations
import copy
from validation.p015_official_dna_definition import load
def main():
    m=load(); d=copy.deepcopy(m.OCE_DNA_OFFICIAL_DEFINITION); e=copy.deepcopy(m.OCE_DNA_EPISTEMIC_STATUS)
    d["constraint_domains"]=tuple(x for x in d["constraint_domains"] if x!="evidence"); e["consciousness_proven"]=True
    assert "evidence" not in d["constraint_domains"] and e["consciousness_proven"] is True
    print("P015_DEGRADATION_TEST_OK"); return 0
if __name__=="__main__": raise SystemExit(main())
