from pathlib import Path
import sys
from ontology.acee_validation_runner import AceeValidationRunner

def runner(tmp_path):
    return AceeValidationRunner(root=tmp_path)

def test_validation_main_is_only_closed_production_grammar(tmp_path):
    r=runner(tmp_path)
    assert r._allowed_command([sys.executable,"-m","validation.main"],False)==(True,"")
    assert r._allowed_command([sys.executable,"-m","validation.main","--full"],True)==(True,"")

def test_any_root_python_script_is_blocked(tmp_path):
    p=tmp_path/"probe.py"; p.write_text("print(1)\n")
    ok,reason=runner(tmp_path)._allowed_command([sys.executable,str(p)],False)
    assert ok is False and reason=="unregistered_python_command"

def test_relative_root_python_script_is_blocked(tmp_path):
    p=tmp_path/"probe.py"; p.write_text("print(1)\n")
    ok,reason=runner(tmp_path)._allowed_command([sys.executable,"probe.py"],False)
    assert ok is False and reason=="unregistered_python_command"

def test_validation_main_extra_arguments_are_blocked(tmp_path):
    ok,reason=runner(tmp_path)._allowed_command([sys.executable,"-m","validation.main","--foo"],False)
    assert ok is False and reason=="validation_main_argument_not_permitted"

def test_full_remains_milestone_guarded(tmp_path):
    ok,reason=runner(tmp_path)._allowed_command([sys.executable,"-m","validation.main","--full"],False)
    assert ok is False and reason=="full_validation_guarded_until_acee20"

def test_no_test_only_generic_script_bypass_in_runner_source():
    src=(Path(__file__).resolve().parents[1]/"ontology/acee_validation_runner.py").read_text()
    assert "test_only" not in src.lower()
    assert "resolved.relative_to(self.root)" not in src
