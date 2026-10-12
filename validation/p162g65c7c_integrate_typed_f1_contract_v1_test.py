from pathlib import Path
from ontology.acee_installation_executor import AceeInstallationExecutor
from ontology.f1_validation_command_contract import REQUIRED_ROLES
def obj(): return AceeInstallationExecutor.__new__(AceeInstallationExecutor)
def typed(kind="VALIDATION_MAIN"): return [{"role":r,"kind":kind} for r in REQUIRED_ROLES]
def test_typed_validation_main_compiles_to_exact_module_argv():
 cmds,reasons=obj()._validate_f1_command_contract(typed())
 assert reasons==[] and len(cmds)==7
 assert all(x["argv"][1:]==["-m","validation.main"] for x in cmds)
def test_legacy_opaque_argv_is_rejected():
 raw=[{"role":r,"argv":["python3","x.py"]} for r in REQUIRED_ROLES]
 cmds,reasons=obj()._validate_f1_command_contract(raw)
 assert cmds==[] and reasons==["local_validation_opaque_argv_forbidden"]
def test_registered_script_fails_closed_until_registry_binding():
 raw=[{"role":r,"kind":"REGISTERED_SCRIPT","script_id":f"id_{r}"} for r in REQUIRED_ROLES]
 cmds,reasons=obj()._validate_f1_command_contract(raw)
 assert cmds==[] and len(reasons)==7
 assert all(x.startswith("local_validation_registered_script_unresolved:") for x in reasons)
def test_f2_bounded_validation_path_preserved():
 s=(Path(__file__).resolve().parents[1]/"ontology/acee_installation_executor.py").read_text()
 assert '[sys.executable, "-m", "validation.main", "--full"]' in s
def test_backup_exists():
 assert (Path(__file__).resolve().parents[1]/"ontology/acee_installation_executor.py.bak.p162g65c7c").is_file()
