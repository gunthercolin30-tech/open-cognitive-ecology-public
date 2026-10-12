#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path.home()/"open-cognitive-ecology"
COMPONENT="ontology/civilizational_notification_engine.py"
CALLABLE="step"
SOURCE_SHA256="08c1459cb64b54f59179b38a3dd94443223b009a2fd815390df9177fc36e394e"
EXPECTED_FIRST="fd3f6d455529261f97866e2a278067290d34dd7216e272042ce0e533b15ab25e"
FIRST_REPORT=ROOT/"p014_d3_first_step_isolated_invocation_report.json"
REPORT=ROOT/"p014_d3_step_replication_report.json"
SOURCE=ROOT/COMPONENT
WORKER='import hashlib, importlib.util, json, sys\nfrom pathlib import Path\nsource=Path(sys.argv[1]); expected=sys.argv[2]; callable_name=sys.argv[3]\nif hashlib.sha256(source.read_bytes()).hexdigest()!=expected:\n    print(json.dumps({"execution_status":"REFUSED","reason":"SOURCE_HASH_DRIFT"})); raise SystemExit(40)\nname="_oce_p014_d3_step_replication_worker"\nspec=importlib.util.spec_from_file_location(name,str(source))\nif spec is None or spec.loader is None:\n    print(json.dumps({"execution_status":"EXCEPTION","exception_type":"ImportSpecError"})); raise SystemExit(41)\nmodule=importlib.util.module_from_spec(spec); sys.modules[name]=module\ntry:\n    spec.loader.exec_module(module)\n    fn=getattr(module,callable_name,None)\n    if not callable(fn):\n        print(json.dumps({"execution_status":"REFUSED","reason":"CALLABLE_MISSING"})); raise SystemExit(42)\n    value=fn()\n    encoded=json.dumps(value,sort_keys=True,separators=(",",":"))\n    print(json.dumps({"execution_status":"SUCCESS","contract_conformance":"PASS","runtime_evidence":"POSITIVE","raw_result":value,"raw_result_sha256":hashlib.sha256(encoded.encode()).hexdigest()},sort_keys=True))\nexcept SystemExit:\n    raise\nexcept Exception as exc:\n    print(json.dumps({"execution_status":"EXCEPTION","contract_conformance":"UNDETERMINED","runtime_evidence":"INSUFFICIENT","exception_type":type(exc).__name__,"exception_message":str(exc)},sort_keys=True)); raise SystemExit(43)\nfinally:\n    sys.modules.pop(name,None)\n'

def hb(b): return hashlib.sha256(b).hexdigest()
def cs(o): return hb(json.dumps(o,sort_keys=True,separators=(",",":")).encode())
def load(p): return json.loads(p.read_text(encoding="utf-8"))

def verify_first(r):
    if r.get("first_step_isolated_identity_sha256")!=EXPECTED_FIRST:
        raise SystemExit("first isolated step identity drift")
    x=dict(r); got=x.pop("first_step_isolated_identity_sha256",None)
    if cs(x)!=got: raise SystemExit("first isolated step identity round-trip failure")
    t=r.get("target",{})
    if (t.get("component"),t.get("source_sha256"),t.get("callable"))!=(COMPONENT,SOURCE_SHA256,CALLABLE):
        raise SystemExit("first observation target drift")
    p=r.get("post_execution_verdict",{})
    o=r.get("observation",{})
    if o.get("execution_status")!="SUCCESS" or o.get("contract_conformance")!="PASS":
        raise SystemExit("first step observation not successful")
    if p.get("compatibility_status")!="COMPATIBLE":
        raise SystemExit("first step local compatibility not established")
    if not p.get("side_effect_free_in_sandbox"):
        raise SystemExit("first step was not sandbox-side-effect-free")

def shape(v):
    if isinstance(v,dict): return {"type":"dict","keys":sorted(v.keys()),"children":{k:shape(v[k]) for k in sorted(v)}}
    if isinstance(v,list): return {"type":"list","length":len(v),"children":[shape(x) for x in v]}
    if v is None: return {"type":"null"}
    if isinstance(v,bool): return {"type":"bool"}
    if isinstance(v,int): return {"type":"int"}
    if isinstance(v,float): return {"type":"float"}
    if isinstance(v,str): return {"type":"str"}
    return {"type":type(v).__name__}

def is_temporal_key(k):
    q=k.lower()
    return any(x in q for x in ("time","timestamp","date","created","updated","utc","now"))

def normalize_temporal(v,key=""):
    if isinstance(v,dict):
        return {k:("<TEMPORAL>" if is_temporal_key(k) else normalize_temporal(x,k)) for k,x in sorted(v.items())}
    if isinstance(v,list): return [normalize_temporal(x,key) for x in v]
    return v

def main():
    if not FIRST_REPORT.is_file(): raise SystemExit("first step report missing")
    if not SOURCE.is_file(): raise SystemExit("legacy source missing")
    first=load(FIRST_REPORT); verify_first(first)
    source_before=hb(SOURCE.read_bytes())
    if source_before!=SOURCE_SHA256: raise SystemExit("legacy source SHA drift")
    first_raw=first.get("observation",{}).get("raw_result")
    if "raw_result" not in first.get("observation",{}): raise SystemExit("first raw result unavailable")

    correlation_id="p014-d3-step-real-002"
    with tempfile.TemporaryDirectory(prefix="oce_p014_d3_step_replication_") as td:
        sandbox=Path(td); wp=sandbox/"worker.py"; wp.write_text(WORKER,encoding="utf-8")
        baseline=sorted(str(p.relative_to(sandbox)) for p in sandbox.rglob("*"))
        env={"PATH":os.environ.get("PATH",""),"HOME":str(sandbox),"TMPDIR":str(sandbox),"PYTHONDONTWRITEBYTECODE":"1","PYTHONNOUSERSITE":"1","LANG":os.environ.get("LANG","C.UTF-8")}
        try:
            cp=subprocess.run([sys.executable,str(wp),str(SOURCE),SOURCE_SHA256,CALLABLE],cwd=str(sandbox),env=env,text=True,capture_output=True,timeout=10)
            process_status="EXITED"; stdout=cp.stdout; stderr=cp.stderr
        except subprocess.TimeoutExpired as exc:
            cp=None; process_status="TIMEOUT"; stdout=exc.stdout or ""; stderr=exc.stderr or ""
        final=sorted(str(p.relative_to(sandbox)) for p in sandbox.rglob("*"))
        created=[x for x in final if x not in baseline]
        parsed=None
        if cp is not None:
            lines=[x for x in stdout.splitlines() if x.strip()]
            if lines:
                try: parsed=json.loads(lines[-1])
                except Exception: parsed=None
        obs=parsed or {"execution_status":"EXCEPTION","contract_conformance":"UNDETERMINED","runtime_evidence":"INSUFFICIENT","exception_type":"TimeoutExpired" if cp is None else "WorkerProtocolError"}

    source_after=hb(SOURCE.read_bytes())
    if source_after!=source_before: raise SystemExit("legacy source mutation detected")

    second_raw=obs.get("raw_result")
    structural_match="UNDETERMINED"
    non_temporal="UNDETERMINED"
    temporal_variation="UNDETERMINED"
    if obs.get("execution_status")=="SUCCESS" and obs.get("contract_conformance")=="PASS":
        structural_match="PASS" if shape(first_raw)==shape(second_raw) else "FAIL"
        n1=normalize_temporal(first_raw); n2=normalize_temporal(second_raw)
        non_temporal="PASS" if n1==n2 else "FAIL"
        temporal_variation="OBSERVED" if first_raw!=second_raw and n1==n2 else ("NOT_OBSERVED" if first_raw==second_raw else "MIXED_OR_NON_TEMPORAL")

    side_effect_free=len(created)==0
    reproduced=(process_status=="EXITED" and obs.get("execution_status")=="SUCCESS" and obs.get("contract_conformance")=="PASS" and structural_match=="PASS" and non_temporal=="PASS" and side_effect_free and not stderr.strip())
    reproducibility="REPRODUCED" if reproduced else ("NOT_REPRODUCED" if obs.get("execution_status")=="SUCCESS" else "UNDETERMINED")
    compatibility="COMPATIBLE" if reproduced else "UNKNOWN"

    tests={
        "first_identity_verified":True,
        "source_hash_verified":source_before==SOURCE_SHA256,
        "second_invocation_attempted_once":True,
        "correlation_distinct":correlation_id!=first.get("target",{}).get("correlation_id"),
        "source_nonmutation":source_after==source_before,
        "sandbox_inspected":True,
    }
    body={"schema":"oce.p014.d3.step_replication.v1","milestone":"P014-D3-STEP-REPLICATION","status":"OBSERVED","bindings":{"first_step_isolated":EXPECTED_FIRST},"target":{"component":COMPONENT,"source_sha256":SOURCE_SHA256,"callable":CALLABLE,"correlation_id":correlation_id},"process":{"process_status":process_status,"returncode":None if cp is None else cp.returncode,"stdout_nonempty":bool(stdout.strip()),"stderr_nonempty":bool(stderr.strip())},"observation":obs,"comparison":{"structural_match":structural_match,"non_temporal_invariants":non_temporal,"temporal_variation":temporal_variation,"temporary_files_created":len(created),"side_effect_free":side_effect_free,"reproducibility_status":reproducibility,"compatibility_status":compatibility},"tests":tests,"epistemic_status":{"raw_sha_equality_required":False,"temporal_variation_allowed":True,"general_legacy_compatibility_proven":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}}
    ident=cs(body); body["step_replication_identity_sha256"]=ident
    REPORT.write_text(json.dumps(body,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("P014_D3_STEP_REPLICATION_OBSERVED")
    print("status=OBSERVED"); print("component="+COMPONENT); print("callable="+CALLABLE); print("replication_attempts=1")
    print("process_status="+process_status); print("execution_status="+obs.get("execution_status","UNKNOWN")); print("contract_conformance="+obs.get("contract_conformance","UNDETERMINED"))
    print("structural_match="+structural_match); print("non_temporal_invariants="+non_temporal); print("temporal_variation="+temporal_variation)
    print("temporary_files_created="+str(len(created))); print("side_effect_free="+("YES" if side_effect_free else "NO")); print("stderr_observed="+("YES" if stderr.strip() else "NO"))
    print("reproducibility_status="+reproducibility); print("compatibility_status="+compatibility); print("source_mutation=NO")
    print("step_replication_identity_sha256="+ident); print("report="+str(REPORT))
if __name__=="__main__": main()
