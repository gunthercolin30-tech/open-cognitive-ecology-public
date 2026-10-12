from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_constitutional_compiler_bounded_gaps as g
SRC=ROOT/"normative"/"occ1a"; PROOF=ROOT/"validation_artifacts"/"p159"/"occ1b"/"occ1b_postclose_verification.json"
COMP=ROOT/"ontology"/"occ_constitutional_compiler.py"
def run():
    a=g.build(SRC,PROOF,COMP); b=g.build(SRC,PROOF,COMP)
    assert a==b
    assert all(x["detected"] for x in a["evidence"]["proofs"])
    assert a["compile_report"]["cci_7_13_14_proven"] is True
    assert len(a["transformation_ledger"]["entries"])==48
    m=a["compiler_manifest"]
    assert m["compiler_sha256"] and m["self_certification"] is False and m["self_activation"] is False
    assert m["authorization_created"] is False and m["execution_performed"] is False
    assert all(d["sha256"] for d in m["dependencies"])
    print("P159_OCC1C_CCI7_DNA_BALANCING_ATTACK_DETECTED")
    print("P159_OCC1C_CCI13_CRITICAL_AMBIGUITY_ESCALATES")
    print("P159_OCC1C_CCI14_FAILURE_FAILS_CLOSED")
    print("P159_OCC1C_COMPILE_REPORT_ARTIFACT_READY")
    print("P159_OCC1C_TRANSFORMATION_LEDGER_ARTIFACT_READY")
    print("P159_OCC1C_COMPILER_MANIFEST_BUILD_IDENTITY_READY")
    print("P159_OCC1C_BOUNDED_GAPS_DETERMINISM_OK")
    print("P159_OCC1C_BOUNDED_GAPS_STAGE_BOUNDARY_OK")
if __name__=="__main__": run()
