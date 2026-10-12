import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c4/python_validation_subfamily_audit.json"
def d(): return json.loads(R.read_text())
def test_required_families_are_distinct():
 x=d()["families"]
 assert x["ENVIRONMENT_FINGERPRINT"]==1
 assert x["CANONICAL_VALIDATION_MODULE"]==2
 assert x["ISOLATED_GENERATED_PROBE"]==7
 assert x["ROOT_BOUNDED_GENERAL_PYTHON_RUNNER"]==1
def test_false_positive_not_granted_python_policy():
 x=d(); assert x["families"]["NON_PYTHON_FALSE_POSITIVE"]==3
 assert x["policy"]["NON_PYTHON_FALSE_POSITIVE"]=="REMOVE_FROM_PYTHON_VALIDATION_DENOMINATOR"
def test_general_runner_kept_higher_power():
 assert d()["policy"]["ROOT_BOUNDED_GENERAL_PYTHON_RUNNER"]=="HIGHER_POWER_SEPARATE_POLICY_REQUIRED"
def test_no_automatic_migration_or_closure():
 x=d()
 assert x["automatic_migration_performed"] is False
 assert x["authorization_created"] is False and x["execution_performed"] is False
 assert x["process_bypass_zero_claimed"] is False and x["process_migration_complete"] is False
 assert x["p162g_closure_not_claimed"] is True and x["p162h_opened"] is False
