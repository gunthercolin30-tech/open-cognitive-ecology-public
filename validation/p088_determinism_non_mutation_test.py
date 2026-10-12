import copy
from ontology import dna_fundamental as d
def main():
 a=d.fundamental_manifest(); b=d.fundamental_manifest(); assert a==b
 c=copy.deepcopy(a); c["boundaries"]["does_not_grant_runtime_authority"]=False
 assert d.fundamental_manifest()["boundaries"]["does_not_grant_runtime_authority"]
 assert len(d.FUNDAMENTAL_RELATION_DIMENSIONS)==16
 print("P088_DETERMINISM_NON_MUTATION_OK")
if __name__=="__main__": main()
