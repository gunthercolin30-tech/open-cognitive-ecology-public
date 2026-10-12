from copy import deepcopy
from ontology import dna_mutation_protocol as d
r={"mutation_id":"M","stage":d.SANDBOX,"status":"PASS","scope":"DNA","proposal_ref":"p","evidence_refs":("e",),"authority_ref":None,"rollback_ref":"rb","version":"1","provenance":"test"}
before=deepcopy(r); assert d.validate_mutation_record(r); assert r==before
m=d.mutation_protocol_manifest(); m["boundaries"]["does_not_execute_mutation"]=False
assert d.mutation_protocol_manifest()["boundaries"]["does_not_execute_mutation"]
print("P021_NON_MUTATION_TEST_OK")
