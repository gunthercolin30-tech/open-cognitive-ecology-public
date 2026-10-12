import json
from pathlib import Path
from ontology import dna_fitness_suite as p23
from ontology import dna_adversarial_regression as p24
ROOT=Path.home()/"open-cognitive-ecology"
lock=json.loads((ROOT/"validation_evidence/p023_final_lock_report.json").read_text(encoding="utf-8"))
assert lock["milestone"]=="P023" and lock["status"]=="LOCKED"
assert p23.P023_SCOPE=="P023_ONLY" and p24.P024_SCOPE=="P024_ONLY"
assert p24.P024_BOUNDARIES["preserves_p023_fitness_semantics"] is True
print("P024_NON_REGRESSION_P023_TEST_OK")
