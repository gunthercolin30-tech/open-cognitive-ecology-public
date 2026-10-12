import json
from pathlib import Path
from ontology import dna_versioning_lineage as p22
from ontology import dna_fitness_suite as d
ROOT=Path.home()/"open-cognitive-ecology"
lock=json.loads((ROOT/"validation_evidence/p022_final_lock_report.json").read_text())
assert lock["milestone"]=="P022" and lock["status"]=="LOCKED"
assert p22.P022_SCOPE=="P022_ONLY" and d.P023_SCOPE=="P023_ONLY"
assert d.P023_BOUNDARIES["does_not_define_p024_adversarial_campaign"] is True
print("P023_NON_REGRESSION_TEST_OK")
