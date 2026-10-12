from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
def test_migrated_sources():
 b=(ROOT/"ontology/baseline_integrity.py").read_text()
 assert "_system_subprocess" not in b and '"pip", "freeze"' not in b
 for n in ("linux_node_deployment_validation.py","raspberry_pi_deployment_validation.py"):
  s=(ROOT/"ontology"/n).read_text()
  assert "import subprocess" not in s and '"validation.main"' not in s
  assert "validation_main(" in s
def test_not_general_runner():
 import ontology.governed_bounded_python_process as g
 assert set(g._ALLOWED)=={"PIP_FREEZE","VALIDATION_MAIN"}
 with pytest.raises(PermissionError): g.run_bounded_python("ARBITRARY_SCRIPT",cwd=ROOT,timeout_seconds=1)
def test_exact_profiles(monkeypatch):
 import ontology.governed_bounded_python_process as g
 seen=[]
 class E:
  @staticmethod
  def canonical_target(x): return "process://"+x
  def __init__(self,**kw): pass
  def execute(self,*,request,handle,adapter_id):
   seen.append(request.argv); return {"status":"EFFECT_CONFIRMED","returncode":0,"stdout":b"","stderr":b""}
 monkeypatch.setattr(g,"GovernedProcessEffector",E)
 g.pip_freeze(cwd=ROOT); g.validation_main(cwd=ROOT)
 assert seen==[("python-current","-m","pip","freeze"),("python-current","-m","validation.main")]
def test_single_transport_boundary():
 assert "subprocess.run" not in (ROOT/"ontology/governed_bounded_python_process.py").read_text()
 assert (ROOT/"ontology/governed_process_effector.py").read_text().count("subprocess.run(")==1
