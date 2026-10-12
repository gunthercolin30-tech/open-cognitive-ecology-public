#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile
ROOT=Path.home()/"open-cognitive-ecology"
R=ROOT/"ontology"/"p160_normative_decision_sealing.py"
BASE=ROOT/"validation"/"p160g_normative_decision_sealing_v1_test.py"
DEF=ROOT/"validation"/"p160g_normative_decision_sealing_defensive_crown_v1_test.py"
SURV=ROOT/"validation"/"p160g_normative_decision_sealing_mutation_survivor_killers_v1_test.py"
REPORT=ROOT/"validation"/"p160g_normative_decision_sealing_mutation_crown_consolidated_v1_report.json"
E="12e46324fb8887c94a1f33074e2431177ba5b5ff1b9e2c956ff825097a1a705c"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if not all(p.is_file() for p in (R,BASE,DEF,SURV)):raise SystemExit("ERROR: required input missing")
if sha(R)!=E:raise SystemExit("ERROR: runtime G drift")
src=R.read_text(encoding="utf-8")
mutants=[
("M01_BINDING_FAIL_OPEN",'return "UNDETERMINED",["CROSS_BINDING_NOT_PROVEN"]','return "ELIGIBLE_CANDIDATE",["MUTANT_BINDING_FAIL_OPEN"]'),
("M02_CONSTITUTIVE_UNKNOWN_POSITIVE",'return "UNDETERMINED",["CONSTITUTIVE_UNDETERMINED"]','return "ELIGIBLE_CANDIDATE",["MUTANT_CONSTITUTIVE_UNKNOWN"]'),
("M03_AUTHORITY_UNKNOWN_POSITIVE",'return "UNDETERMINED",["AUTHORITY_UNDETERMINED"]','return "ELIGIBLE_CANDIDATE",["MUTANT_AUTHORITY_UNKNOWN"]'),
("M04_HUMAN_ABSENCE_SUCCESS",'return "ESCALATION_REQUIRED",["AUTHORITY_"+str(auth)]','return "ELIGIBLE_CANDIDATE",["MUTANT_HUMAN_ABSENCE"]'),
("M05_DROP_BC_CHAIN",'errors.append("UPSTREAM_HASH_MISMATCH:C:B")','pass # MUTANT_DROP_BC'),
("M06_DROP_CD_CHAIN",'errors.append("UPSTREAM_HASH_MISMATCH:D:C")','pass # MUTANT_DROP_CD'),
("M07_DROP_BD_CHAIN",'errors.append("UPSTREAM_HASH_MISMATCH:D:B")','pass # MUTANT_DROP_BD'),
("M08_INCOMPLETE_ACTION_POSITIVE",'elig="UNDETERMINED"; reasons.append("ACTION_DIGEST_INCOMPLETE")','elig="ELIGIBLE_CANDIDATE"; reasons.append("MUTANT_ACTION_INCOMPLETE")'),
("M09_INCOMPLETE_PROVENANCE_POSITIVE",'elig="UNDETERMINED"; reasons.append("UPSTREAM_PROVENANCE_INCOMPLETE")','elig="ELIGIBLE_CANDIDATE"; reasons.append("MUTANT_PROVENANCE_INCOMPLETE")'),
("M10_SCOPE_UNION_RULE",'"scope_merge_rule":"INTERSECTION_NEVER_UNION"','"scope_merge_rule":"UNION"'),
("M11_PURPOSE_UNION_RULE",'"purpose_merge_rule":"INTERSECTION_NEVER_UNION"','"purpose_merge_rule":"UNION"'),
("M12_AUTHORIZATION_TRUE",'"authorization_created":False','"authorization_created":True'),
("M13_TOKEN_TRUE",'"authorization_token_created":False','"authorization_token_created":True'),
("M14_EXECUTION_TRUE",'"execution_performed":False','"execution_performed":True'),
("M15_P161_TRUE",'"p161_opened":False','"p161_opened":True'),
("M16_ACCEPT_NOT_SEALED",'life=x.get("lifecycle")=="SEALED" and x.get("transaction_state")=="COMMITTED"','life=x.get("transaction_state")=="COMMITTED"'),
("M17_ACCEPT_NOT_COMMITTED",'life=x.get("lifecycle")=="SEALED" and x.get("transaction_state")=="COMMITTED"','life=x.get("lifecycle")=="SEALED"'),
("M18_IGNORE_ARTIFACT_HASH",'artok=art==canonical_sha256(x)','artok=True'),
("M19_IGNORE_SEAL_BINDING",'semok=sem==seal.get("semantic_hash")','semok=True'),
]
res=[]
with tempfile.TemporaryDirectory(prefix="oce-p160g-mut-final-") as td0:
 td=Path(td0)
 for name,old,new in mutants:
  if src.count(old)!=1:
   res.append({"mutant":name,"status":"INCONCLUSIVE","reason":"ANCHOR_COUNT_"+str(src.count(old))});continue
  mr=td/name;(mr/"ontology").mkdir(parents=True);(mr/"tests").mkdir()
  (mr/"ontology"/"__init__.py").write_text("",encoding="utf-8")
  mf=mr/"ontology"/"p160_normative_decision_sealing.py";mf.write_text(src.replace(old,new,1),encoding="utf-8")
  shutil.copy2(BASE,mr/"tests"/"test_baseline.py");shutil.copy2(DEF,mr/"tests"/"test_defensive.py");shutil.copy2(SURV,mr/"tests"/"test_discriminants.py")
  (mr/"tests"/"test_000_import_sentinel.py").write_text(
   "import os,hashlib\nfrom pathlib import Path\nimport ontology.p160_normative_decision_sealing as m\n"
   "def test_mutant_import():\n p=Path(m.__file__).resolve();assert str(p)==os.environ['MF'];assert hashlib.sha256(p.read_bytes()).hexdigest()==os.environ['MS']\n",encoding="utf-8")
  env=os.environ.copy();env["PYTHONPATH"]=str(mr);env["MF"]=str(mf.resolve());env["MS"]=sha(mf)
  cp=subprocess.run([sys.executable,"-m","pytest","-q","tests"],cwd=str(mr),env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
  sentfail=("test_mutant_import" in cp.stdout and "FAILED" in cp.stdout)
  status="INCONCLUSIVE" if sentfail else ("KILLED" if cp.returncode else "SURVIVED")
  res.append({"mutant":name,"status":status,"pytest_import":"FAIL" if sentfail else "PASS","returncode":cp.returncode,"mutant_sha256":sha(mf),"tail":"\n".join(cp.stdout.splitlines()[-10:])})
  if sha(R)!=E:raise SystemExit("ERROR: canonical runtime changed")
k=sum(x["status"]=="KILLED" for x in res);s=sum(x["status"]=="SURVIVED" for x in res);i=sum(x["status"]=="INCONCLUSIVE" for x in res);score=k/19
d={"schema":"oce.p160g.mutation_crown.consolidated.v1","runtime_sha256":sha(R),"mutants_total":19,"killed":k,"survived":s,"inconclusive":i,"mutation_score":score,"results":res,"runtime_unchanged":sha(R)==E,"pytest_import_sentinel":"PER_MUTANT","test_basis":{"baseline_sha256":sha(BASE),"defensive_sha256":sha(DEF),"discriminants_sha256":sha(SURV)},"authorization_created":False,"authorization_token_created":False,"execution_performed":False,"p160h_opened":False,"p161_opened":False}
REPORT.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
for x in res:print(x["mutant"],x["status"],"PYTEST_IMPORT="+x.get("pytest_import","FAIL"))
print("mutants_total=19");print("killed="+str(k));print("survived="+str(s));print("inconclusive="+str(i));print("mutation_score=%.6f"%score);print("RUNTIME_UNCHANGED="+str(sha(R)==E).lower())
if k!=19 or s or i:raise SystemExit(1)
print("P160G_MUTATION_CROWN_CONSOLIDATED_OK");print("P160H_OPENED=false");print("P161_OPENED=false")
