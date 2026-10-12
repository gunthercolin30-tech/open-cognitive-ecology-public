from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from ontology import occ_normative_ir_niri_consolidation as c
SOURCE=ROOT/"normative"/"occ1a"

def run():
    a=c.consolidate(SOURCE); b=c.consolidate(SOURCE)
    assert a["status"]==c.PASS,a
    r=a["report"]
    assert r["all_14_accounted"] is True
    assert len(r["rows"])==14
    assert r["pass_count"]==12 and r["bounded_count"]==2 and r["fail_count"]==0,r
    assert r["bounded_invariants"]==["NIRI-6","NIRI-7"]
    assert r["all_14_unqualified_pass_claimed"] is False
    assert r["bounded_claims_preserved"] is True
    assert a["report_sha256"]==b["report_sha256"]
    assert c.verify_report(r)["status"]==c.PASS

    tam=deepcopy(r); tam["rows"][0]["status"]="FAIL"
    assert c.verify_report(tam)["status"]==c.FAIL

    byid={x["invariant_id"]:x for x in r["rows"]}
    assert byid["NIRI-6"]["status"]==c.BOUNDED
    assert "no positive no-widening proof claimed" in byid["NIRI-6"]["limitation"]
    assert byid["NIRI-7"]["status"]==c.BOUNDED
    assert "no positive no-weakening proof claimed" in byid["NIRI-7"]["limitation"]

    for i in ("NIRI-1","NIRI-2","NIRI-3","NIRI-4","NIRI-5","NIRI-8","NIRI-9",
              "NIRI-10","NIRI-11","NIRI-12","NIRI-13","NIRI-14"):
        assert byid[i]["status"]==c.PASS,(i,byid[i])
        assert byid[i]["evidence"],i

    assert r["authority_activated"] is False and r["execution_performed"] is False
    assert r["occ1c_opened"] is False and r["p160_opened"] is False
    assert r["final_lock_performed"] is False

    print("P159_OCC1B_NIRI_14_OF_14_ACCOUNTED_OK")
    print("P159_OCC1B_NIRI_12_EVIDENCE_BACKED_PASS_OK")
    print("P159_OCC1B_NIRI_6_SCOPE_BOUNDED_OK")
    print("P159_OCC1B_NIRI_7_TEMPORAL_BOUNDED_OK")
    print("P159_OCC1B_NIRI_NO_UNQUALIFIED_14_PASS_OK")
    print("P159_OCC1B_NIRI_REPORT_TAMPER_DETECTED")
    print("P159_OCC1B_NIRI_DETERMINISM_OK")
    print("P159_OCC1B_NIRI_STAGE_BOUNDARY_OK")
if __name__=="__main__": run()
