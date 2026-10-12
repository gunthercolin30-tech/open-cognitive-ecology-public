from ontology import dna_mutation_protocol as d

def rec(stage,status="PASS",authority=None):
 return {"mutation_id":"M","stage":stage,"status":status,"scope":"DNA","proposal_ref":"p","evidence_refs":("e",),"authority_ref":authority,"rollback_ref":"rb","version":"1","provenance":"test"}

# Governance PASS cannot manufacture authority.
try: d.validate_mutation_record(rec(d.GOVERNANCE,"PASS",None))
except ValueError: pass
else: raise AssertionError("governance PASS without authority accepted")

# Authority reference is evidence/provenance only: boundaries remain no-authority/no-execution.
g=rec(d.GOVERNANCE,"PASS","authority:external")
assert d.validate_mutation_record(g)
assert d.P021_BOUNDARIES["does_not_grant_modification_authority"] is True
assert d.P021_BOUNDARIES["does_not_execute_mutation"] is True
assert d.P021_BOUNDARIES["does_not_replace_existing_governance"] is True

# FAIL and UNDETERMINED never advance.
for status in ("FAIL","UNDETERMINED","PENDING"):
 assert d.can_advance(rec(d.SANDBOX,status,None)) is False

# A complete sequence with one UNDETERMINED cannot be approved.
records=[]
for s in d.MUTATION_STAGES:
 status="UNDETERMINED" if s==d.COMPATIBILITY_ANALYSIS else "PASS"
 authority="authority:external" if s==d.GOVERNANCE else None
 records.append(rec(s,status,authority))
assert d.protocol_decision(tuple(records))=="UNDETERMINED"

# P022 semantic boundary.
assert d.P021_BOUNDARIES["does_not_define_p022_lineage_versioning"] is True
assert d.P021_BOUNDARIES["versioning_stage_is_handoff_only"] is True
print("P021_AUTHORITY_BOUNDARY_TEST_OK")
