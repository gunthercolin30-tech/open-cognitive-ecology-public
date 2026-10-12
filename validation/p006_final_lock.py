from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(ROOT/"validation"/"p006_evidence_report.py")],cwd=str(ROOT),check=True)
protected=["validation/p006_go_rethink_stop.py","validation/p006_test_support.py","validation/p006_functional_test.py",
"validation/p006_degradation_test.py","validation/p006_adversarial_test.py","validation/p006_non_regression_test.py",
"validation/p006_cwd_test.py","validation/p006_adversarial_crown_test.py","validation/p006_temporal_preregistration_crown_test.py","validation/p006_evidence_report.py",
"evidence/p006/p006_specification.json","evidence/p006/p006_evidence_report.json"]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
payload={"canonical_id":"P006","status":"LOCKED","protected_hashes":{r:sha(ROOT/r) for r in protected},
"functional_conclusion_only":True,"phenomenology_undetermined":True}
out=ROOT/"evidence"/"p006"/"p006_final_lock.json"
out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("P006_FINAL_LOCK_OK"); print("lock_sha256="+sha(out))
