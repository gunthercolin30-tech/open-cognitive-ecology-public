from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
tests=["p003_functional_test.py","p003_degradation_test.py","p003_adversarial_test.py","p003_non_regression_test.py","p003_cwd_test.py","p003_adversarial_crown_test.py"]
for t in tests: subprocess.run([sys.executable,str(ROOT/"validation"/t)],cwd=ROOT,check=True)
protected=[ROOT/"validation"/"p003_development_evidence_roadmap.py",ROOT/"evidence"/"p003"/"p003_specification.json"]+[ROOT/"validation"/t for t in tests]
payload={"milestone":"P003","status":"LOCKED","protected_hashes":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected},"functional_conclusion_only":True,"phenomenology_undetermined":True,"baseline_reconciliation":"REPO_WIDE_BASELINE_DEFERRED_TO_P007"}
out=ROOT/"evidence"/"p003"/"p003_final_lock.json"
out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
json.loads(out.read_text(encoding="utf-8"))
print("P003_FINAL_LOCK_OK")
print("lock_sha256="+hashlib.sha256(out.read_bytes()).hexdigest())
