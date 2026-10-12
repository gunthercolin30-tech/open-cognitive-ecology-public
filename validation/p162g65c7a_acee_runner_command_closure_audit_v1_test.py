import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c7a/acee_runner_command_closure_audit.json"
def d(): return json.loads(R.read_text())
def test_role_set_closed_command_set_not_closed():
 f=d()["findings"]; assert len(f["required_roles"])==7 and f["roles_closed"] is True
 assert f["argv_grammar_closed"] is False and f["script_identity_closed"] is False
def test_current_power_explicit():
 f=d()["findings"]
 assert f["root_relative_python_script_class_present"] is True
 assert f["ambient_environment_inherited"] is True
 assert f["production_source_of_commands"]=="admission_context.local_validation_commands"
def test_no_premature_closure():
 x=d()
 assert x["migration_performed"] is False and x["authorization_created"] is False
 assert x["execution_performed"] is False and x["process_bypass_zero_claimed"] is False
 assert x["process_migration_complete"] is False and x["p162g_closure_not_claimed"] is True
