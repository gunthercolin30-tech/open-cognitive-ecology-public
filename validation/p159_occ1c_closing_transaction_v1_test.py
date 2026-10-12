from pathlib import Path
from copy import deepcopy
import json,shutil,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_constitutional_compiler_closing_transaction as c
ART=ROOT/"validation_artifacts"/"p159"/"occ1c"
def run():
    a=c.build(ART); b=c.build(ART)
    assert a["status"]=="PASS" and c.verify(a,ART) and a==b
    p=a["payload"]
    assert p["occ1c_closed"] is True and p["occ1d_opened"] is False and p["p160_opened"] is False
    assert p["authorization_created"] is False and p["authority_activated"] is False and p["execution_performed"] is False
    x=deepcopy(a); x["payload"]["authority_activated"]=True
    assert not c.verify(x,ART)
    x=deepcopy(a); x["payload"]["occ1d_opened"]=True
    assert not c.verify(x,ART)
    x=deepcopy(a); x["payload"]["readiness_counts"]["SATISFIED"]=24
    assert not c.verify(x,ART)
    with tempfile.TemporaryDirectory() as td:
        d=Path(td)
        for n in c.REQUIRED_FILES: shutil.copy2(ART/n,d/n)
        (d/"bounded_gaps_evidence_v1.json").unlink()
        assert c.build(d)["status"]=="FAIL"
    print("P159_OCC1C_CLOSING_TRANSACTION_FUNCTIONAL_OK")
    print("P159_OCC1C_CLOSING_TRANSACTION_DETERMINISM_OK")
    print("P159_OCC1C_CLOSING_TRANSACTION_READINESS_25_OF_25_REQUIRED")
    print("P159_OCC1C_CLOSING_TRANSACTION_MISSING_EVIDENCE_REJECTED")
    print("P159_OCC1C_CLOSING_TRANSACTION_AUTHORITY_INFLATION_REJECTED")
    print("P159_OCC1C_CLOSING_TRANSACTION_OCC1D_OPENING_REJECTED")
    print("P159_OCC1C_CLOSING_TRANSACTION_STAGE_BOUNDARY_OK")
if __name__=="__main__": run()
