from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys, tempfile

ROOT=Path.home()/"open-cognitive-ecology"
R=ROOT/"ontology/p160_authority_requirements_resolution.py"
EXPECTED="6c9959a1e413af550e61b82e71e16cb684bf92a07f5b6fe784e3579beb86c60c"
def sh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sh(R)!=EXPECTED: raise SystemExit("P160F_MUTATION_V2_PRECONDITION_HASH_MISMATCH")
base=R.read_text(encoding="utf-8")

# Anchors are derived from the exact v1.1 runtime. Each replacement must occur exactly once.
mutants=[
("M01_DUPLICATE_QUORUM",'if len(ids)!=len(set(ids)):','if False and len(ids)!=len(set(ids)):'),
("M02_PROVENANCE_BYPASS",'if h.get("status","UNKNOWN")=="ACTIVE" and not _p160f_provenance_complete(h.get("provenance")):','if False and h.get("status","UNKNOWN")=="ACTIVE" and not _p160f_provenance_complete(h.get("provenance")):'),
("M03_SNAPSHOT_BINDING",'if r.get("constitutional_snapshot_hash") and supplied_snapshot and r.get("constitutional_snapshot_hash")!=supplied_snapshot:','if False and r.get("constitutional_snapshot_hash") and supplied_snapshot and r.get("constitutional_snapshot_hash")!=supplied_snapshot:'),
("M04_PROFILE_BINDING",'if r.get("compiled_profile_hash") and supplied_profile and r.get("compiled_profile_hash")!=supplied_profile:','if False and r.get("compiled_profile_hash") and supplied_profile and r.get("compiled_profile_hash")!=supplied_profile:'),
("M05_CCAD_HASH",'if not _present(e.get("resolution_hash")):','if False and not _present(e.get("resolution_hash")):'),
("M06_AUTH_FINGERPRINT",'if not _present(a.get("authority_context_fingerprint")):','if False and not _present(a.get("authority_context_fingerprint")):'),
("M07_EXPIRY",'if ex is not None and now>=ex:','if False and ex is not None and now>=ex:'),
("M08_ESCALATION_PREEXISTING",'if esc.get("preexisting") is not True:','if False and esc.get("preexisting") is not True:'),
("M09_ESCALATION_EXPANSION",'if esc.get("from_class") and esc.get("to_class") and esc.get("from_class")!=esc.get("to_class"):','if False and esc.get("from_class") and esc.get("to_class") and esc.get("from_class")!=esc.get("to_class"):'),
("M10_REVOKED",'if h.get("revoked") is True: return False, "REVOKED"','if h.get("revoked") is True: pass'),
("M11_EXPIRED_HOLDER",'if h.get("expired") is True: return False, "EXPIRED"','if h.get("expired") is True: pass'),
("M12_ENVIRONMENT",'if h.get("environment") != environment: return False, "INVALID"','if False and h.get("environment") != environment: return False, "INVALID"'),
("M13_SOD",'if _sod_unsatisfied(candidates, sod):','if False and _sod_unsatisfied(candidates, sod):'),
("M14_BREAK_GLASS_DNA",'if bg.get("dna_override") is True: return _fail("INVALID",rid,bindings,["BREAK_GLASS_DNA_OVERRIDE_FORBIDDEN"])','if False and bg.get("dna_override") is True: return _fail("INVALID",rid,bindings,["BREAK_GLASS_DNA_OVERRIDE_FORBIDDEN"])'),
("M15_HUMAN_AI_FALLBACK",'if human_reserved and h.get("kind") != "HUMAN": return False, "HUMAN_RESERVED_UNAVAILABLE"','if human_reserved and h.get("kind") != "HUMAN": pass'),
("M16_SEQUENTIAL_MISSING_ROLE",'if not eligible:\n                return _fail("QUORUM_UNSATISFIED",rid,bindings,["SEQUENTIAL_APPROVAL_ROLE_MISSING",role])','if False and not eligible:\n                return _fail("QUORUM_UNSATISFIED",rid,bindings,["SEQUENTIAL_APPROVAL_ROLE_MISSING",role])'),
("M17_REVIEW_APPEAL",'if not eligible:\n                return _fail("UNAVAILABLE",rid,bindings,[label+"_AUTHORITY_UNAVAILABLE"])','if False and not eligible:\n                return _fail("UNAVAILABLE",rid,bindings,[label+"_AUTHORITY_UNAVAILABLE"])')
]

results=[]
with tempfile.TemporaryDirectory(prefix="p160f-mf2-") as td:
    td=Path(td)
    for mid,old,new in mutants:
        count=base.count(old)
        if count!=1:
            results.append({"id":mid,"status":"INCONCLUSIVE","reason":"anchor_count","count":count})
            continue
        d=td/mid
        (d/"ontology").mkdir(parents=True); (d/"validation").mkdir()
        (d/"ontology/__init__.py").write_text("",encoding="utf-8")
        (d/"ontology/p160_authority_requirements_resolution.py").write_text(base.replace(old,new,1),encoding="utf-8")
        for n in ("p160f_authority_requirements_resolution_v1_test.py",
                  "p160f_authority_requirements_resolution_defensive_crown_v1_test.py",
                  "p160f_authority_requirements_resolution_mutation_crown_v2_test.py"):
            shutil.copy2(ROOT/"validation"/n,d/"validation"/n)
        env=os.environ.copy(); env["PYTHONPATH"]=str(d)+os.pathsep+str(ROOT)
        cp=subprocess.run([sys.executable,"-m","pytest","-q",
            str(d/"validation/p160f_authority_requirements_resolution_v1_test.py"),
            str(d/"validation/p160f_authority_requirements_resolution_defensive_crown_v1_test.py"),
            str(d/"validation/p160f_authority_requirements_resolution_mutation_crown_v2_test.py")],
            cwd=d,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        results.append({"id":mid,"status":"KILLED" if cp.returncode else "SURVIVED",
                        "returncode":cp.returncode,"output_tail":cp.stdout[-1000:]})

if sh(R)!=EXPECTED: raise SystemExit("P160F_CANONICAL_RUNTIME_CONTAMINATED")
k=sum(x["status"]=="KILLED" for x in results)
s=sum(x["status"]=="SURVIVED" for x in results)
i=sum(x["status"]=="INCONCLUSIVE" for x in results)
score=k/len(results) if results else 0.0
report={"schema":"oce.p160f.mutation_crown.v2","supersedes":"oce.p160f.mutation_crown.v1",
"runtime_sha256":EXPECTED,"mutant_count":len(results),"killed":k,"survived":s,
"inconclusive":i,"mutation_score":score,"canonical_runtime_unchanged":True,
"authority_created":False,"authorization_created":False,"execution_performed":False,
"p160g_opened":False,"p161_opened":False,"results":results}
rp=ROOT/"validation/p160f_authority_requirements_resolution_mutation_crown_v2_report.json"
rp.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
for x in results: print(x["id"]+"="+x["status"])
print("P160F_MUTATION_CROWN_V2_RESULTS")
print("MUTANTS="+str(len(results))); print("KILLED="+str(k)); print("SURVIVED="+str(s)); print("INCONCLUSIVE="+str(i))
print("MUTATION_SCORE="+format(score,".6f")); print("CANONICAL_RUNTIME_UNCHANGED=true")
print("AUTHORITY_CREATED=false"); print("AUTHORIZATION_CREATED=false"); print("EXECUTION_PERFORMED=false")
print("P160G_OPENED=false"); print("P161_OPENED=false"); print("REPORT="+str(rp))
if s or i: raise SystemExit(1)
print("P160F_MUTATION_CROWN_V2_OK")
