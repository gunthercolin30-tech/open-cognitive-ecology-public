from copy import deepcopy
from ontology import dna_versioning_lineage as d
x=d.create_lineage("I1",d.INSTITUTION,"DNA-A",provenance="degradation")
bad=deepcopy(x); bad["current_DNA"]="DNA-B"
try: d.validate_lineage(bad)
except ValueError: pass
else: raise AssertionError("silent current_DNA rewrite accepted")
for kind in ("individual","UNKNOWN","CRITICAL"):
 try: d.create_lineage("X",kind,"DNA-A",provenance="degradation")
 except ValueError: pass
 else: raise AssertionError("invalid entity type accepted")
try: d.migrate_lineage(x,migration_id="M0",to_DNA="DNA-A",mutation_ref="P021:M0",evidence_refs=(),authority_ref="AUTH",provenance="degradation")
except ValueError: pass
else: raise AssertionError("no-op DNA migration accepted")
print("P022_DEGRADATION_TEST_OK")
