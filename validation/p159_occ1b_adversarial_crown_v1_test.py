from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_normative_ir_adversarial_crown as c
SOURCE=ROOT/"normative"/"occ1a"

def run():
    a=c.run_crown(SOURCE); b=c.run_crown(SOURCE)
    assert a["status"]==c.PASS,a
    r=a["report"]
    assert r["attack_count"]==18,r
    assert r["attack_detected_count"]==18,r
    assert r["control_count"]==4,r
    assert r["control_pass_count"]==4,r
    assert r["false_negatives"]==[],r
    assert r["control_failures"]==[],r
    assert r["source_package_mutated"] is False
    assert r["niri_6_scope_real_source_claim"]=="BOUNDED_NOT_APPLICABLE_SOURCE_ABSENT"
    assert r["niri_7_temporal_real_source_claim"]=="BOUNDED_NOT_APPLICABLE_SOURCE_ABSENT"
    assert a["report_sha256"]==b["report_sha256"]
    assert r["authority_activated"] is False and r["execution_performed"] is False
    assert r["occ1c_opened"] is False and r["p160_opened"] is False
    assert r["final_lock_performed"] is False
    print("P159_OCC1B_ADVERSARIAL_CROWN_18_OF_18_DETECTED_OK")
    print("P159_OCC1B_ADVERSARIAL_CROWN_4_OF_4_CONTROLS_OK")
    print("P159_OCC1B_ADVERSARIAL_CROWN_NO_FALSE_NEGATIVES_OK")
    print("P159_OCC1B_ADVERSARIAL_CROWN_NO_CONTROL_FAILURES_OK")
    print("P159_OCC1B_ADVERSARIAL_CROWN_SOURCE_IMMUTABILITY_OK")
    print("P159_OCC1B_ADVERSARIAL_CROWN_NIRI_6_7_BOUNDS_PRESERVED_OK")
    print("P159_OCC1B_ADVERSARIAL_CROWN_DETERMINISM_OK")
    print("P159_OCC1B_ADVERSARIAL_CROWN_STAGE_BOUNDARY_OK")
if __name__=="__main__": run()
