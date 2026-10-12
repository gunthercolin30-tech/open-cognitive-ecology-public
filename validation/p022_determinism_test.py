from ontology import dna_versioning_lineage as d
k=dict(entity_id="C1",entity_type=d.CRITICAL_COMPONENT,dna_version="DNA-A",provenance="det")
assert d.create_lineage(**k)==d.create_lineage(**k); assert d.lineage_manifest()==d.lineage_manifest()
print("P022_DETERMINISM_TEST_OK")
