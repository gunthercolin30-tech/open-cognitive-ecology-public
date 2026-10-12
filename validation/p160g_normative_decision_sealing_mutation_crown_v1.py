#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys, tempfile

ROOT=Path.home()/"open-cognitive-ecology"
RUNTIME=ROOT/"ontology"/"p160_normative_decision_sealing.py"
EXPECTED="12e46324fb8887c94a1f33074e2431177ba5b5ff1b9e2c956ff825097a1a705c"
BASE=ROOT/"validation"/"p160g_normative_decision_sealing_v1_test.py"
CROWN=ROOT/"validation"/"p160g_normative_decision_sealing_defensive_crown_v1_test.py"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def die(s): raise SystemExit("ERROR: "+s)
if sha(RUNTIME)!=EXPECTED: die("runtime G drift before mutation campaign")
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
with tempfile.TemporaryDirectory(prefix="oce-p160g-mut-") as td:
    td=Path(td)
    for name,old,new in mutants:
        if src.count(old)!=1:
            results.append({"mutant":name,"status":"INCONCLUSIVE","reason":"ANCHOR_COUNT_"+str(src.count(old))})
            continue
        msrc=src.replace(old,new,1)
        mroot=td/name
        (mroot/"ontology").mkdir(parents=True)
        (mroot/"ontology"/"__init__.py").write_text("",encoding="utf-8")
        (mroot/"ontology"/"p160_normative_decision_sealing.py").write_text(msrc,encoding="utf-8")
        env=os.environ.copy()
        env["PYTHONPATH"]=str(mroot)+os.pathsep+str(ROOT)
        cmd=[sys.executable,"-m","pytest","-q",str(BASE),str(CROWN)]
        cp=subprocess.run(cmd,cwd=str(ROOT),env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
        status="KILLED" if cp.returncode!=0 else "SURVIVED"
        results.append({"mutant":name,"status":status,"returncode":cp.returncode,"tail":"\n".join(cp.stdout.splitlines()[-8:])})
        if sha(RUNTIME)!=EXPECTED: die("canonical runtime changed during mutation campaign")

killed=sum(r["status"]=="KILLED" for r in results)
survived=sum(r["status"]=="SURVIVED" for r in results)
inconclusive=sum(r["status"]=="INCONCLUSIVE" for r in results)
total=len(results)
score=(killed/total) if total else 0.0
report={"schema":"oce.p160g.mutation_crown.v1","runtime_sha256":sha(RUNTIME),"mutants_total":total,"killed":killed,"survived":survived,"inconclusive":inconclusive,"mutation_score":score,"results":results,"runtime_unchanged":sha(RUNTIME)==EXPECTED,"authorization_created":False,"authorization_token_created":False,"execution_performed":False,"p160h_opened":False,"p161_opened":False}
report_path=ROOT/"validation"/"p160g_normative_decision_sealing_mutation_crown_v1_report.json"
report_path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
for r in results: print(r["mutant"],r["status"])
print("mutants_total="+str(total)); print("killed="+str(killed)); print("survived="+str(survived)); print("inconclusive="+str(inconclusive)); print("mutation_score=%.6f"%score)
print("RUNTIME_UNCHANGED="+str(sha(RUNTIME)==EXPECTED).lower())
if survived or inconclusive or score!=1.0: raise SystemExit(1)
print("P160G_MUTATION_CROWN_OK")
print("AUTHORIZATION_CREATED=false"); print("AUTHORIZATION_TOKEN_CREATED=false"); print("EXECUTION_PERFORMED=false"); print("P160H_OPENED=false"); print("P161_OPENED=false")
