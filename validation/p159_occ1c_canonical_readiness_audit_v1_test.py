from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_constitutional_compiler_canonical_readiness_audit as a
SRC=ROOT/"normative"/"occ1a"
PROOF=ROOT/"validation_artifacts"/"p159"/"occ1b"/"occ1b_postclose_verification.json"
def run():
    x=a.audit(SRC,PROOF); y=a.audit(SRC,PROOF)
    assert x["status"]=="PASS",x
    p=x["payload"]
    assert p["decision"]=="OCC1C_NOT_READY_TO_CLOSE",p
    assert p["counts"]=={"SATISFIED":19,"BOUNDED":6,"MISSING":0},p["counts"]
    assert p["cci"]["CCI-7"]["status"]=="BOUNDED"
    assert p["cci"]["CCI-13"]["status"]=="BOUNDED"
    assert p["cci"]["CCI-14"]["status"]=="BOUNDED"
    assert p["artifacts"]["ART-4_COMPILE_REPORT"]["status"]=="BOUNDED"
    assert p["artifacts"]["ART-5_TRANSFORMATION_LEDGER"]["status"]=="BOUNDED"
    assert p["artifacts"]["ART-6_COMPILER_MANIFEST"]["status"]=="BOUNDED"
    assert all(v["status"]=="SATISFIED" for v in p["closure_criteria"].values())
    assert x["audit_sha256"]==y["audit_sha256"]
    assert p["occ1c_closed"] is False and p["occ1d_opened"] is False and p["p160_opened"] is False
    print("P159_OCC1C_READINESS_AUDIT_FUNCTIONAL_OK")
    print("P159_OCC1C_CCI_15_ACCOUNTED_OK")
    print("P159_OCC1C_ARTIFACTS_6_ACCOUNTED_OK")
    print("P159_OCC1C_CLOSURE_CRITERIA_4_ACCOUNTED_OK")
    print("P159_OCC1C_READINESS_SATISFIED_19_BOUNDED_6_MISSING_0")
    print("P159_OCC1C_READINESS_DECISION_NOT_READY_TO_CLOSE")
    print("P159_OCC1C_READINESS_DETERMINISM_OK")
    print("P159_OCC1C_READINESS_STAGE_BOUNDARY_OK")
if __name__=="__main__": run()
