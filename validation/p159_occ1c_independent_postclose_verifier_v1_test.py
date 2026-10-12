from pathlib import Path
from copy import deepcopy
import json,shutil,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from ontology import occ_constitutional_compiler_postclose_verifier as v
ART=ROOT/"validation_artifacts"/"p159"/"occ1c"
def copy_all(d):
    d.mkdir(parents=True,exist_ok=True)
    for n in v.EVIDENCE+(v.CLOSURE,):shutil.copy2(ART/n,d/n)
def run():
    a=v.verify(ART);b=v.verify(ART)
    assert a["status"]=="PASS" and v.verify_proof(a,ART) and a==b
    p=a["payload"];assert p["occ1c_closed"] is True and p["postclose_verified"] is True
    assert p["occ1d_opened"] is False and p["p160_opened"] is False and p["p159_final_lock"] is False
    with tempfile.TemporaryDirectory() as td:
        d=Path(td);copy_all(d);(d/"bounded_gaps_evidence_v1.json").unlink();assert v.verify(d)["status"]=="FAIL"
    with tempfile.TemporaryDirectory() as td:
        d=Path(td);copy_all(d);q=d/v.CLOSURE;o=json.loads(q.read_text());o["payload"]["authority_activated"]=True;q.write_text(json.dumps(o,sort_keys=True,separators=(",",":"))+"\n");assert v.verify(d)["status"]=="FAIL"
    with tempfile.TemporaryDirectory() as td:
        d=Path(td);copy_all(d);q=d/v.CLOSURE;o=json.loads(q.read_text());o["payload"]["occ1d_opened"]=True;o["payload"]["transaction_id"]=v.ch({k:x for k,x in o["payload"].items() if k!="transaction_id"});q.write_text(json.dumps(o,sort_keys=True,separators=(",",":"))+"\n");assert v.verify(d)["status"]=="FAIL"
    with tempfile.TemporaryDirectory() as td:
        d=Path(td);copy_all(d);q=d/"compile_report_v1.json";o=json.loads(q.read_text());o["cci_7_13_14_proven"]=False;q.write_text(json.dumps(o,sort_keys=True,separators=(",",":"))+"\n");assert v.verify(d)["status"]=="FAIL"
    print("P159_OCC1C_POSTCLOSE_FUNCTIONAL_OK")
    print("P159_OCC1C_POSTCLOSE_TRANSACTION_ID_VERIFIED")
    print("P159_OCC1C_POSTCLOSE_UPSTREAM_BINDINGS_VERIFIED")
    print("P159_OCC1C_POSTCLOSE_MISSING_EVIDENCE_DETECTED")
    print("P159_OCC1C_POSTCLOSE_AUTHORITY_INFLATION_DETECTED")
    print("P159_OCC1C_POSTCLOSE_REHASHED_STAGE_DRIFT_DETECTED")
    print("P159_OCC1C_POSTCLOSE_UPSTREAM_TAMPER_DETECTED")
    print("P159_OCC1C_POSTCLOSE_DETERMINISM_OK")
    print("P159_OCC1C_POSTCLOSE_STAGE_BOUNDARY_OK")
if __name__=="__main__":run()
