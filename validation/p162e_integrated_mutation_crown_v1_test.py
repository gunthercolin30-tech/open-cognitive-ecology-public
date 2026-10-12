import os, subprocess, sys, tempfile
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"ontology/scope_intersection_engine.py"
TESTS=[ROOT/"validation/p162e_integrated_effective_envelope_v1_test.py",ROOT/"validation/p162e_effective_capability_resource_scope_gate_v1_test.py",ROOT/"validation/p162e_defense_crown_v1_test.py",ROOT/"validation/p162e_e10_quantitative_binding_v1_test.py"]
SOURCE=ENGINE.read_text(encoding="utf-8")
MUTATIONS=[
("V7M01_drop_effect_empty_propagation",'elif effect.get("status")=="EFFECT_SCOPE_EMPTY":status="EFFECTIVE_SCOPE_EMPTY"','elif effect.get("status")=="EFFECT_SCOPE_EMPTY":status="EFFECTIVE_SCOPE_CONSTRUCTED"'),
("V7M02_drop_credential_failure_propagation",'elif credential.get("status")=="CREDENTIAL_ATTENUATION_UNAVAILABLE":status="CREDENTIAL_ATTENUATION_UNAVAILABLE"','elif credential.get("status")=="CREDENTIAL_ATTENUATION_UNAVAILABLE":status="EFFECTIVE_SCOPE_CONSTRUCTED"'),
("V7M03_drop_dependency_failure_propagation",'elif depcomp.get("status")=="DEPENDENCY_SCOPE_INSUFFICIENT":status="DEPENDENCY_SCOPE_INSUFFICIENT"','elif depcomp.get("status")=="DEPENDENCY_SCOPE_INSUFFICIENT":status="EFFECTIVE_SCOPE_CONSTRUCTED"'),
("V7M04_drop_composition_conflict_propagation",'elif depcomp.get("status")=="COMPOSITION_SCOPE_CONFLICT":status="COMPOSITION_SCOPE_CONFLICT"','elif depcomp.get("status")=="COMPOSITION_SCOPE_CONFLICT":status="EFFECTIVE_SCOPE_CONSTRUCTED"'),
("V7M05_drop_temporal_empty_propagation",'elif temporal.get("status")=="EFFECTIVE_SCOPE_EMPTY":status="EFFECTIVE_SCOPE_EMPTY"','elif temporal.get("status")=="EFFECTIVE_SCOPE_EMPTY":status="EFFECTIVE_SCOPE_CONSTRUCTED"'),
("V7M06_drop_effect_unknown_detection",'if effect.get("status") in {"EFFECT_SCOPE_UNDETERMINED","EFFECTIVE_SCOPE_UNDETERMINED"}:unknowns.append("effect_scope")','if False:unknowns.append("effect_scope")'),
("V7M07_drop_credential_unknown_detection",'if credential.get("status")=="EFFECTIVE_SCOPE_UNDETERMINED":unknowns.append("credential_scope")','if False:unknowns.append("credential_scope")'),
("V7M08_drop_dependency_unknown_detection",'if depcomp.get("status")=="EFFECTIVE_SCOPE_UNDETERMINED":unknowns.append("dependency_composition_envelope")','if False:unknowns.append("dependency_composition_envelope")'),
("V7M09_drop_temporal_unknown_detection",'if temporal.get("status")=="EFFECTIVE_SCOPE_UNDETERMINED":unknowns.append("temporal_bounds")','if False:unknowns.append("temporal_bounds")'),
("V7M10_credential_reserved_true",'"credential_reserved":False','"credential_reserved":True'),
("V7M11_resource_reserved_true",'"resource_reserved":False','"resource_reserved":True'),
("V7M12_execution_lease_created_true",'"execution_lease_created":False','"execution_lease_created":True'),
("V7M13_p162f_opened_true",'"p162f_opened":False','"p162f_opened":True'),
]
def run_mutation(name,old,new):
 assert SOURCE.count(old)==1, f"{name}: operator target count={SOURCE.count(old)}"
 mutated=SOURCE.replace(old,new,1)
 with tempfile.TemporaryDirectory(prefix="p162e-v8-") as raw:
  td=Path(raw); pkg=td/"ontology"; pkg.mkdir(); val=td/"validation"; val.mkdir()
  (pkg/"__init__.py").write_text("",encoding="utf-8"); (val/"__init__.py").write_text("",encoding="utf-8")
  for f in (ROOT/"ontology").glob("*.py"):
   if ".bak" not in f.name: (pkg/f.name).write_bytes(f.read_bytes())
  (pkg/"scope_intersection_engine.py").write_text(mutated,encoding="utf-8")
  local_tests=[]
  for original in TESTS:
   dest=val/original.name; dest.write_bytes(original.read_bytes()); local_tests.append(dest)
  env=os.environ.copy(); env["PYTHONPATH"]=str(td)
  probe=subprocess.run([sys.executable,"-c","import ontology.scope_intersection_engine as m; print(m.__file__)"],cwd=str(td),env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  expected=str(pkg/"scope_intersection_engine.py")
  assert probe.returncode==0, f"{name}: isolation probe failed\\n{probe.stdout}"
  assert Path(probe.stdout.strip()).resolve()==Path(expected).resolve(), f"{name}: isolation invalid expected={Path(expected).resolve()} actual={Path(probe.stdout.strip()).resolve()}"
  r=subprocess.run([sys.executable,"-m","pytest","-q"]+[str(x) for x in local_tests],cwd=str(td),env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  return r.returncode,r.stdout

@pytest.mark.parametrize("name,old,new",MUTATIONS,ids=[m[0] for m in MUTATIONS])
def test_v7_integration_mutation_is_killed(name,old,new):
 rc,out=run_mutation(name,old,new)
 assert rc!=0, f"{name}: SURVIVED/INVALID\n{out}"
def test_v8_mutation_catalog_is_complete_and_unique():
 assert len(MUTATIONS)==13
 assert len({m[0] for m in MUTATIONS})==13
 assert all(SOURCE.count(old)==1 for _,old,_ in MUTATIONS)
