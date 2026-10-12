from ontology import dna_mutation_protocol as d
def rec(stage,status="PASS"):
 return {"mutation_id":"M1","stage":stage,"status":status,"scope":"DNA","proposal_ref":"proposal:M1","evidence_refs":("e1",),"authority_ref":"gov:M1" if stage==d.GOVERNANCE else None,"rollback_ref":"rb:M1","version":"1","provenance":"P021-test"}
records=tuple(rec(s) for s in d.MUTATION_STAGES)
for a,b in d.ALLOWED_TRANSITIONS: assert d.validate_transition(a,b)
assert d.protocol_decision(records)=="APPROVED"
print("P021_FUNCTIONAL_TEST_OK")
