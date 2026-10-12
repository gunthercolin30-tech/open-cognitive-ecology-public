
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
tests=["p002_minimal_sufficiency_functional_test.py","p002_minimal_sufficiency_degradation_test.py","p002_minimal_sufficiency_adversarial_test.py","p002_minimal_sufficiency_non_regression_test.py","p002_adversarial_crown_test.py","p002_cost_integrity_boundary_crown_test.py"]
for t in tests: subprocess.run([sys.executable,str(ROOT/"validation"/t)],cwd=ROOT,check=True)
legacy_test=ROOT/"tests"/"test_strategy_selection.py"
subprocess.run([sys.executable,str(legacy_test)],cwd=ROOT,check=True)
protected=[ROOT/"ontology"/"strategy_selection.py",ROOT/"evidence"/"p002"/"p002_specification.json",legacy_test]+[ROOT/"validation"/t for t in tests]
hashes={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in protected}
payload={"milestone":"P002","status":"LOCKED","protected_hashes":hashes,"functional_conclusion_only":True,"phenomenology_undetermined":True}
out=ROOT/"evidence"/"p002"/"p002_final_lock.json"
out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("P002_FINAL_LOCK_OK")
print("lock_sha256="+hashlib.sha256(out.read_bytes()).hexdigest())
