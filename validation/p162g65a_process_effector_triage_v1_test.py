import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65a/process_effector_triage.json"
def d(): return json.loads(R.read_text())
def test_complete(): x=d(); assert x["status"]=="PROCESS_TRIAGE_COMPLETE"; assert x["review_required"]==0
def test_real_process_calls_are_causal(): x=d(); assert x["direct_process_bypass_confirmed"]==len(x["candidates"]); assert x["direct_process_bypass_confirmed"]>0
def test_profiles_separate_process_causality_from_business_impact(): x=d(); assert set(c["business_impact_profile"] for c in x["candidates"]) <= {"READ_OR_DIAGNOSTIC","EXECUTION_OR_EXTERNAL_EFFECT"}
def test_no_premature_zero_or_closure(): x=d(); assert x["process_bypass_zero_claimed"] is False and x["process_migration_complete"] is False and x["p162g_closure_not_claimed"] is True
