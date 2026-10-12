import json
from pathlib import Path
from ontology import dna_adversarial_regression as d
ROOT=Path.home()/"open-cognitive-ecology"
r=json.loads((ROOT/"validation_evidence/p023_final_lock_report.json").read_text(encoding="utf-8"))
assert r["milestone"]=="P023" and r["status"]=="LOCKED"
assert d.validate_adversarial_regression()
assert d.P024_SCOPE=="P024_ONLY"
print("P024_CROWN_NON_REGRESSION_TEST_OK")
