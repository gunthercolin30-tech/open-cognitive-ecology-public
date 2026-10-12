from ontology import dna_versioning_lineage as d

x=d.create_lineage("E",d.INDIVIDUAL,"DNA-A",provenance="authority")
for auth in ("",None):
 try:
  d.migrate_lineage(x,migration_id="M1",to_DNA="DNA-B",mutation_ref="P021:M1",evidence_refs=("EV",),authority_ref=auth,provenance="authority")
 except ValueError: pass
 else: raise AssertionError("migration_without_authority_ref_accepted")

m=d.lineage_manifest()
assert m["boundaries"]["does_not_grant_mutation_authority"] is True
assert m["boundaries"]["does_not_execute_structural_mutation"] is True
assert m["boundaries"]["undetermined_is_not_pass"] is True
assert "APPROVED" not in d.ENTITY_TYPES
assert "PASS" not in d.ENTITY_TYPES
print("P022_AUTHORITY_BOUNDARY_TEST_OK")
