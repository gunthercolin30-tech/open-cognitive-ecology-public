#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,tempfile

ROOT=Path.home()/"open-cognitive-ecology"
RUNTIME=ROOT/"ontology"/"p160_normative_decision_sealing.py"
BASE=ROOT/"validation"/"p160g_normative_decision_sealing_v1_test.py"
CROWN=ROOT/"validation"/"p160g_normative_decision_sealing_defensive_crown_v1_test.py"
REPORT=ROOT/"validation"/"p160g_normative_decision_sealing_mutation_crown_v3_report.json"
EXPECTED="12e46324fb8887c94a1f33074e2431177ba5b5ff1b9e2c956ff825097a1a705c"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def die(s):raise SystemExit("ERROR: "+s)
if not all(p.is_file() for p in (RUNTIME,BASE,CROWN)):die("inputs missing")
if sha(RUNTIME)!=EXPECTED:die("runtime G drift")
src=RUNTIME.read_text(encoding="utf-8")

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
results=[]
with tempfile.TemporaryDirectory(prefix="oce-p160g-mut-v3-") as td0:
 td=Path(td0)
 for name,old,new in mutants:
  n=src.count(old)
  if n!=1:
   results.append({"mutant":name,"status":"INCONCLUSIVE","reason":"ANCHOR_COUNT_"+str(n)});continue
  mroot=td/name; pkg=mroot/"ontology"; tests=mroot/"tests"
  pkg.mkdir(parents=True);tests.mkdir(parents=True)
  (pkg/"__init__.py").write_text("",encoding="utf-8")
  mf=pkg/"p160_normative_decision_sealing.py"
  mf.write_text(src.replace(old,new,1),encoding="utf-8")
  shutil.copy2(BASE,tests/"test_baseline.py")
  shutil.copy2(CROWN,tests/"test_defensive.py")
  sentinel=tests/"test_000_import_sentinel.py"
  sentinel.write_text(
   "import os,hashlib\nfrom pathlib import Path\nimport ontology.p160_normative_decision_sealing as m\n"
   "def test_mutant_is_actually_under_test():\n"
   " p=Path(m.__file__).resolve(); s=hashlib.sha256(p.read_bytes()).hexdigest()\n"
   " assert str(p)==os.environ['P160G_EXPECTED_MUTANT_FILE'], (str(p),os.environ['P160G_EXPECTED_MUTANT_FILE'])\n"
   " assert s==os.environ['P160G_EXPECTED_MUTANT_SHA'], (s,os.environ['P160G_EXPECTED_MUTANT_SHA'])\n",
   encoding="utf-8")
  env=os.environ.copy()
  env["PYTHONPATH"]=str(mroot)
  env["P160G_EXPECTED_MUTANT_FILE"]=str(mf.resolve())
  env["P160G_EXPECTED_MUTANT_SHA"]=sha(mf)
  cp=subprocess.run([sys.executable,"-m","pytest","-q","tests"],cwd=str(mroot),env=env,
                    stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
  # If sentinel itself failed, classification is inconclusive, not killed.
  sentinel_failed=("test_mutant_is_actually_under_test" in cp.stdout and "FAILED" in cp.stdout)
  if sentinel_failed:
   status="INCONCLUSIVE"
  else:
   status="KILLED" if cp.returncode!=0 else "SURVIVED"
  results.append({"mutant":name,"status":status,"returncode":cp.returncode,
                  "mutant_file":str(mf.resolve()),"mutant_sha256":sha(mf),
                  "pytest_sentinel":"PASS" if not sentinel_failed else "FAIL",
                  "tail":"\n".join(cp.stdout.splitlines()[-12:])})
  if sha(RUNTIME)!=EXPECTED:die("canonical runtime changed during campaign")
k=sum(r["status"]=="KILLED" for r in results);s=sum(r["status"]=="SURVIVED" for r in results);i=sum(r["status"]=="INCONCLUSIVE" for r in results);t=len(results);score=k/t if t else 0
d={"schema":"oce.p160g.mutation_crown.v3","runtime_sha256":sha(RUNTIME),"mutants_total":t,"killed":k,"survived":s,"inconclusive":i,"mutation_score":score,"results":results,"runtime_unchanged":sha(RUNTIME)==EXPECTED,"pytest_import_sentinel":"PER_MUTANT","authorization_created":False,"authorization_token_created":False,"execution_performed":False,"p160h_opened":False,"p161_opened":False}
REPORT.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
for r in results:print(r["mutant"],r["status"],"PYTEST_IMPORT="+r.get("pytest_sentinel","FAIL"))
print("mutants_total="+str(t));print("killed="+str(k));print("survived="+str(s));print("inconclusive="+str(i));print("mutation_score=%.6f"%score);print("RUNTIME_UNCHANGED="+str(sha(RUNTIME)==EXPECTED).lower())
if s or i or score!=1.0:raise SystemExit(1)
print("P160G_MUTATION_CROWN_V3_OK");print("P160H_OPENED=false");print("P161_OPENED=false")
