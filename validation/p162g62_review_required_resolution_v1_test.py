import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT/"validation_artifacts/p162/p162g/g6"
R=json.loads((A/"g62_review_required_resolution.json").read_text())
D=json.loads((A/"g62_effector_mediation_registry.json").read_text())
def test_six_resolved(): assert R["review_input_count"]==6 and R["review_remaining"]==0
def test_validation_runner_is_bypass():
 x=next(v for v in R["resolutions"] if v["path"]=="ontology/acee_validation_runner.py")
 assert x["classification"]=="DIRECT_BYPASS_CONFIRMED" and x["migration_required"] is True
def test_five_observational_paths_noncausal():
 assert sum(x["classification"]=="NONCAUSAL_VERIFIED" for x in R["resolutions"])==5
def test_scope_does_not_exempt_filesystem():
 assert R["filesystem_classification_implied"] is False
 assert all(x["filesystem_classification_implied"] is False for x in R["resolutions"])
def test_registry_still_open_for_migration():
 assert D["high_power_triage_complete"] is True
 assert D["high_power_review_required_remaining"]==0
 assert D["historical_effector_migration_complete"] is False
 assert D["status"]=="OPEN_MIGRATION_REQUIRED"
def test_total_high_power_direct_bypass_is_eleven():
 high=[e for e in D["entries"] if e.get("classification")=="DIRECT_BYPASS_CONFIRMED" and
       any(c in {"PROCESS","NETWORK","DATABASE"} for c in e.get("effect_classes",[]))]
 assert len(high)==11
