from __future__ import annotations
from pathlib import Path
import json, tempfile
from ontology import occ_occ1a_atomic_closing_transaction as q
ROOT=Path(__file__).resolve().parents[1]

def main():
    plan=q.prepare(ROOT)
    assert plan["status"]=="PREPARED",plan
    tx=plan["transaction"]
    assert tx["occ1a_closed"] is True
    assert tx["occ1b_opened"] is False and tx["p160_opened"] is False
    assert tx["authority_activated"] is False and tx["execution_performed"] is False
    assert tx["final_lock_performed"] is False
    print("P159_OCC1A_ATOMIC_CLOSING_TRANSACTION_V1_PREPARE_OK")

    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"closure.json"
        try:
            q.commit(ROOT,p,expected_transaction_hash=tx["transaction_hash"],inject_failure=True)
            raise AssertionError("injected failure did not fail")
        except RuntimeError as e:
            assert "INJECTED_CLOSURE_FAILURE" in str(e)
        assert not p.exists()
        print("P159_OCC1A_ATOMIC_CLOSING_TRANSACTION_V1_ROLLBACK_OK")

        try:
            q.commit(ROOT,p,expected_transaction_hash="0"*64)
            raise AssertionError("drift did not fail")
        except RuntimeError as e:
            assert "PRECOMMIT_EVIDENCE_DRIFT" in str(e)
        assert not p.exists()
        print("P159_OCC1A_ATOMIC_CLOSING_TRANSACTION_V1_DRIFT_OK")

        a=q.commit(ROOT,p,expected_transaction_hash=tx["transaction_hash"])
        assert a["status"]=="COMMITTED" and a["occ1a_closed"] is True,a
        assert a["occ1b_opened"] is False and a["p160_opened"] is False
        assert a["authority_activated"] is False and a["execution_performed"] is False
        assert a["final_lock_performed"] is False
        v=q.verify_artifact(p,ROOT,True)
        assert v["valid"] is True and v["status"]=="COMMITTED_VALID",v
        print("P159_OCC1A_ATOMIC_CLOSING_TRANSACTION_V1_FUNCTIONAL_OK")
        print("P159_OCC1A_ATOMIC_CLOSING_TRANSACTION_V1_PERSISTENCE_OK")

        b=q.commit(ROOT,p)
        assert b["status"]=="COMMITTED_IDEMPOTENT" and b["idempotent"] is True,b
        print("P159_OCC1A_ATOMIC_CLOSING_TRANSACTION_V1_IDEMPOTENCE_OK")

        raw=json.loads(p.read_text(encoding="utf-8"))
        raw["transaction"]["occ1b_opened"]=True
        p.write_text(json.dumps(raw,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        bad=q.verify_artifact(p,ROOT,False)
        assert bad["valid"] is False and bad["status"]=="TAMPERED",bad
        print("P159_OCC1A_ATOMIC_CLOSING_TRANSACTION_V1_TAMPER_OK")

    p2=q.prepare(ROOT)
    assert p2["transaction"]["transaction_hash"]==tx["transaction_hash"]
    print("P159_OCC1A_ATOMIC_CLOSING_TRANSACTION_V1_DETERMINISM_OK")
    print("P159_OCC1A_ATOMIC_CLOSING_TRANSACTION_V1_STAGE_BOUNDARY_OK")
    print("P159_OCC1A_ATOMIC_CLOSING_TRANSACTION_V1_TEST_OK")
if __name__=="__main__": main()
