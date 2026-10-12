from copy import deepcopy
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_normative_ir_closure_audit as a
SOURCE=ROOT/"normative"/"occ1a"

def run():
    x=a.audit(SOURCE); y=a.audit(SOURCE)
    assert x["status"]==a.PASS,x
    assert x["decision"]=="READY_TO_CLOSE",x
    r=x["report"]
    assert r["requirements_total"]==27,r
    assert r["satisfied_count"]==25,r
    assert r["bounded_count"]==2,r
    assert r["missing_count"]==0,r
    assert r["bounded_requirements"]==["C08","C09"],r
    assert r["missing_requirements"]==[],r
    assert r["closure_performed"] is False
    assert r["occ1b_closed"] is False
    assert r["occ1c_opened"] is False and r["p160_opened"] is False
    assert r["authority_activated"] is False and r["execution_performed"] is False
    assert r["p159_final_lock_performed"] is False
    assert x["report_sha256"]==y["report_sha256"]
    assert a.verify_report(r)["status"]==a.PASS
    tam=deepcopy(r); tam["decision"]="NOT_READY_TO_CLOSE"
    assert a.verify_report(tam)["status"]==a.FAIL
    print("P159_OCC1B_CLOSURE_AUDIT_27_OF_27_ACCOUNTED_OK")
    print("P159_OCC1B_CLOSURE_AUDIT_25_SATISFIED_2_BOUNDED_OK")
    print("P159_OCC1B_CLOSURE_AUDIT_ZERO_MISSING_OK")
    print("P159_OCC1B_CLOSURE_AUDIT_SCOPE_TEMPORAL_LIMITS_PRESERVED_OK")
    print("P159_OCC1B_CLOSURE_AUDIT_TAMPER_DETECTED")
    print("P159_OCC1B_CLOSURE_AUDIT_DETERMINISM_OK")
    print("P159_OCC1B_CLOSURE_AUDIT_STAGE_BOUNDARY_OK")
    print("P159_OCC1B_READY_TO_CLOSE")
if __name__=="__main__": run()
