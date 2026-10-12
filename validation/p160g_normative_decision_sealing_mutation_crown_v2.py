#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib, json, os, subprocess, sys, tempfile

ROOT=Path.home()/"open-cognitive-ecology"
RUNTIME=ROOT/"ontology"/"p160_normative_decision_sealing.py"
EXPECTED="12e46324fb8887c94a1f33074e2431177ba5b5ff1b9e2c956ff825097a1a705c"
BASE=ROOT/"validation"/"p160g_normative_decision_sealing_v1_test.py"
CROWN=ROOT/"validation"/"p160g_normative_decision_sealing_defensive_crown_v1_test.py"
REPORT=ROOT/"validation"/"p160g_normative_decision_sealing_mutation_crown_v2_report.json"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def die(s): raise SystemExit("ERROR: "+s)
if not RUNTIME.is_file() or sha(RUNTIME)!=EXPECTED: die("runtime G absent ou dérivé")
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
with tempfile.TemporaryDirectory(prefix="oce-p160g-mut-v2-") as td0:
    td=Path(td0)
    for name,old,new in mutants:
        count=src.count(old)
        if count!=1:
            results.append({"mutant":name,"status":"INCONCLUSIVE","reason":"ANCHOR_COUNT_"+str(count)})
            continue
        msrc=src.replace(old,new,1)
        mroot=td/name
        pkg=mroot/"ontology"
        pkg.mkdir(parents=True)
        (pkg/"__init__.py").write_text("",encoding="utf-8")
        mutant_file=pkg/"p160_normative_decision_sealing.py"
        mutant_file.write_text(msrc,encoding="utf-8")
        marker=hashlib.sha256(msrc.encode("utf-8")).hexdigest()

        env=os.environ.copy()
        env["PYTHONPATH"]=str(mroot)+os.pathsep+str(ROOT)
        env["P160G_EXPECTED_MUTANT_FILE"]=str(mutant_file.resolve())
        env["P160G_EXPECTED_MUTANT_SHA"]=marker

        # Critical v2 fix: run outside ROOT so sys.path[0] cannot shadow PYTHONPATH.
        probe='import os,hashlib; import ontology.p160_normative_decision_sealing as m; from pathlib import Path; p=Path(m.__file__).resolve(); s=hashlib.sha256(p.read_bytes()).hexdigest(); print(str(p)); print(s); assert str(p)==os.environ["P160G_EXPECTED_MUTANT_FILE"]; assert s==os.environ["P160G_EXPECTED_MUTANT_SHA"]'
        pr=subprocess.run([sys.executable,"-c",probe],cwd=str(mroot),env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=20)
        if pr.returncode!=0:
            results.append({"mutant":name,"status":"INCONCLUSIVE","reason":"MUTANT_IMPORT_PROBE_FAILED","probe":pr.stdout[-2000:]})
            continue

        cp=subprocess.run([sys.executable,"-m","pytest","-q",str(BASE),str(CROWN)],
                          cwd=str(mroot),env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
        status="KILLED" if cp.returncode!=0 else "SURVIVED"
        results.append({"mutant":name,"status":status,"returncode":cp.returncode,
                        "mutant_file":str(mutant_file.resolve()),"mutant_sha256":marker,
                        "import_probe":"PASS","tail":"\n".join(cp.stdout.splitlines()[-10:])})
        if sha(RUNTIME)!=EXPECTED: die("canonical runtime changed during mutation campaign")

killed=sum(r["status"]=="KILLED" for r in results)
survived=sum(r["status"]=="SURVIVED" for r in results)
inconclusive=sum(r["status"]=="INCONCLUSIVE" for r in results)
total=len(results)
score=killed/total if total else 0.0
report={"schema":"oce.p160g.mutation_crown.v2","runtime_sha256":sha(RUNTIME),
        "mutants_total":total,"killed":killed,"survived":survived,"inconclusive":inconclusive,
        "mutation_score":score,"results":results,"runtime_unchanged":sha(RUNTIME)==EXPECTED,
        "harness_import_isolation":"PROBED_PER_MUTANT",
        "authorization_created":False,"authorization_token_created":False,
        "execution_performed":False,"p160h_opened":False,"p161_opened":False}
REPORT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
for r in results: print(r["mutant"],r["status"],"IMPORT="+r.get("import_probe","FAIL"))
print("mutants_total="+str(total)); print("killed="+str(killed)); print("survived="+str(survived)); print("inconclusive="+str(inconclusive)); print("mutation_score=%.6f"%score)
print("RUNTIME_UNCHANGED="+str(sha(RUNTIME)==EXPECTED).lower())
if survived or inconclusive or score!=1.0: raise SystemExit(1)
print("P160G_MUTATION_CROWN_V2_OK")
print("AUTHORIZATION_CREATED=false"); print("AUTHORIZATION_TOKEN_CREATED=false"); print("EXECUTION_PERFORMED=false"); print("P160H_OPENED=false"); print("P161_OPENED=false")
