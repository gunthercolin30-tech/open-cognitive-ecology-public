import json
from pathlib import Path
from ontology import dna_mutation_protocol as p21
from ontology import dna_versioning_lineage as d

ROOT=Path.home()/"open-cognitive-ecology"
lock=json.loads((ROOT/"validation_evidence/p021_final_lock_report.json").read_text())
assert lock["milestone"]=="P021" and lock["status"]=="LOCKED"
assert p21.P021_SCOPE=="P021_ONLY"
assert p21.P021_BOUNDARIES["does_not_define_p022_lineage_versioning"] is True
assert p21.P021_BOUNDARIES["versioning_stage_is_handoff_only"] is True
assert d.P022_SCOPE=="P022_ONLY"
assert d.P022_BOUNDARIES["does_not_define_p023_fitness_suite"] is True
assert d.P022_BOUNDARIES["does_not_define_p024_adversarial_campaign"] is True
assert d.P022_TRANSVERSAL_REFERENTIALS["world_models_dependency"] is None
print("P022_CROWN_NON_REGRESSION_TEST_OK")
