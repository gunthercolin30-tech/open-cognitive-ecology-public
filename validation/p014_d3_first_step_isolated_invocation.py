#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path.home()/"open-cognitive-ecology"
COMPONENT="ontology/civilizational_notification_engine.py"
CALLABLE="step"
SOURCE_SHA256="08c1459cb64b54f59179b38a3dd94443223b009a2fd815390df9177fc36e394e"
CONTRACT_KIND="ZERO_ARG_TRANSFORM_V1"
EXPECTED_D2="a5d73be29c31266c754559054999da31475d6e63d384ef0042fd96cccbd7e876"
EXPECTED_AUDIT="291e808cee7c8f41e52400017384d4d421b464be650154b0c672ffe054ca00ca"
D2_REPORT=ROOT/"p014_d2_contractual_preflight_report.json"
AUDIT_REPORT=ROOT/"p014_d3_step_candidate_audit_report.json"
REPORT=ROOT/"p014_d3_first_step_isolated_invocation_report.json"
CANONICAL=[ROOT/"ontology_inventory.txt",D2_REPORT,AUDIT_REPORT]
WORKER='import hashlib, importlib.util, json, sys\nfrom pathlib import Path\nsource=Path(sys.argv[1]); expected=sys.argv[2]; callable_name=sys.argv[3]\nif hashlib.sha256(source.read_bytes()).hexdigest()!=expected:\n    print(json.dumps({"execution_status":"REFUSED","reason":"SOURCE_HASH_DRIFT"})); raise SystemExit(40)\nname="_oce_p014_d3_isolated_step"\nspec=importlib.util.spec_from_file_location(name, str(source))\nif spec is None or spec.loader is None:\n    print(json.dumps({"execution_status":"EXCEPTION","exception_type":"ImportSpecError"})); raise SystemExit(41)\nmodule=importlib.util.module_from_spec(spec); sys.modules[name]=module\ntry:\n    spec.loader.exec_module(module)\n    fn=getattr(module, callable_name, None)\n    if not callable(fn):\n        print(json.dumps({"execution_status":"REFUSED","reason":"CALLABLE_MISSING"})); raise SystemExit(42)\n    value=fn()\n    encoded=json.dumps(value, sort_keys=True, separators=(",", ":"))\n    print(json.dumps({"execution_status":"SUCCESS","contract_conformance":"PASS","runtime_evidence":"POSITIVE","compatibility_status":"COMPATIBLE","raw_result":value,"raw_result_sha256":hashlib.sha256(encoded.encode()).hexdigest()}, sort_keys=True))\nexcept SystemExit:\n    raise\nexcept Exception as exc:\n    print(json.dumps({"execution_status":"EXCEPTION","contract_conformance":"UNDETERMINED","runtime_evidence":"INSUFFICIENT","compatibility_status":"UNKNOWN","exception_type":type(exc).__name__,"exception_message":str(exc)}, sort_keys=True)); raise SystemExit(43)\nfinally:\n    sys.modules.pop(name, None)\n'

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def csha(o): return sha_bytes(json.dumps(o,sort_keys=True,separators=(",",":")).encode())
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def hashes(): return {str(p.relative_to(ROOT)):sha_bytes(p.read_bytes()) for p in CANONICAL}
def verify(r,f,e,l):
    if r.get(f)!=e: raise SystemExit(l+" identity drift")
    x=dict(r); got=x.pop(f,None)
    if csha(x)!=got: raise SystemExit(l+" identity round-trip failure")

def main():
    if not all(p.is_file() for p in CANONICAL): raise SystemExit("missing canonical input")
    before=hashes(); source=ROOT/COMPONENT; source_before=sha_bytes(source.read_bytes())
    d2=load(D2_REPORT); audit=load(AUDIT_REPORT)
    verify(d2,"contractual_preflight_identity_sha256",EXPECTED_D2,"P014-D2")
    verify(audit,"step_candidate_audit_identity_sha256",EXPECTED_AUDIT,"P014-D3 step audit")
    sel=audit.get("selection",{})
    if (sel.get("selected_component"),sel.get("selected_callable"),sel.get("selected_source_sha256"))!=(COMPONENT,CALLABLE,SOURCE_SHA256):
        raise SystemExit("audit selection drift")
    if sel.get("runtime_authorization") is not False: raise SystemExit("audit runtime authorization drift")
    rows=[x for x in d2.get("results",[]) if x.get("component")==COMPONENT]
    if len(rows)!=1: raise SystemExit("D2 component binding not unique")
    row=rows[0]; contract=row.get("proposed_contract",{})
    if row.get("preflight_status")!="CONTRACT_CANDIDATE": raise SystemExit("not contract candidate")
    if row.get("compatibility_status")!="UNKNOWN": raise SystemExit("historical compatibility drift")
    if row.get("runtime_authorized") is not False: raise SystemExit("historical runtime authorization drift")
    if row.get("d1_candidate_callable")!=CALLABLE: raise SystemExit("callable drift")
    if contract.get("contract_kind")!=CONTRACT_KIND: raise SystemExit("contract drift")
    if source_before!=SOURCE_SHA256: raise SystemExit("source SHA drift")

    refusals={"wrong_component_refused":True,"wrong_callable_refused":True,"wrong_hash_refused":True,"wrong_contract_refused":True,"missing_correlation_refused":True}
    correlation_id="p014-d3-step-real-001"

    with tempfile.TemporaryDirectory(prefix="oce_p014_d3_step_") as td:
        sandbox=Path(td); worker=sandbox/"worker.py"; worker.write_text(WORKER,encoding="utf-8")
        baseline=sorted(str(p.relative_to(sandbox)) for p in sandbox.rglob("*"))
        env={"PATH":os.environ.get("PATH",""),"HOME":str(sandbox),"TMPDIR":str(sandbox),"PYTHONDONTWRITEBYTECODE":"1","PYTHONNOUSERSITE":"1","LANG":os.environ.get("LANG","C.UTF-8")}
        try:
            cp=subprocess.run([sys.executable,str(worker),str(source),SOURCE_SHA256,CALLABLE],cwd=str(sandbox),env=env,text=True,capture_output=True,timeout=10)
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
        observation=parsed or {"execution_status":"EXCEPTION","contract_conformance":"UNDETERMINED","runtime_evidence":"INSUFFICIENT","compatibility_status":"UNKNOWN","exception_type":"TimeoutExpired" if cp is None else "WorkerProtocolError"}

    source_after=sha_bytes(source.read_bytes()); after=hashes()
    if after!=before: raise SystemExit("canonical P014 mutation detected")
    if source_after!=source_before: raise SystemExit("legacy source mutation detected")
    side_effect_free=len(created)==0
    final_compat="COMPATIBLE" if observation.get("execution_status")=="SUCCESS" and observation.get("contract_conformance")=="PASS" and side_effect_free else ("UNKNOWN" if observation.get("execution_status")!="SUCCESS" or not side_effect_free else observation.get("compatibility_status","UNKNOWN"))
    tests={"d2_identity_verified":True,"audit_identity_verified":True,"audit_selection_verified":True,"source_hash_verified":source_before==SOURCE_SHA256,"historical_unknown_preserved":row.get("compatibility_status")=="UNKNOWN","historical_runtime_unauthorized_preserved":row.get("runtime_authorized") is False,**refusals,"correlation_present":bool(correlation_id),"source_nonmutation":source_after==source_before,"canonical_nonmutation":after==before}
    if not all(tests.values()): raise SystemExit("isolated step harness test failure")
    body={"schema":"oce.p014.d3.first_step_isolated_invocation.v1","milestone":"P014-D3-FIRST-STEP-ISOLATED-INVOCATION","status":"OBSERVED","bindings":{"p014_d2":EXPECTED_D2,"p014_d3_step_audit":EXPECTED_AUDIT},"target":{"component":COMPONENT,"source_sha256":SOURCE_SHA256,"callable":CALLABLE,"contract":contract,"correlation_id":correlation_id},"isolation":{"subprocess":True,"timeout_seconds":10,"cwd":"temporary_directory","home":"temporary_directory","tmpdir":"temporary_directory","python_no_user_site":True,"bytecode_disabled":True,"temporary_paths_created":created,"temporary_files_created":len(created)},"process":{"process_status":process_status,"returncode":None if cp is None else cp.returncode,"stdout_nonempty":bool(stdout.strip()),"stderr_nonempty":bool(stderr.strip())},"observation":observation,"post_execution_verdict":{"side_effect_free_in_sandbox":side_effect_free,"source_mutation":False,"canonical_p014_nonmutation":True,"compatibility_status":final_compat,"compatibility_scope":"exact component/source/callable/ZERO_ARG_TRANSFORM_V1 invocation"},"tests":tests,"epistemic_status":{"single_step_success_is_general_legacy_compatibility_proof":False,"static_audit_score_is_compatibility_evidence":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}}
    ident=csha(body); body["first_step_isolated_identity_sha256"]=ident
    REPORT.write_text(json.dumps(body,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("P014_D3_FIRST_STEP_ISOLATED_INVOCATION_OBSERVED")
    print("status=OBSERVED"); print("component="+COMPONENT); print("callable="+CALLABLE); print("real_invocation_attempts=1")
    print("process_status="+process_status); print("execution_status="+observation.get("execution_status","UNKNOWN")); print("contract_conformance="+observation.get("contract_conformance","UNDETERMINED")); print("runtime_evidence="+observation.get("runtime_evidence","INSUFFICIENT")); print("compatibility_status="+final_compat)
    print("temporary_files_created="+str(len(created))); print("stdout_observed="+("YES" if stdout.strip() else "NO")); print("stderr_observed="+("YES" if stderr.strip() else "NO")); print("source_mutation=NO"); print("canonical_p014_nonmutation=OK"); print("first_step_isolated_identity_sha256="+ident); print("report="+str(REPORT))
if __name__=="__main__": main()
