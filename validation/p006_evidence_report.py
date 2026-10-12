from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
tests=["p006_functional_test.py","p006_degradation_test.py","p006_adversarial_test.py","p006_non_regression_test.py","p006_cwd_test.py","p006_adversarial_crown_test.py","p006_temporal_preregistration_crown_test.py"]
rows=[]
for name in tests:
    p=subprocess.run([sys.executable,str(ROOT/"validation"/name)],cwd=str(ROOT),text=True,capture_output=True)
    rows.append({"test":name,"returncode":p.returncode,"stdout":p.stdout.strip(),"stderr":p.stderr.strip()})
    if p.returncode: raise SystemExit(p.stdout+p.stderr)
report={"canonical_id":"P006","status":"EVIDENCE_COMPLETE",
"reuse":["ontology/theory_falsification_framework.py","ontology/trajectory_decision_policy.py",
"ontology/reflexive_threshold_replication_result_evaluator.py","ontology/reference_runtime_freeze_protocol.py"],
"delta":"preregistered canonical four-outcome decision contract",
"baseline_reconciliation":"DEFERRED_TO_P007","tests":rows,
"functional_conclusion_only":True,"phenomenology_undetermined":True}
out=ROOT/"evidence"/"p006"/"p006_evidence_report.json"; out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("P006_EVIDENCE_REPORT_OK")
