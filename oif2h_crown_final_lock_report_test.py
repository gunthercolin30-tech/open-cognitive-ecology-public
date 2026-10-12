import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
path=ROOT/"oif2h_crown_final_lock_report.json"
report=json.loads(path.read_text(encoding="utf-8"))
assert report["milestone"]=="OIF-2H-CROWN"
assert report["status"]=="LOCKED"
assert report["functional_only"] is True
assert report["phenomenology_undetermined"] is True
assert report["core_final_lock_verified"] is True
assert report["adversarial_tests"]==7
for rel,digest in report["protected_hashes"].items():
    assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest, rel
print("OIF2H_CROWN_FINAL_LOCK_REPORT_OK")
