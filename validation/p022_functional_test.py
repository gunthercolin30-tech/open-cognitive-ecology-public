from ontology import dna_versioning_lineage as d
x=d.create_lineage("IND-1",d.INDIVIDUAL,"DNA-A",provenance="functional")
y=d.migrate_lineage(x,migration_id="M1",to_DNA="DNA-B",mutation_ref="P021:M1",evidence_refs=("EV1",),authority_ref="AUTH1",provenance="functional")
z=d.migrate_lineage(y,migration_id="M2",to_DNA="DNA-C",mutation_ref="P021:M2",evidence_refs=("EV2",),authority_ref="AUTH2",provenance="functional")
assert z["created_under_DNA"]=="DNA-A" and z["current_DNA"]=="DNA-C"
assert tuple(m["from_DNA"] for m in z["migration_history"])==("DNA-A","DNA-B")
assert tuple(m["to_DNA"] for m in z["migration_history"])==("DNA-B","DNA-C")
print("P022_FUNCTIONAL_TEST_OK")
