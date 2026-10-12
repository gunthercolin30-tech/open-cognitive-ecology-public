from ontology import dna_mutation_protocol as d

def rec(stage,status="PASS"):
 return {"mutation_id":"M","stage":stage,"status":status,"scope":"DNA","proposal_ref":"p","evidence_refs":("e",),"authority_ref":"authority:M" if stage==d.GOVERNANCE and status=="PASS" else None,"rollback_ref":"rb","version":"1","provenance":"test"}

# Exact lexical vocabulary only.
for bad in ("proposal"," PROPOSAL","PROPOSAL ","PASS ","TRUE","UNKNOWN","APPROVED","PАSS"):
 try:
  if "PROPOSAL" in bad: d.validate_stage(bad)
  else: d.validate_mutation_record({**rec(d.SANDBOX), "status":bad})
 except ValueError: pass
 else: raise AssertionError("lexical near-miss accepted: "+bad)

# Exhaustive transition matrix: exactly eight adjacent edges.
for a in d.MUTATION_STAGES:
 for b in d.MUTATION_STAGES:
  expected=(a,b) in d.ALLOWED_TRANSITIONS
  try: d.validate_transition(a,b); got=True
  except ValueError: got=False
  assert got is expected, (a,b,expected,got)

# No reordered, duplicated, skipped or suffix-only protocol.
bad_sequences=[
 (d.IMPACT_ANALYSIS,),
 (d.PROPOSAL,d.SANDBOX),
 (d.PROPOSAL,d.PROPOSAL),
 (d.PROPOSAL,d.IMPACT_ANALYSIS,d.ADVERSARIAL_TESTS),
]
for seq in bad_sequences:
 try: d.protocol_decision(tuple(rec(x) for x in seq))
 except ValueError: pass
 else:
  if seq!=(d.PROPOSAL,): raise AssertionError("non-canonical sequence accepted")

# Exact field contract: no missing or authority-like extra field.
base=rec(d.SANDBOX)
for mutation in (
 {k:v for k,v in base.items() if k!="provenance"},
 {**base,"modification_authority":"self"},
 {**base,"runtime_authority":True},
 {**base,"enforcement":"PASS"},
):
 try: d.validate_mutation_record(mutation)
 except ValueError: pass
 else: raise AssertionError("malformed/authority-inflated record accepted")

print("P021_ADVERSARIAL_TEST_OK")
