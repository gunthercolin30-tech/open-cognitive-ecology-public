from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
tests=["p004_functional_test.py","p004_degradation_test.py","p004_adversarial_test.py","p004_non_regression_test.py","p004_cwd_test.py","p004_adversarial_crown_test.py"]
results={}
for t in tests:
 p=subprocess.run([sys.executable,str(ROOT/"validation"/t)],cwd=ROOT,text=True,capture_output=True)
 results[t]={"returncode":p.returncode,"stdout":p.stdout.strip()}
 if p.returncode: raise SystemExit(p.stdout+p.stderr)
payload={"canonical_id":"P004","status":"EVIDENCE_READY","tests":results,
 "provenance":{"generator":"validation/p004_evidence_report.py"},
 "configuration":{"confidence_threshold":0.5,"cumulative":True},
 "dependencies":[],"metrics":{"test_count":len(tests),"passed":sum(v["returncode"]==0 for v in results.values())},
 "decision":"READY_FOR_FINAL_LOCK","baseline_reconciliation":"REPO_WIDE_BASELINE_DEFERRED_TO_P007",
 "functional_conclusion_only":True,"phenomenology_undetermined":True}
out=ROOT/"evidence"/"p004"/"p004_evidence_report.json"; out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("P004_EVIDENCE_REPORT_OK")
