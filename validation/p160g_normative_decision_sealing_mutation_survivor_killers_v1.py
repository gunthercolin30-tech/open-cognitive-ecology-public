#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile
ROOT=Path.home()/"open-cognitive-ecology"
R=ROOT/"ontology"/"p160_normative_decision_sealing.py"
BASE=ROOT/"validation"/"p160g_normative_decision_sealing_v1_test.py"
DEF=ROOT/"validation"/"p160g_normative_decision_sealing_defensive_crown_v1_test.py"
SURV=ROOT/"validation"/"p160g_normative_decision_sealing_mutation_survivor_killers_v1_test.py"
REPORT=ROOT/"validation"/"p160g_normative_decision_sealing_mutation_survivor_killers_v1_report.json"
E="12e46324fb8887c94a1f33074e2431177ba5b5ff1b9e2c956ff825097a1a705c"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if sha(R)!=E:raise SystemExit("ERROR: runtime G drift")
src=R.read_text()
mutants=[
("M16_ACCEPT_NOT_SEALED",'life=x.get("lifecycle")=="SEALED" and x.get("transaction_state")=="COMMITTED"','life=x.get("transaction_state")=="COMMITTED"'),
("M17_ACCEPT_NOT_COMMITTED",'life=x.get("lifecycle")=="SEALED" and x.get("transaction_state")=="COMMITTED"','life=x.get("lifecycle")=="SEALED"'),
("M19_IGNORE_SEAL_BINDING",'semok=sem==seal.get("semantic_hash")','semok=True'),
]
res=[]
with tempfile.TemporaryDirectory(prefix="oce-p160g-survivors-") as td0:
 td=Path(td0)
 for name,old,new in mutants:
  if src.count(old)!=1:
   res.append({"mutant":name,"status":"INCONCLUSIVE","reason":"ANCHOR_COUNT"});continue
  mr=td/name;(mr/"ontology").mkdir(parents=True);(mr/"tests").mkdir()
  (mr/"ontology"/"__init__.py").write_text("")
  mf=mr/"ontology"/"p160_normative_decision_sealing.py";mf.write_text(src.replace(old,new,1))
  shutil.copy2(BASE,mr/"tests"/"test_baseline.py")
  shutil.copy2(DEF,mr/"tests"/"test_defensive.py")
  shutil.copy2(SURV,mr/"tests"/"test_survivors.py")
  sentinel=mr/"tests"/"test_000_import_sentinel.py"
  sentinel.write_text("import os,hashlib\nfrom pathlib import Path\nimport ontology.p160_normative_decision_sealing as m\ndef test_mutant_import():\n p=Path(m.__file__).resolve();assert str(p)==os.environ['MF'];assert hashlib.sha256(p.read_bytes()).hexdigest()==os.environ['MS']\n")
  env=os.environ.copy();env["PYTHONPATH"]=str(mr);env["MF"]=str(mf.resolve());env["MS"]=sha(mf)
  cp=subprocess.run([sys.executable,"-m","pytest","-q","tests"],cwd=str(mr),env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
  sentfail=("test_mutant_import" in cp.stdout and "FAILED" in cp.stdout)
  status="INCONCLUSIVE" if sentfail else ("KILLED" if cp.returncode else "SURVIVED")
  res.append({"mutant":name,"status":status,"pytest_import":"FAIL" if sentfail else "PASS","tail":"\n".join(cp.stdout.splitlines()[-10:])})
  if sha(R)!=E:raise SystemExit("ERROR: canonical runtime changed")
k=sum(x["status"]=="KILLED" for x in res);s=sum(x["status"]=="SURVIVED" for x in res);i=sum(x["status"]=="INCONCLUSIVE" for x in res)
d={"schema":"oce.p160g.mutation_survivor_killers.v1","runtime_sha256":sha(R),"mutants_total":3,"killed":k,"survived":s,"inconclusive":i,"mutation_score":k/3,"results":res,"runtime_unchanged":sha(R)==E,"p160h_opened":False,"p161_opened":False}
REPORT.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
for x in res:print(x["mutant"],x["status"],"PYTEST_IMPORT="+x.get("pytest_import","FAIL"))
print("mutants_total=3");print("killed="+str(k));print("survived="+str(s));print("inconclusive="+str(i));print("mutation_score=%.6f"%(k/3));print("RUNTIME_UNCHANGED="+str(sha(R)==E).lower())
if k!=3 or s or i:raise SystemExit(1)
print("P160G_MUTATION_SURVIVOR_KILLERS_OK");print("P160H_OPENED=false");print("P161_OPENED=false")
