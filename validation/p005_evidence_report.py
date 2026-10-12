from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
tests=["p005_functional_test.py","p005_degradation_test.py","p005_adversarial_test.py","p005_non_regression_test.py","p005_cwd_test.py","p005_adversarial_crown_test.py","p005_external_evidence_integrity_crown_test.py"]
rows=[]
for name in tests:
    p=subprocess.run([sys.executable,str(ROOT/"validation"/name)],cwd=str(ROOT),text=True,capture_output=True)
    rows.append({"test":name,"returncode":p.returncode,"stdout":p.stdout.strip(),"stderr":p.stderr.strip()})
    if p.returncode: raise SystemExit(p.stdout+p.stderr)
report={"canonical_id":"P005","objective":"Separate technical evidence from market evidence.",
"acceptance":"Do not promote a market to priority without measurable external demand or reuse signal.",
"baseline_reconciliation":"DEFERRED_TO_P007","tests":rows,
"functional_conclusion_only":True,"phenomenology_undetermined":True}
out=ROOT/"evidence"/"p005"/"p005_evidence_report.json"; out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("P005_EVIDENCE_REPORT_OK")
