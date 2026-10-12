from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(ROOT/"validation"/"p005_evidence_report.py")],cwd=str(ROOT),check=True)
protected=["validation/p005_product_market_evidence_ladder.py","validation/p005_test_support.py",
"validation/p005_functional_test.py","validation/p005_degradation_test.py","validation/p005_adversarial_test.py",
"validation/p005_non_regression_test.py","validation/p005_cwd_test.py","validation/p005_adversarial_crown_test.py",
"validation/p005_external_evidence_integrity_crown_test.py",
"validation/p005_evidence_report.py","evidence/p005/p005_specification.json","evidence/p005/p005_evidence_report.json"]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
payload={"canonical_id":"P005","status":"LOCKED","protected_hashes":{r:sha(ROOT/r) for r in protected},
"functional_conclusion_only":True,"phenomenology_undetermined":True}
out=ROOT/"evidence"/"p005"/"p005_final_lock.json"; out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("P005_FINAL_LOCK_OK"); print("lock_sha256="+sha(out))
