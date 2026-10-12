import json
from pathlib import Path
from ontology import dna_fitness_suite as d
from ontology import dna_versioning_lineage as p22
ROOT=Path.home()/"open-cognitive-ecology"
lock=json.loads((ROOT/"validation_evidence/p022_final_lock_report.json").read_text(encoding="utf-8"))
assert lock["milestone"]=="P022" and lock["status"]=="LOCKED"
assert p22.P022_SCOPE=="P022_ONLY"
assert d.P023_SCOPE=="P023_ONLY"
assert d.P023_BOUNDARIES["fitness_does_not_create_norms"] is True
assert d.P023_BOUNDARIES["fitness_does_not_grant_authority"] is True
assert d.P023_BOUNDARIES["does_not_define_p024_adversarial_campaign"] is True
assert d.P023_TRANSVERSAL_REFERENTIALS["world_models_dependency"] is None
print("P023_CROWN_NON_REGRESSION_TEST_OK")
