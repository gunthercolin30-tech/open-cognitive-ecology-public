from pathlib import Path
import pytest,sys
from ontology.acee_validation_runner import AceeValidationRunner
ROOT=Path(__file__).resolve().parents[1]
def test_runner_direct_transport_removed():
 s=(ROOT/"ontology/acee_validation_runner.py").read_text()
 assert "subprocess." not in s and "os.environ.copy()" not in s and "os.killpg" not in s
 assert "run_closed_validation" in s
def test_c7d3_grammar_still_closed(tmp_path):
 r=AceeValidationRunner(root=tmp_path)
 assert r._allowed_command([sys.executable,"-m","validation.main"],False)==(True,"")
 assert r._allowed_command([sys.executable,"-m","validation.main","--full"],True)==(True,"")
 assert r._allowed_command([sys.executable,"-c","print(1)"],False)[0] is False
 assert r._allowed_command([sys.executable,"probe.py"],False)[0] is False
def test_backend_rejects_arbitrary_python():
 from ontology.governed_acee_validation_backend import run_closed_validation
 with pytest.raises(PermissionError): run_closed_validation([sys.executable,"-c","print(1)"],cwd=ROOT,timeout_seconds=5)
def test_backend_rejects_script_path():
 from ontology.governed_acee_validation_backend import run_closed_validation
 with pytest.raises(PermissionError): run_closed_validation([sys.executable,"probe.py"],cwd=ROOT,timeout_seconds=5)
def test_backend_transport_bounds():
 s=(ROOT/"ontology/governed_acee_validation_backend.py").read_text()
 assert "shell=False" in s and "start_new_session=True" in s and "close_fds=True" in s
 assert "os.killpg" in s and "SIGTERM" in s and "SIGKILL" in s and "os.environ.copy()" not in s
def test_backup_exists():
 assert (ROOT/"ontology/acee_validation_runner.py.bak.p162g65c10c").is_file()
