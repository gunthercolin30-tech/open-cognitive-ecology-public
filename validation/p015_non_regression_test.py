from __future__ import annotations
from validation.p015_official_dna_definition import load
def main():
    m=load(); p=m.MinimalDNAPrimitive({"identity":"oce"},{"specialization":"test"}); r=p.step()
    assert r["viable"] and r["ready_for_transmission"] and r["minimal_dna_integrity_score"]==1.0 and p.genome()["identity"]=="oce"
    print("P015_NON_REGRESSION_TEST_OK"); return 0
if __name__=="__main__": raise SystemExit(main())
