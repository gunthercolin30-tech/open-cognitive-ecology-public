from ontology import dna_versioning_lineage as d
assert d.validate_versioning_lineage_model()
for kind in d.ENTITY_TYPES:
 x=d.create_lineage("E-"+kind,kind,"DNA-v1",provenance="P022-test")
 assert x["created_under_DNA"]=="DNA-v1" and x["current_DNA"]=="DNA-v1" and x["migration_history"]==()
print("P022_DNA_VERSIONING_LINEAGE_OK")
