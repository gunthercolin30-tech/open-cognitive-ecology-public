from pathlib import Path
import json,shutil,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_constitutional_compiler_canonical_readiness_audit as a
SRC=ROOT/"normative"/"occ1a"; PROOF=ROOT/"validation_artifacts"/"p159"/"occ1b"/"occ1b_postclose_verification.json"
ART=ROOT/"validation_artifacts"/"p159"/"occ1c"; COMP=ROOT/"ontology"/"occ_constitutional_compiler.py"
NAMES=("compile_report_v1.json","transformation_ledger_v1.json","compiler_manifest_v1.json","bounded_gaps_evidence_v1.json")
def cp(dst):
    dst.mkdir(parents=True,exist_ok=True)
    for n in NAMES: shutil.copy2(ART/n,dst/n)
def run():
    x=a.audit_v1_1(SRC,PROOF,ART,COMP); y=a.audit_v1_1(SRC,PROOF,ART,COMP)
    assert x["status"]=="PASS" and x["payload"]["counts"]=={"SATISFIED":25,"BOUNDED":0,"MISSING":0},x
    assert x["payload"]["decision"]=="OCC1C_READY_TO_CLOSE"
    assert x["audit_sha256"]==y["audit_sha256"]
    assert x["payload"]["occ1c_closed"] is False and x["payload"]["occ1d_opened"] is False and x["payload"]["p160_opened"] is False
    with tempfile.TemporaryDirectory() as t:
        d=Path(t); cp(d); (d/NAMES[3]).unlink()
        assert a.audit_v1_1(SRC,PROOF,d,COMP)["payload"]["decision"]=="OCC1C_NOT_READY_TO_CLOSE"
    with tempfile.TemporaryDirectory() as t:
        d=Path(t); cp(d); q=d/NAMES[3]; o=json.loads(q.read_text()); o["proofs"][1]["ops"]=["ABSTAIN"]; q.write_text(json.dumps(o,sort_keys=True,separators=(",",":"))+"\n")
        assert a.audit_v1_1(SRC,PROOF,d,COMP)["payload"]["decision"]=="OCC1C_NOT_READY_TO_CLOSE"
    with tempfile.TemporaryDirectory() as t:
        d=Path(t); cp(d); q=d/NAMES[1]; o=json.loads(q.read_text()); o["entries"]=o["entries"][:-1]; q.write_text(json.dumps(o,sort_keys=True,separators=(",",":"))+"\n")
        assert a.audit_v1_1(SRC,PROOF,d,COMP)["payload"]["decision"]=="OCC1C_NOT_READY_TO_CLOSE"
    with tempfile.TemporaryDirectory() as t:
        d=Path(t); cp(d); q=d/NAMES[2]; o=json.loads(q.read_text()); o["self_activation"]=True; q.write_text(json.dumps(o,sort_keys=True,separators=(",",":"))+"\n")
        assert a.audit_v1_1(SRC,PROOF,d,COMP)["payload"]["decision"]=="OCC1C_NOT_READY_TO_CLOSE"
    print("P159_OCC1C_READINESS_V1_1_FUNCTIONAL_OK")
    print("P159_OCC1C_READINESS_V1_1_25_SATISFIED_0_BOUNDED_0_MISSING")
    print("P159_OCC1C_READINESS_V1_1_READY_TO_CLOSE")
    print("P159_OCC1C_READINESS_V1_1_MISSING_ARTIFACT_DETECTED")
    print("P159_OCC1C_READINESS_V1_1_CCI13_TAMPER_DETECTED")
    print("P159_OCC1C_READINESS_V1_1_LEDGER_47_OF_48_DETECTED")
    print("P159_OCC1C_READINESS_V1_1_SELF_ACTIVATION_TAMPER_DETECTED")
    print("P159_OCC1C_READINESS_V1_1_DETERMINISM_OK")
    print("P159_OCC1C_READINESS_V1_1_STAGE_BOUNDARY_OK")
if __name__=="__main__": run()
