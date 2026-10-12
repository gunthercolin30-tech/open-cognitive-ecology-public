from pathlib import Path
from ontology import minimal_dna,dna_stack,dna_registry,dna_severity_model,dna_inheritance,dna_mutation_protocol as d
ROOT=Path.home()/"open-cognitive-ecology"
assert minimal_dna.PRIMITIVE=="minimal_architectural_dna"
assert dna_stack.validate_stack()
assert dna_registry.validate_registry()
assert dna_severity_model.SEVERITY_LEVELS==("ADVISORY","STANDARD","STRICT","CONSTITUTIONAL")
assert dna_inheritance.validate_inheritance_model()
assert (ROOT/"validation_evidence/p020_final_lock_report.json").is_file()
assert d.validate_mutation_protocol()
m=d.mutation_protocol_manifest()
assert m["scope"]=="P021_ONLY"
assert m["transversal_referentials"]["world_models_dependency"] is None
assert tuple(m["reuse_map"])==d.MUTATION_STAGES
assert m["boundaries"]["functional_conclusion_only"] is True
assert m["boundaries"]["phenomenology_undetermined"] is True
assert m["boundaries"]["does_not_define_p022_lineage_versioning"] is True
print("P021_CROWN_NON_REGRESSION_TEST_OK")
