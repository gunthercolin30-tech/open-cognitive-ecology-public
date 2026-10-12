from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(ROOT/"validation"/"p004_evidence_report.py")],cwd=ROOT,check=True)
protected=[
"validation/p004_evidence_ladder.py","validation/p004_test_support.py",
"validation/p004_functional_test.py","validation/p004_degradation_test.py",
"validation/p004_adversarial_test.py","validation/p004_non_regression_test.py",
"validation/p004_cwd_test.py","validation/p004_adversarial_crown_test.py",
"validation/p004_evidence_semantics_crown_test.py",
"validation/p004_evidence_report.py","evidence/p004/p004_specification.json",
"evidence/p004/p004_evidence_report.json"]
payload={"milestone":"P004","status":"LOCKED",
 "protected_hashes":{r:hashlib.sha256((ROOT/r).read_bytes()).hexdigest() for r in protected},
 "functional_conclusion_only":True,"phenomenology_undetermined":True,
 "baseline_reconciliation":"REPO_WIDE_BASELINE_DEFERRED_TO_P007"}
out=ROOT/"evidence"/"p004"/"p004_final_lock.json"
out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
json.loads(out.read_text(encoding="utf-8"))
print("P004_FINAL_LOCK_OK"); print("lock_sha256="+hashlib.sha256(out.read_bytes()).hexdigest())
