from pathlib import Path
import importlib.util,json
R=Path(__file__).resolve().parents[1]; M=R/'ontology/occ1h_a050_role_rename_laundering_semantics.py'; A=R/'validation_artifacts/p159/occ1h/a050/a050_rrpf_role_rename_laundering_projection_v1.json'
def load():
 s=importlib.util.spec_from_file_location('a050t',M);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def base(): return {'stable_role_id':'r1','role_label':'reviewer','authority':['REVIEW'],'authority_provenance':'gov-v1'}
def test_laundering_resisted():
 m=load(); x=m.evaluate_role_transition(base(),{'stable_role_id':'r1','role_label':'admin','authority':['REVIEW','CONSTITUTIONAL_CHANGE'],'authority_provenance':'gov-v1'}); assert x['verdict']=='RESISTED'
def test_legitimate_rename_control():
 m=load(); x=m.evaluate_role_transition(base(),{'stable_role_id':'r1','role_label':'senior reviewer','authority':['REVIEW'],'authority_provenance':'gov-v1'}); assert x['verdict']=='ADMISSIBLE_CONTROL'
def test_degradation_fail_closed():
 m=load(); x=m.evaluate_role_transition(base(),{'stable_role_id':'r1','role_label':'admin','authority':['REVIEW'],'authority_provenance':''}); assert x['verdict']=='UNRESOLVED'
def test_rrp22_and_boundaries():
 x=json.loads(A.read_text()); assert x['RRP21']['status']=='COMPLETE'; assert x['RRP22']['status']=='INDEPENDENT_REQUALIFICATION_REQUIRED'; assert x['boundaries']=={'occ1h_closed':False,'p159_final_lock':False,'p160_opened':False}
