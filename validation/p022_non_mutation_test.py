from copy import deepcopy
from ontology import dna_versioning_lineage as d
x=d.create_lineage("I1",d.INDIVIDUAL,"DNA-A",provenance="nonmutation"); before=deepcopy(x)
y=d.migrate_lineage(x,migration_id="M1",to_DNA="DNA-B",mutation_ref="P021:M1",evidence_refs=("E",),authority_ref="A",provenance="nonmutation")
assert x==before and y is not x
m=d.lineage_manifest(); m["boundaries"]["created_under_DNA_is_immutable"]=False
assert d.lineage_manifest()["boundaries"]["created_under_DNA_is_immutable"] is True
print("P022_NON_MUTATION_TEST_OK")
