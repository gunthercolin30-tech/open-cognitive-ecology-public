from pathlib import Path
import importlib.util, json, subprocess, sys
R=Path(__file__).resolve().parents[1]
M=R/"ontology/occ1h_a049_purpose_laundering_semantics.py"
A=R/"validation_artifacts/p159/occ1h/a049/a049_rrpf_purpose_laundering_projection_v1.json"
def load():
 s=importlib.util.spec_from_file_location("a049_sem",M); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def test_functional_and_degraded_controls():
 m=load()
 ok=[{"governed_purpose":"research","provenance":"gov:p1","individually_admissible":True},{"governed_purpose":"research","provenance":"gov:p2","individually_admissible":True}]
 assert m.classify(ok,"research")["status"]=="ADMISSIBLE_CONTROL"
 assert m.classify(ok,"unauthorized_aggregate")["status"]=="RESISTED"
 bad=[{"governed_purpose":"research","provenance":"","individually_admissible":True}]
 assert m.classify(bad,"unauthorized_aggregate")["status"]=="UNRESOLVED"
def test_two_fresh_interpreters_identical():
 code=("import importlib.util,json; p="+repr(str(M))+"; s=importlib.util.spec_from_file_location('x',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);a=[{'governed_purpose':'research','provenance':'gov:p1','individually_admissible':True},{'governed_purpose':'analysis','provenance':'gov:p2','individually_admissible':True}];print(json.dumps(m.classify(a,'unauthorized_aggregate'),sort_keys=True))")
 a=subprocess.check_output([sys.executable,"-c",code],text=True).strip()
 b=subprocess.check_output([sys.executable,"-c",code],text=True).strip()
 assert a==b and json.loads(a)["status"]=="RESISTED"
def test_independent_requalification_contract():
 x=json.loads(A.read_text()); assert x["RRP21"]["status"]=="COMPLETE"; assert x["RRP22"]["status"]=="INDEPENDENT_REQUALIFICATION_REQUIRED"; assert x["RRP22"]["self_certification_forbidden"] is True; assert x["candidate_verdict"]=="RESISTED"
def test_no_authority_or_closure_expansion():
 m=load(); x=json.loads(A.read_text()); assert m.RUNTIME_AUTHORITY_GRANTED is False; assert x["boundaries"]=={"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False}
