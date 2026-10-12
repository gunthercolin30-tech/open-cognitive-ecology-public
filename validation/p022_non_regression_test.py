import json
from pathlib import Path
from ontology import minimal_dna,dna_stack,dna_registry,dna_severity_model,dna_inheritance,dna_mutation_protocol,dna_versioning_lineage as d
ROOT=Path.home()/"open-cognitive-ecology"
assert minimal_dna.PRIMITIVE=="minimal_architectural_dna"; assert dna_stack.validate_stack(); assert dna_registry.validate_registry()
assert dna_severity_model.SEVERITY_LEVELS==("ADVISORY","STANDARD","STRICT","CONSTITUTIONAL")
assert dna_inheritance.validate_inheritance_model(); assert dna_mutation_protocol.validate_mutation_protocol()
lock=json.loads((ROOT/"validation_evidence/p021_final_lock_report.json").read_text())
assert lock["milestone"]=="P021" and lock["status"]=="LOCKED"; assert d.DEPENDENCIES==["dna_mutation_protocol"]
print("P022_NON_REGRESSION_TEST_OK")
