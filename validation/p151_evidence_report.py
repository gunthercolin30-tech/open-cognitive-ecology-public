from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]; tests=["p151_functional_test.py","p151_degradation_test.py","p151_adversarial_test.py","p151_non_regression_test.py","p151_adversarial_crown_test.py","p151_cwd_independence_test.py"]; results=[]
for n in tests:
 p=ROOT/"validation"/n; r=subprocess.run([sys.executable,str(p)],cwd=str(ROOT),text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT); assert r.returncode==0,r.stdout; results.append({"test":n,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"output":r.stdout.strip()})
out=ROOT/"evidence/p151/p151_evidence_report.json"; out.write_text(json.dumps({"canonical_id":"P151","status":"EVIDENCE_READY","tests":results,"functional_conclusion_only":True,"phenomenology_undetermined":True},indent=2,sort_keys=True)+"\n"); print("P151_EVIDENCE_REPORT_OK")
