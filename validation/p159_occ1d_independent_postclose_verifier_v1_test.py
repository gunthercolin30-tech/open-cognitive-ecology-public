from pathlib import Path
from copy import deepcopy
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_static_constitutional_checker_postclose_verifier as v

def run():
    a=v.verify_postclose(ROOT); b=v.verify_postclose(ROOT)
    assert a["status"]=="PASS",a
    assert a==b and v.verify_proof(a,ROOT)
    p=a["payload"]
    assert p["closure_transaction_id"]==v.EXPECTED_TRANSACTION_ID
    assert p["closure_revalidated"] is True
    assert p["static_decision_preserved"]=="STATIC_UNRESOLVED"
    assert p["bounded_unresolved_phases"]==["S7","S8","S10"]
    assert p["missing_check_mechanisms"]==0 and p["genuine_adversarial_gaps"]==0
    assert p["occ1d_closed"] is True and p["postclose_verified"] is True
    assert p["occ1e_opened"] is False and p["p160_opened"] is False and p["p159_final_lock"] is False
    assert p["authorization_created"] is False and p["authority_activated"] is False and p["execution_performed"] is False

    for key,val in [
      ("occ1e_opened",True),("p160_opened",True),("p159_final_lock",True),
      ("authority_activated",True),("execution_performed",True),
      ("genuine_adversarial_gaps",1)]:
        x=deepcopy(a); x["payload"][key]=val
        assert not v.verify_proof(x,ROOT)

    x=deepcopy(a); x["payload"]["bounded_unresolved_phases"]=["S7","S8"]
    assert not v.verify_proof(x,ROOT)

    print("P159_OCC1D_POSTCLOSE_FUNCTIONAL_OK")
    print("P159_OCC1D_POSTCLOSE_TRANSACTION_ID_VERIFIED")
    print("P159_OCC1D_POSTCLOSE_CLOSURE_REVALIDATED_OK")
    print("P159_OCC1D_POSTCLOSE_UNRESOLVED_S7_S8_S10_PRESERVED_OK")
    print("P159_OCC1D_POSTCLOSE_GAP_REINTRODUCTION_DETECTED")
    print("P159_OCC1D_POSTCLOSE_AUTHORITY_INFLATION_DETECTED")
    print("P159_OCC1D_POSTCLOSE_STAGE_BOUNDARY_OK")
    print("P159_OCC1D_POSTCLOSE_DETERMINISM_OK")
    print("P159_OCC1D_POSTCLOSE_VERIFICATION_VERIFIED")
if __name__=="__main__": run()
