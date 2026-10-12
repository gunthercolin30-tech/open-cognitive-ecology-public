from pathlib import Path
from ontology import dna_inheritance,dna_severity_model,dna_registry,dna_stack,minimal_dna
from ontology import dna_mutation_protocol as d
ROOT=Path.home()/"open-cognitive-ecology"
assert minimal_dna.PRIMITIVE=="minimal_architectural_dna"; assert dna_stack.validate_stack(); assert dna_registry.validate_registry()
assert dna_severity_model.SEVERITY_LEVELS==("ADVISORY","STANDARD","STRICT","CONSTITUTIONAL")
assert dna_inheritance.validate_inheritance_model(); assert (ROOT/"validation_evidence/p020_final_lock_report.json").is_file()
assert d.DEPENDENCIES==["dna_inheritance"] and d.P021_BOUNDARIES["does_not_define_p022_lineage_versioning"]
print("P021_NON_REGRESSION_TEST_OK")
