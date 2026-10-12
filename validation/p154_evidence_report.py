from pathlib import Path
import sys,json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1]
TESTS=["validation/p154_functional_test.py","validation/p154_degradation_test.py","validation/p154_adversarial_test.py","validation/p154_adversarial_crown_test.py","validation/p154_non_regression_test.py","validation/p154_cwd_independence_test.py"]
results=[]
for rel in TESTS:
 cp=subprocess.run([sys.executable,str(ROOT/rel)],cwd=str(ROOT),capture_output=True,text=True)
 results.append({"path":rel,"returncode":cp.returncode,"stdout":cp.stdout.strip(),"stderr":cp.stderr.strip()})
 if cp.returncode: raise SystemExit(cp.stderr or cp.stdout)
def sha(rel): return hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
report={"canonical_id":"P154","status":"FUNCTIONALLY_VALIDATED_CONTRACT","real_economic_hypotheses_validated":False,"scope":"mechanism_and_falsifiability_contract_only","tests":results,"protected_dependencies":{"p005_final_lock":sha("evidence/p005/p005_final_lock.json"),"p006_final_lock":sha("evidence/p006/p006_final_lock.json"),"p151_final_lock":sha("evidence/p151/p151_final_lock.json")},"implementation_hash":sha("validation/p154_cardinal_economic_hypotheses.py"),"specification_hash":sha("evidence/p154/p154_specification.json"),"functional_conclusion_only":True,"phenomenology_undetermined":True}
out=ROOT/"evidence/p154/p154_evidence_report.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print("P154_EVIDENCE_REPORT_OK")
