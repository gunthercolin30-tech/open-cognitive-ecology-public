from pathlib import Path
import json, tempfile
from ontology import occ_governed_version_binding_resolver as v

ROOT=Path(__file__).resolve().parents[1]
EXPECTED="da56dde746fcb7f6154b4aac99879d727e30645a77564f35bbc5bca6102269bc"

def _write(root,rel,obj):
    p=root/rel
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,sort_keys=True),encoding="utf-8")

def _fixtures(root, identity=EXPECTED):
    lock={
      "schema":"oce.p110.final_lock.v1","milestone":"P110","status":"LOCKED",
      "canonical_signal":"CONSTITUTIONAL_FINAL_LOCK_OK","constitutional_final_lock_ok":True,
      "final_lock_identity_sha256":identity,
      "signals":{"CONSTITUTION_LOCKED":True,"DNA_CONSTITUTIVE_LOCKED":True,"GOVERNANCE_ENGINE_VALIDATED":True}}
    post={
      "schema":"oce.p110.postlock.verification.v1","milestone":"P110","status":"POSTLOCK_VERIFIED",
      "final_lock_identity_sha256":identity,"identity_exact":True,"identity_recomputed":True,
      "protected_artifact_drift_absent":True}
    _write(root,"validation/evidence/p110_final_lock_v1.json",lock)
    _write(root,"validation/evidence/p110_postlock_verification_v1.json",post)

def main():
    x=v.resolve(ROOT)
    assert x["status"]=="GOVERNED_VERSION_BINDINGS_RESOLVED",x
    assert x["p110_final_lock_identity_sha256"]==EXPECTED,x
    assert x["constitution_version"]=="P110:CONSTITUTIONAL_FINAL_LOCK_OK:"+EXPECTED
    assert x["governance_version"]=="P110:GOVERNANCE_ENGINE_VALIDATED:"+EXPECTED
    assert x["read_only"] and not x["normative_effect"] and not x["authority_activated"]
    print("P159_OCC1A_GOVERNED_VERSION_BINDING_V1_1_FUNCTIONAL_OK")

    with tempfile.TemporaryDirectory() as td:
        t=Path(td); _fixtures(t)
        # A textual/report duplicate with the signal but wrong schema must be ignored.
        _write(t,"validation/evidence/p110_report_copy.json",
               {"schema":"oce.report.v1","canonical_signal":"CONSTITUTIONAL_FINAL_LOCK_OK",
                "final_lock_identity_sha256":"0"*64})
        y=v.resolve(t)
        assert y["status"]=="GOVERNED_VERSION_BINDINGS_RESOLVED",y
        assert y["p110_final_lock_identity_sha256"]==EXPECTED
    print("P159_OCC1A_GOVERNED_VERSION_BINDING_V1_1_FALSE_DUPLICATE_IGNORED_OK")

    cases=[]
    with tempfile.TemporaryDirectory() as td:
        t=Path(td); _fixtures(t)
        (t/"validation/evidence/p110_postlock_verification_v1.json").unlink()
        cases.append(v.resolve(t)["status"]=="GOVERNED_VERSION_BINDINGS_BLOCKED")
    with tempfile.TemporaryDirectory() as td:
        t=Path(td); _fixtures(t)
        p=t/"validation/evidence/p110_postlock_verification_v1.json"
        d=json.loads(p.read_text()); d["final_lock_identity_sha256"]="1"*64; p.write_text(json.dumps(d))
        z=v.resolve(t); cases.append("P110_LOCK_POSTLOCK_IDENTITY_DIVERGENCE" in z["blockers"])
    with tempfile.TemporaryDirectory() as td:
        t=Path(td); _fixtures(t)
        p=t/"validation/evidence/p110_final_lock_v1.json"
        d=json.loads(p.read_text()); d["signals"]["GOVERNANCE_ENGINE_VALIDATED"]=False; p.write_text(json.dumps(d))
        z=v.resolve(t); cases.append("P110_GOVERNANCE_ENGINE_BINDING_MISSING" in z["blockers"])
    assert all(cases),cases
    print("P159_OCC1A_GOVERNED_VERSION_BINDING_V1_1_DEGRADATION_OK")

    assert v.resolve(ROOT)==v.resolve(ROOT)
    print("P159_OCC1A_GOVERNED_VERSION_BINDING_V1_1_NONREGRESSION_OK")
    print("status="+x["status"])
    print("constitution_version="+x["constitution_version"])
    print("governance_version="+x["governance_version"])
    print("authority_activated=false")
    print("occ1a_closed=false")
    print("occ1b_opened=false")
    print("p160_opened=false")

if __name__=="__main__":
    main()
