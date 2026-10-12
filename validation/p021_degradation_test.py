from ontology import dna_mutation_protocol as d
def r(stage,status):
 return {"mutation_id":"M2","stage":stage,"status":status,"scope":"DNA","proposal_ref":"p","evidence_refs":(),"authority_ref":"gov" if stage==d.GOVERNANCE and status=="PASS" else None,"rollback_ref":"rb","version":"1","provenance":"test"}
assert not d.can_advance(r(d.SANDBOX,"FAIL")); assert not d.can_advance(r(d.SANDBOX,"UNDETERMINED"))
assert d.protocol_decision((r(d.PROPOSAL,"PASS"),r(d.IMPACT_ANALYSIS,"FAIL")))=="REJECTED"
assert d.protocol_decision((r(d.PROPOSAL,"PASS"),))=="UNDETERMINED"
try: d.validate_transition(d.PROPOSAL,d.SANDBOX)
except ValueError: pass
else: raise AssertionError("stage bypass accepted")
print("P021_DEGRADATION_TEST_OK")
