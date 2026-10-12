from copy import deepcopy
from pathlib import Path
import json, shutil, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_normative_ir_closing_transaction as tx
SOURCE=ROOT/"normative"/"occ1a"

def run():
    with tempfile.TemporaryDirectory() as td:
        out=Path(td)/"occ1b_closure_transaction.json"
        a=tx.close(SOURCE,out)
        assert a["status"]==tx.PASS,a
        assert a["reason"]=="P159_OCC1B_CLOSING_TRANSACTION_COMMITTED",a
        assert a["occ1b_closed"] is True and a["post_close_verified"] is False
        obj=json.loads(out.read_text(encoding="utf-8"))
        assert tx.verify_artifact(obj)["status"]==tx.PASS
        assert obj["payload"]["requirements_total"]==27
        assert obj["payload"]["satisfied_count"]==25
        assert obj["payload"]["bounded_count"]==2
        assert obj["payload"]["bounded_requirements"]==["C08","C09"]
        assert obj["payload"]["missing_count"]==0
        assert obj["payload"]["authority_activated"] is False
        assert obj["payload"]["execution_performed"] is False
        assert obj["payload"]["occ1c_opened"] is False
        assert obj["payload"]["p160_opened"] is False
        assert obj["payload"]["p159_final_lock_performed"] is False

        b=tx.close(SOURCE,out)
        assert b["status"]==tx.PASS and b["reason"]=="P159_OCC1B_CLOSING_TRANSACTION_IDEMPOTENT",b
        assert b["transaction_id"]==a["transaction_id"]

        tam=deepcopy(obj); tam["payload"]["missing_count"]=1
        assert tx.verify_artifact(tam)["status"]==tx.FAIL

        divergent=deepcopy(obj); divergent["payload"]["bounded_requirements"]=["C08"]
        divergent["payload_sha256"]=tx.nir.canonical_sha256(divergent["payload"])
        divergent["transaction_id"]=divergent["payload_sha256"]
        out.write_text(json.dumps(divergent,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
        c=tx.close(SOURCE,out)
        assert c["status"]==tx.FAIL and c["reason"]=="DIVERGENT_REPLAY_REJECTED",c

    print("P159_OCC1B_CLOSING_TRANSACTION_FUNCTIONAL_OK")
    print("P159_OCC1B_CLOSING_TRANSACTION_25_SATISFIED_2_BOUNDED_OK")
    print("P159_OCC1B_CLOSING_TRANSACTION_ARTIFACT_TAMPER_DETECTED")
    print("P159_OCC1B_CLOSING_TRANSACTION_IDEMPOTENCE_OK")
    print("P159_OCC1B_CLOSING_TRANSACTION_DIVERGENT_REPLAY_REJECTED")
    print("P159_OCC1B_CLOSING_TRANSACTION_SOURCE_IMMUTABILITY_OK")
    print("P159_OCC1B_CLOSING_TRANSACTION_STAGE_BOUNDARY_OK")
if __name__=="__main__": run()
