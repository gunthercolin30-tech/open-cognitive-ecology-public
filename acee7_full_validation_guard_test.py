from pathlib import Path
from ontology.acee_validation_runner import AceeValidationRunner
base={"validation_id":"full-guard","scope":"all","mode":"full_isolated","command_results":[]}
r=AceeValidationRunner(root=Path("/nonexistent")).step(inputs=base,persist=False)
assert r["validation_status"]=="ACEE_VALIDATION_BLOCKED" and "full_validation_guarded_until_acee20" in r["blocking_reasons"]
a=dict(base); a["allow_full_validation"]=True; a["milestone"]="ACEE20"; a["command_results"]=[{"name":"full","returncode":0}]
r=AceeValidationRunner(root=Path("/nonexistent")).step(inputs=a,persist=False)
assert r["validation_passed"] is True and r["full_validation_authorized"] is True
print("ACEE7_FULL_VALIDATION_GUARD_OK")
