from ontology.dna_meta_rules import *
def main():
    for bad in ("M0","M7","m1","",None,"F1"):
        try: get_meta_rule(bad)
        except KeyError: pass
        else: raise AssertionError("invalid MetaRule accepted: %r" % (bad,))
    assert evaluate_non_compensation(("PASS","UNKNOWN"))=="UNDETERMINED"
    assert evidence_requirement(-1,1,1)["status"]=="UNDETERMINED"
    assert evaluate_authority(None)=="NO_EXPANSION_OF_AUTHORITY"
    assert evaluate_fundamental_protection()=="UNDETERMINED"
    print("P090_DEGRADATION_OK")
if __name__=="__main__": main()
