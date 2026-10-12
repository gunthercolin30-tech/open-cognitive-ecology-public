#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict

ROOT=Path.home()/"open-cognitive-ecology"
INV=ROOT/"ontology_inventory.txt"
P014A=ROOT/"p014_a_legacy_capability_boundary_contract_report.json"
P014B=ROOT/"p014_b_governed_legacy_candidate_assessment_report.json"
OUT=ROOT/"p014_c_legacy_capability_adapter_core_report.json"

EXPECTED_A="6698bee8229a108f290f3797b6f34e94c28040a365900dba81c98268885adae4"
EXPECTED_B="48891a4800e4661a90dfec2f8f654cd4a4153babcee378d694085590493fc947"
ALLOWED={"COMPATIBLE","INCOMPATIBLE","UNKNOWN"}

def fail(x): raise SystemExit("P014_C_REFUSED: "+x)
def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def stable(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

for p in (INV,P014A,P014B):
    if not p.is_file(): fail("missing prerequisite: "+str(p))
inv0=sha(INV); a=load(P014A); b=load(P014B)
if a.get("contract_identity_sha256")!=EXPECTED_A: fail("P014-A identity drift")
if b.get("assessment_identity_sha256")!=EXPECTED_B: fail("P014-B identity drift")
s=b.get("summary",{})
if (s.get("candidate_count"),s.get("COMPATIBLE"),s.get("INCOMPATIBLE"),s.get("UNKNOWN"))!=(973,0,0,973):
    fail("P014-B compatibility boundary drift")

@dataclass(frozen=True)
class Binding:
    component_id:str
    source_path:str
    source_sha256:str
    operation:str
    status:str
    target_contract:str
    evidence:tuple

class LegacyCapabilityAdapter:
    """Boundary adapter only. No dynamic imports, eval, discovery, dispatcher or executor."""
    def __init__(self, bindings:Dict[str,Binding], callables:Dict[str,Callable[[Any],Any]]):
        self._bindings=dict(bindings)
        self._callables=dict(callables)

    def invoke(self, request:Dict[str,Any])->Dict[str,Any]:
        required=("legacy_component_id","legacy_source_path","legacy_source_sha256","operation","input_payload","correlation_id")
        missing=[k for k in required if k not in request or (k!="input_payload" and not str(request[k]).strip())]
        if missing: return self._failure(request,"CONTRACT_INVALID","missing:"+",".join(missing))
        cid=str(request["legacy_component_id"])
        binding=self._bindings.get(cid)
        if binding is None: return self._failure(request,"UNRESOLVED_COMPONENT","component not explicitly bound")
        if binding.status not in ALLOWED: return self._failure(request,"ASSESSMENT_INVALID","invalid compatibility status")
        if binding.status=="UNKNOWN": return self._failure(request,"COMPATIBILITY_UNKNOWN","runtime invocation refused")
        if binding.status=="INCOMPATIBLE": return self._failure(request,"COMPATIBILITY_INCOMPATIBLE","runtime invocation refused")
        if not binding.evidence or not binding.target_contract or binding.target_contract=="UNKNOWN":
            return self._failure(request,"COMPATIBILITY_EVIDENCE_INVALID","compatible binding lacks target evidence")
        if request["legacy_source_path"]!=binding.source_path or request["legacy_source_sha256"]!=binding.source_sha256:
            return self._failure(request,"PROVENANCE_MISMATCH","source provenance mismatch")
        if request["operation"]!=binding.operation:
            return self._failure(request,"OPERATION_MISMATCH","operation mismatch")
        fn=self._callables.get(cid)
        if fn is None: return self._failure(request,"CALLABLE_NOT_BOUND","no explicit callable binding")
        try:
            value=fn(copy.deepcopy(request["input_payload"]))
            return {
              "status":"SUCCESS","output_payload":value,
              "error":{"code":None,"message":None,"legacy_exception_type":None},
              "correlation_id":request["correlation_id"],"legacy_component_id":cid,
              "provenance":{"source_path":binding.source_path,"source_sha256":binding.source_sha256,
                            "target_contract":binding.target_contract,"adapter":"LegacyCapabilityAdapter"}
            }
        except Exception as ex:
            return self._failure(request,"LEGACY_EXCEPTION",str(ex)[:240],type(ex).__name__)

    def _failure(self,r,code,msg,etype=None):
        return {"status":"FAILURE","output_payload":None,
          "error":{"code":code,"message":msg,"legacy_exception_type":etype},
          "correlation_id":r.get("correlation_id"),"legacy_component_id":r.get("legacy_component_id")}

calls={"n":0}
def fixture(payload):
    calls["n"]+=1
    return {"echo":payload,"fixture":True}
def exploding(payload):
    calls["n"]+=1
    raise ValueError("fixture failure")

H="a"*64
req={"legacy_component_id":"fixture.ok","legacy_source_path":"fixtures/ok.py","legacy_source_sha256":H,
     "operation":"echo","input_payload":{"x":1},"correlation_id":"corr-1"}
compatible=Binding("fixture.ok","fixtures/ok.py",H,"echo","COMPATIBLE","V2:fixture.echo",("synthetic positive evidence",))
unknown=Binding("fixture.unknown","fixtures/u.py",H,"echo","UNKNOWN","UNKNOWN",("insufficient evidence",))
incompatible=Binding("fixture.bad","fixtures/b.py",H,"echo","INCOMPATIBLE","UNKNOWN",("synthetic incompatibility evidence",))
explodes=Binding("fixture.ex","fixtures/ex.py",H,"echo","COMPATIBLE","V2:fixture.echo",("synthetic positive evidence",))

adapter=LegacyCapabilityAdapter(
 {"fixture.ok":compatible,"fixture.unknown":unknown,"fixture.bad":incompatible,"fixture.ex":explodes},
 {"fixture.ok":fixture,"fixture.unknown":fixture,"fixture.bad":fixture,"fixture.ex":exploding}
)
tests=[]
def t(n,v): tests.append({"name":n,"passed":bool(v)})

before=calls["n"]; out=adapter.invoke(req)
t("compatible_fixture_success",out["status"]=="SUCCESS" and out["output_payload"]["echo"]=={"x":1})
t("correlation_preserved",out["correlation_id"]=="corr-1")
t("provenance_preserved",out["provenance"]["source_sha256"]==H)
t("compatible_fixture_called_once",calls["n"]==before+1)

r=dict(req); r["legacy_component_id"]="fixture.unknown"; r["legacy_source_path"]="fixtures/u.py"
before=calls["n"]; out=adapter.invoke(r)
t("unknown_refused",out["error"]["code"]=="COMPATIBILITY_UNKNOWN" and calls["n"]==before)

r=dict(req); r["legacy_component_id"]="fixture.bad"; r["legacy_source_path"]="fixtures/b.py"
before=calls["n"]; out=adapter.invoke(r)
t("incompatible_refused",out["error"]["code"]=="COMPATIBILITY_INCOMPATIBLE" and calls["n"]==before)

r=dict(req); r["legacy_component_id"]="missing"
before=calls["n"]; out=adapter.invoke(r)
t("unresolved_refused",out["error"]["code"]=="UNRESOLVED_COMPONENT" and calls["n"]==before)

r=dict(req); r["legacy_source_sha256"]="b"*64
before=calls["n"]; out=adapter.invoke(r)
t("provenance_mismatch_refused",out["error"]["code"]=="PROVENANCE_MISMATCH" and calls["n"]==before)

r=dict(req); r["operation"]="other"
before=calls["n"]; out=adapter.invoke(r)
t("operation_mismatch_refused",out["error"]["code"]=="OPERATION_MISMATCH" and calls["n"]==before)

r=dict(req); r.pop("correlation_id")
before=calls["n"]; out=adapter.invoke(r)
t("invalid_contract_refused",out["error"]["code"]=="CONTRACT_INVALID" and calls["n"]==before)

r=dict(req); r["legacy_component_id"]="fixture.ex"; r["legacy_source_path"]="fixtures/ex.py"
out=adapter.invoke(r)
t("legacy_exception_normalized",out["status"]=="FAILURE" and out["error"]["code"]=="LEGACY_EXCEPTION" and out["error"]["legacy_exception_type"]=="ValueError")

t("p014a_binding",a.get("contract_identity_sha256")==EXPECTED_A)
t("p014b_binding",b.get("assessment_identity_sha256")==EXPECTED_B)
t("real_candidates_all_unknown",s.get("UNKNOWN")==973 and s.get("COMPATIBLE")==0)
t("no_real_candidate_binding",all(not k.startswith(("ontology/","runtime/","validation/")) for k in adapter._bindings))
t("ontology_nonmutation",sha(INV)==inv0)

if not all(x["passed"] for x in tests): fail("self-test failure")

report={
 "schema":"oce.p014.legacy_capability_adapter_core.v1","milestone":"P014-C","status":"VALIDATED",
 "architecture":{
   "role":"legacy adaptation boundary/bridge only",
   "creates_executor":False,"creates_dispatcher":False,"dynamic_imports":False,"eval":False,
   "explicit_binding_required":True,
   "existing_execution_pipeline_preserved":True,
   "real_legacy_invocation_performed":False
 },
 "compatibility_gate":{"UNKNOWN":"REFUSED","INCOMPATIBLE":"REFUSED","COMPATIBLE":"ELIGIBLE_WITH_EXPLICIT_BINDING_AND_EVIDENCE"},
 "real_candidate_boundary":{"candidate_count":973,"COMPATIBLE":0,"INCOMPATIBLE":0,"UNKNOWN":973,"invocable":0},
 "synthetic_fixture":{"used":True,"purpose":"exercise adapter mechanics without promoting or invoking real legacy candidates"},
 "tests":{"passed":sum(x["passed"] for x in tests),"total":len(tests),"details":tests},
 "bindings":{"p014_a_contract_identity_sha256":EXPECTED_A,"p014_b_assessment_identity_sha256":EXPECTED_B,
             "ontology_inventory_sha256":inv0},
 "epistemic_status":{"functional_conclusion_only":True,"phenomenology_undetermined":True,
   "consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False},
 "next_step":"P014-D representative governed runtime compatibility campaign."
}
report["adapter_core_identity_sha256"]=stable(report)
OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
if sha(INV)!=inv0: fail("ontology inventory mutated")
rt=load(OUT); ident=rt.pop("adapter_core_identity_sha256")
if stable(rt)!=ident: fail("round-trip identity failure")

print("P014_C_LEGACY_CAPABILITY_ADAPTER_CORE_OK")
print("status=VALIDATED")
print(f"tests={len(tests)}/{len(tests)}")
print("real_candidates=973")
print("real_COMPATIBLE=0")
print("real_UNKNOWN=973")
print("real_invocable=0")
print("real_legacy_invocation=NONE")
print("synthetic_compatible_fixture=SUCCESS")
print("UNKNOWN_gate=REFUSED")
print("INCOMPATIBLE_gate=REFUSED")
print("dynamic_imports=NONE")
print("new_executor=NO")
print("new_dispatcher=NO")
print("p014_a_binding=VERIFIED")
print("p014_b_binding=VERIFIED")
print("ontology_inventory_non_mutation=OK")
print("adapter_core_identity_sha256="+ident)
print("report="+str(OUT))
