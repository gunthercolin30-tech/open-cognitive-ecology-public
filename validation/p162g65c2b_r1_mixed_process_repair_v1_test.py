from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
def test_split_or_bounded_progression():
 s=(ROOT/"ontology/baseline_integrity.py").read_text()
 assert "governed_git_exact_process import governed_git_subprocess as subprocess" in s
 r1_state="import subprocess as _system_subprocess" in s
 c5_state="governed_bounded_python_process import pip_freeze" in s
 assert r1_state ^ c5_state
 if r1_state:
  assert "freeze = _system_subprocess.run(" in s
 if c5_state:
  assert "freeze_result = pip_freeze(" in s
  assert "_system_subprocess" not in s

def test_allowed():
 from ontology.governed_git_exact_process import _bounded
 for a in [["git","branch","--show-current"],["git","rev-parse","HEAD"],["git","tag","--points-at","HEAD"],["git","ls-files"],["git","ls-files","--others","--exclude-standard"],["git","diff","--name-only"],["git","diff","--cached","--name-only"]]: assert _bounded(a)==a
def test_denied():
 from ontology.governed_git_exact_process import _bounded
 for a in [["git","branch","new"],["git","tag","v1"],["git","remote","add","x","y"],["git","push"],["git","commit"],["git","checkout","x"]]:
  with pytest.raises(PermissionError): _bounded(a)
def test_pip_path_progression(monkeypatch):
 import ontology.baseline_integrity as mod
 src=(ROOT/"ontology/baseline_integrity.py").read_text()
 if hasattr(mod,"_system_subprocess"):
  class R: returncode=0; stdout="x==1\n"; stderr=""
  seen={}
  def fake(args,**kw): seen["args"]=args; return R()
  monkeypatch.setattr(mod._system_subprocess,"run",fake)
  d=mod._dependency_fingerprint()
  assert seen["args"][1:]==["-m","pip","freeze"]
  assert d["package_count"]==1
 else:
  assert "governed_bounded_python_process import pip_freeze" in src
  seen={}
  def fake(*,cwd,timeout_seconds=60):
   seen["cwd"]=cwd
   return {"returncode":0,"stdout":b"x==1\n","stderr":b"","status":"EFFECT_CONFIRMED"}
  monkeypatch.setattr(mod,"pip_freeze",fake)
  d=mod._dependency_fingerprint()
  assert seen["cwd"]==ROOT
  assert d["package_count"]==1
