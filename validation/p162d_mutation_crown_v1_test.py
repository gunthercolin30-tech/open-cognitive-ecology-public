from pathlib import Path
import subprocess,sys,tempfile,os
ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/"ontology/runtime_precondition_evaluator.py"
BASE=ROOT/"validation/p162d_runtime_context_preconditions_gate_v1_test.py"
DEF=ROOT/"validation/p162d_defense_crown_v1_test.py"
SOURCE=ENGINE.read_text(encoding="utf-8")
MUTATIONS=[
("M01_UNKNOWN_TO_SATISFIED",'elif not known(p["observed_state"]): status="UNKNOWN"','elif not known(p["observed_state"]): status="SATISFIED"'),
("M02_STALE_TO_SATISFIED",'if p["freshness"]!="FRESH": status="STALE"','if p["freshness"]!="FRESH": status="SATISFIED"'),
("M03_PREDICTION_REPLACES_OBSERVATION",'elif p["evidence_class"]=="PREDICTION" and p.get("prediction_allowed") is not True: status="UNKNOWN"','elif p["evidence_class"]=="PREDICTION" and p.get("prediction_allowed") is not True: status="SATISFIED"'),
("M04_TARGET_DRIFT_IGNORED",'if target_snapshot.get("target_binding")!=invocation_request.get("target_binding") or target_snapshot.get("target_fingerprint")!=invocation_request.get("target_fingerprint"): failures.append("TARGET_STATE_DRIFTED")','if False: failures.append("TARGET_STATE_DRIFTED")'),
("M05_SAFETY_INTERLOCK_IGNORED",'if r["type"]=="SAFETY" and r["status"]!="SATISFIED": failures.append("SAFETY_INTERLOCK_FAILED")','if False: failures.append("SAFETY_INTERLOCK_FAILED")'),
("M06_MANDATORY_PRECONDITION_DROPPED",'if eid not in ids: failures.append("MANDATORY_UPSTREAM_PRECONDITION_DROPPED")','if False: failures.append("MANDATORY_UPSTREAM_PRECONDITION_DROPPED")'),
("M07_COMPOSITION_STATE_IGNORED",'if composition_snapshot.get("status")!="SATISFIED": failures.append("COMPOSITION_PRECONDITION_FAILED")','if False: failures.append("COMPOSITION_PRECONDITION_FAILED")'),
("M08_RESOURCE_AVAILABILITY_TREATED_RESERVED",'return {"status":"PRECONDITIONS_SATISFIED","assessment":a,**manifest()}','return {"status":"PRECONDITIONS_SATISFIED","assessment":a,**{**manifest(),"reservation_created":True}}'),
("M09_CONTINUOUS_TO_CHECK_ONCE",'if minimum and RECHECK_RANK[p["recheck_stage"]]<RECHECK_RANK[minimum]: return None,"RECHECK_STAGE_DOWNGRADE"','if False: return None,"RECHECK_STAGE_DOWNGRADE"'),
("M10_SECURITY_UNKNOWN_TO_TRUSTED",'if security_snapshot.get("trust_status")!="TRUSTED" or security_snapshot.get("compromise_flag") is not False: failures.append("SECURITY_CONTEXT_UNTRUSTED")','if security_snapshot.get("trust_status") not in ("TRUSTED","UNKNOWN") or security_snapshot.get("compromise_flag") is not False: failures.append("SECURITY_CONTEXT_UNTRUSTED")')
]
def run_mutant(name,old,new):
    assert SOURCE.count(old)==1,(name,"ANCHOR_COUNT",SOURCE.count(old))
    mutant=SOURCE.replace(old,new)
    with tempfile.TemporaryDirectory(prefix="p162d-mut-") as d:
        d=Path(d); (d/"ontology").mkdir(); (d/"ontology/__init__.py").write_text("")
        (d/"ontology/runtime_precondition_evaluator.py").write_text(mutant,encoding="utf-8")
        (d/"validation").mkdir(); (d/"validation/__init__.py").write_text("")
        (d/"validation"/BASE.name).write_text(BASE.read_text(encoding="utf-8"),encoding="utf-8")
        (d/"validation"/DEF.name).write_text(DEF.read_text(encoding="utf-8"),encoding="utf-8")
        env={**os.environ,"PYTHONPATH":str(d)}
        cp=subprocess.run([sys.executable,"-m","pytest","-q",str(d/"validation"/BASE.name),str(d/"validation"/DEF.name)],cwd=d,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        return cp.returncode,cp.stdout
def test_all_ten_canonical_mutations_are_killed():
    for name,old,new in MUTATIONS:
        rc,out=run_mutant(name,old,new)
        assert rc!=0,name+" SURVIVED\n"+out
def test_mutation_catalog_exact():
    assert len(MUTATIONS)==10 and len({x[0] for x in MUTATIONS})==10
