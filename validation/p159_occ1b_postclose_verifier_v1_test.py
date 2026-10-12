from copy import deepcopy
from pathlib import Path
import json, shutil, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_normative_ir_postclose_verifier as v
SOURCE=ROOT/"normative"/"occ1a"
ART=ROOT/"validation_artifacts"/"p159"/"occ1b"/"occ1b_closure_transaction.json"

def write(p,obj):
    p.write_text(json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")

def rehash(obj):
    obj["payload_sha256"]=v.nir.canonical_sha256(obj["payload"])
    obj["transaction_id"]=obj["payload_sha256"]

def run():
    a=v.verify(SOURCE,ART); b=v.verify(SOURCE,ART)
    assert a["status"]==v.PASS,a
    assert a["reason"]=="P159_OCC1B_POSTCLOSE_VERIFICATION_OK"
    assert a["proof_sha256"]==b["proof_sha256"]
    p=a["proof"]
    assert p["occ1b_closed"] is True and p["post_close_verified"] is True
    assert p["writer_verify_function_used"] is False and p["writer_close_function_used"] is False
    assert p["bounded_requirements"]==["C08","C09"]
    assert p["authority_activated"] is False and p["execution_performed"] is False
    assert p["occ1c_opened"] is False and p["p160_opened"] is False
    assert p["p159_final_lock_performed"] is False
    assert v.verify_proof(p)["status"]==v.PASS
    tam=deepcopy(p); tam["missing_count"]=1
    assert v.verify_proof(tam)["status"]==v.FAIL

    original=json.loads(ART.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        # Simple artifact tamper, without rehash.
        x=deepcopy(original); x["payload"]["missing_count"]=1
        q=td/"tamper.json"; write(q,x)
        assert v.verify(SOURCE,q)["reason"]=="PAYLOAD_SHA_MISMATCH"

        # Rehashed semantic laundering must still fail.
        x=deepcopy(original); x["payload"]["bounded_requirements"]=["C08"]; rehash(x)
        q=td/"launder.json"; write(q,x)
        r=v.verify(SOURCE,q); assert r["status"]==v.FAIL and r["reason"]=="CLOSURE_SEMANTICS_INVALID",r

        # False self-certification.
        x=deepcopy(original); x["payload"]["post_close_verified"]=True; rehash(x)
        q=td/"selfcert.json"; write(q,x)
        r=v.verify(SOURCE,q); assert r["status"]==v.FAIL and r["reason"]=="CLOSURE_SEMANTICS_INVALID",r

        # Authority/execution/stage-boundary inflation.
        for key in ("authority_activated","execution_performed","occ1c_opened","p160_opened","p159_final_lock_performed"):
            x=deepcopy(original); x["payload"][key]=True; rehash(x)
            q=td/(key+".json"); write(q,x)
            r=v.verify(SOURCE,q); assert r["status"]==v.FAIL and r["reason"]=="CLOSURE_SEMANTICS_INVALID",(key,r)

        # Independent source drift fixture: clone package, alter/add/remove.
        clone=td/"occ1a"; shutil.copytree(SOURCE,clone)
        f=next(p for p in clone.rglob("*") if p.is_file() and not p.name.endswith(".bak"))
        f.write_bytes(f.read_bytes()+b"\n")
        r=v.verify(clone,ART); assert r["status"]==v.FAIL and r["reason"]=="POSTCLOSE_SOURCE_DRIFT_DETECTED",r

    print("P159_OCC1B_POSTCLOSE_FUNCTIONAL_OK")
    print("P159_OCC1B_POSTCLOSE_INDEPENDENT_CRYPTO_RECONSTRUCTION_OK")
    print("P159_OCC1B_POSTCLOSE_SOURCE_IDENTITY_OK")
    print("P159_OCC1B_POSTCLOSE_ARTIFACT_TAMPER_DETECTED")
    print("P159_OCC1B_POSTCLOSE_REHASHED_SEMANTIC_LAUNDERING_DETECTED")
    print("P159_OCC1B_POSTCLOSE_FALSE_SELFCERT_DETECTED")
    print("P159_OCC1B_POSTCLOSE_AUTHORITY_EXECUTION_STAGE_INFLATION_DETECTED")
    print("P159_OCC1B_POSTCLOSE_SOURCE_DRIFT_DETECTED")
    print("P159_OCC1B_POSTCLOSE_PROOF_TAMPER_DETECTED")
    print("P159_OCC1B_POSTCLOSE_DETERMINISM_OK")
    print("P159_OCC1B_POSTCLOSE_STAGE_BOUNDARY_OK")
if __name__=="__main__": run()
