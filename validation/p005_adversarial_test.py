from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p005_product_market_evidence_ladder import ProductMarketEvidenceLadder
from validation.p005_test_support import record
R=ProductMarketEvidenceLadder()
x=record("M1"); x["market_evidence"]["M1"]["source"]="internal"; o=R.evaluate(x)
assert o["highest_attained_level"]=="M0" and not o["market_priority_authorized"]
x=record("M1"); x["market_evidence"]["M1"]["confidence"]=float("nan"); assert R.evaluate(x)["highest_attained_level"]=="M0"
x=record("M4"); x["market_evidence"]["M4"]["evidence_refs"]=["market_claim:market-alpha"]; assert R.evaluate(x)["highest_attained_level"]=="M3"
x=record("M6"); x["market_evidence"]["M6"]["refutation_refs"]=["artifact:non-renewal"]; assert R.evaluate(x)["highest_attained_level"]=="M5"
print("P005_ADVERSARIAL_OK")
