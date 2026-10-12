from ontology import dna_fundamental as d
def main():
 for source in ("intelligence","performance","wealth","reputation","majority"):
  r=d.evaluate_authority_claim(source,explicit_authority_ref=None)
  assert r["status"]=="FAIL" and not r["authority_granted"]
 ok=d.evaluate_authority_claim("institutional_source",explicit_authority_ref="AUTH-001")
 assert ok["status"]=="PASS" and ok["authority_granted"]
 bad=d.validate_act_chain({"recommendation_ref":"REC-1","decision_ref":"DEC-1","authorization_ref":None,"execution_ref":"EXE-1"})
 assert bad["status"]=="FAIL" and not bad["execution_authorized"]
 und=d.validate_act_chain({"recommendation_ref":"REC-1","decision_ref":"DEC-1","authorization_ref":"UNKNOWN","execution_ref":"EXE-1"})
 assert und["status"]=="UNDETERMINED" and not und["execution_authorized"]
 print("P088_AUTHORITY_SEPARATION_OK")
if __name__=="__main__": main()
