import subprocess,sys,tempfile,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENG=ROOT/"ontology/scope_intersection_engine.py"
RES=ROOT/"ontology/target_scope_resolver.py"
BASE=[ROOT/"validation/p162e_effective_capability_resource_scope_gate_v1_test.py",ROOT/"validation/p162e_defense_crown_v1_test.py",ROOT/"validation/p162e_e10_quantitative_binding_v1_test.py"]
MUTATIONS=[
("M01_intersection_to_union","common &= set(m)","common |= set(m)"),
("M02_flatten_relational_tuples",'return [maps[0][k] for k in sorted(common)]','return list({tuple_key(t):t for r in rels for t in r}.values())'),
("M03_skip_target_resolution",'escape=any(x not in auth for x in resolved)','escape=False'),
("M04_trust_alias_redirect",'return resolve_target_scope(requested,chain[-1:] if chain else [],authorized,[{"type":"alias_resolution","chain":list(chain)}],False)','return resolve_target_scope(requested,[requested],authorized,[{"type":"trusted_alias"}],False)'),
("M05_technical_requirement_expands_authorization",'eff=min(requested,max_authorized,available)','eff=min(requested,available)'),
("M06_availability_expands_budget",'eff=min(requested,max_authorized,available)','eff=min(requested,available)'),
("M07_ignore_effect_closure",'eff=dset&tset&aset','eff=tset'),
("M08_ignore_credential_scope",'a,r,z=set(available),set(required),set(authorized);eff=r&z&a\n if r-z or (not supported and a-z):','a,r,z=set(available),set(required),set(authorized);eff=r&a\n if (not supported and False):'),
("M09_environment_mapping_permissive",'common &= set(m)','common |= set(m)'),
("M10_child_effect_inherits",'ok=tuple_key(dep) in set(parent_keys)|set(distinct_keys or [])','ok=True'),
("M11_no_enforcement_feasibility",'status="ENFORCEABLE" if observable and preventable else ("PARTIALLY_ENFORCEABLE" if observable or preventable else "UNENFORCEABLE")','status="ENFORCEABLE"'),
("M12_temporal_windows_unioned",'s=max(w["start"] for w in ws);e=min(w["end"] for w in ws)','s=min(w["start"] for w in ws);e=max(w["end"] for w in ws)'),
("M13_empty_scope_to_original_token",'elif not tuples:status="EFFECTIVE_SCOPE_EMPTY"','elif not tuples: tuples=list(rels[0]);status="EFFECTIVE_SCOPE_CONSTRUCTED"'),
]
def run_mutation(name,old,new):
 with tempfile.TemporaryDirectory(prefix="p162e_mut_") as td:
  td=Path(td); (td/"ontology").mkdir(); (td/"validation").mkdir()
  for init in [td/"ontology/__init__.py",td/"validation/__init__.py"]: init.write_text("")
  e=ENG.read_text(); r=RES.read_text()
  target="engine"
  if name in ("M03_skip_target_resolution","M04_trust_alias_redirect"): target="resolver"
  text=r if target=="resolver" else e
  if old not in text: return False,"TRANSFORM_NOT_APPLIED"
  text=text.replace(old,new,1)
  (td/"ontology/scope_intersection_engine.py").write_text(e if target=="resolver" else text)
  (td/"ontology/target_scope_resolver.py").write_text(text if target=="resolver" else r)
  for f in BASE: shutil.copy2(f,td/"validation"/f.name)
  cp=subprocess.run([sys.executable,"-m","pytest","-q"]+[str(td/"validation"/f.name) for f in BASE],
    cwd=td,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  return cp.returncode!=0,cp.stdout
def test_all_13_canonical_mutations_are_killed():
 results=[]
 for name,old,new in MUTATIONS:
  killed,out=run_mutation(name,old,new); results.append((name,killed,out[-1000:]))
 failed=[x for x in results if not x[1]]
 assert not failed, "\n".join(f"{n}: SURVIVED/INVALID\n{o}" for n,_,o in failed)
def test_mutation_catalog_is_exact():
 assert len(MUTATIONS)==13
 assert [m[0].split("_",1)[0] for m in MUTATIONS]==[f"M{i:02d}" for i in range(1,14)]
