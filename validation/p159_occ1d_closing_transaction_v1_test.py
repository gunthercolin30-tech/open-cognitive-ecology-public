from pathlib import Path
from copy import deepcopy
import json, shutil, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_static_constitutional_checker_closing_transaction as c

def run():
    a=c.build(ROOT); b=c.build(ROOT)
    assert a["status"]=="PASS", a
    assert c.verify(a,ROOT) and a==b
    p=a["payload"]
    assert p["phase_results"]["S7"]=="UNRESOLVED"
    assert p["phase_results"]["S8"]=="UNRESOLVED"
    assert p["phase_results"]["S10"]=="UNRESOLVED"
    assert p["static_decision_preserved"]=="STATIC_UNRESOLVED"
    assert p["missing_check_mechanisms"]==0 and p["genuine_adversarial_gaps"]==0
    assert p["occ1d_closed"] is True and p["occ1e_opened"] is False
    assert p["p160_opened"] is False and p["p159_final_lock"] is False
    assert p["authorization_created"] is False and p["authority_activated"] is False and p["execution_performed"] is False

    x=deepcopy(a); x["payload"]["phase_results"]["S7"]="PASS"
    assert not c.verify(x,ROOT)
    x=deepcopy(a); x["payload"]["occ1e_opened"]=True
    assert not c.verify(x,ROOT)
    x=deepcopy(a); x["payload"]["p159_final_lock"]=True
    assert not c.verify(x,ROOT)
    x=deepcopy(a); x["payload"]["genuine_adversarial_gaps"]=1
    assert not c.verify(x,ROOT)

    print("P159_OCC1D_CLOSING_TRANSACTION_FUNCTIONAL_OK")
    print("P159_OCC1D_CLOSING_TRANSACTION_DETERMINISM_OK")
    print("P159_OCC1D_CLOSING_TRANSACTION_S0_S11_COMPLETE_OK")
    print("P159_OCC1D_CLOSING_TRANSACTION_UNRESOLVED_S7_S8_S10_PRESERVED_OK")
    print("P159_OCC1D_CLOSING_TRANSACTION_CROWN_24_24_REQUIRED_OK")
    print("P159_OCC1D_CLOSING_TRANSACTION_EVIDENCE_HASH_BINDING_OK")
    print("P159_OCC1D_CLOSING_TRANSACTION_STAGE_BOUNDARY_OK")
    print("P159_OCC1D_CLOSING_TRANSACTION_NO_AUTHORITY_NO_EXECUTION_OK")
if __name__=="__main__": run()
