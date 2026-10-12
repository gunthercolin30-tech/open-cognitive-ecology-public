from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p005_product_market_evidence_ladder import ProductMarketEvidenceLadder
from validation.p005_test_support import record
R=ProductMarketEvidenceLadder()
def bind(x,start=1,end=9):
    for i in range(start,end+1):
        level=f"M{i}"; ref=x["market_evidence"][level]["evidence_refs"][0]
        x["market_evidence"][level]["external_evidence"]={"origin_type":"external_observation","origin_id":f"origin-{level}","observed_at":"2026-09-15T12:00:00Z","artifact_ref":ref}
    return x
x=record("M1"); x["market_evidence"]["M1"].pop("external_evidence",None); o=R.evaluate(x)
assert o["highest_attained_level"]=="M0" and o["levels"][1]["reason"]=="external_evidence_provenance_required" and not o["market_priority_authorized"]
print("P005_EXTERNAL_SELF_DECLARATION_REJECTED_OK")
x=bind(record("M1"),1,1); x["market_evidence"]["M1"]["external_evidence"]["origin_type"]="oce_internal"
assert R.evaluate(x)["highest_attained_level"]=="M0"
print("P005_EXTERNAL_INTERNAL_ORIGIN_REJECTED_OK")
for missing in ("origin_id","observed_at","artifact_ref"):
    x=bind(record("M1"),1,1); x["market_evidence"]["M1"]["external_evidence"].pop(missing)
    assert R.evaluate(x)["highest_attained_level"]=="M0"
print("P005_EXTERNAL_INCOMPLETE_PROVENANCE_REJECTED_OK")
x=bind(record("M1"),1,1); x["market_evidence"]["M1"]["external_evidence"]["artifact_ref"]="artifact:not-present"
assert R.evaluate(x)["highest_attained_level"]=="M0"
print("P005_EXTERNAL_UNBOUND_ARTIFACT_REJECTED_OK")
x=bind(record("M9"),1,9); o=R.evaluate(x)
assert o["highest_attained_level"]=="M9" and o["claim_authorized"] and o["market_priority_authorized"]
print("P005_EXTERNAL_STRUCTURED_PROVENANCE_OK")
x=record("M0")
for i in range(1,10): x["market_evidence"].pop(f"M{i}")
o=R.evaluate(x); assert o["highest_attained_level"]=="M0" and o["claim_authorized"] and not o["market_priority_authorized"]
print("P005_EXTERNAL_M0_HYPOTHESIS_OK")
print("P005_EXTERNAL_EVIDENCE_INTEGRITY_CROWN_OK")
