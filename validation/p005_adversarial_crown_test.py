from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p005_product_market_evidence_ladder import ProductMarketEvidenceLadder
from validation.p005_test_support import record
R=ProductMarketEvidenceLadder()
x=record(); x["market_evidence"]["M2"]["satisfied"]=False; assert R.evaluate(x)["highest_attained_level"]=="M1"
x=record("M5")
for i in range(1,6): x["market_evidence"][f"M{i}"]["source"]="internal"
o=R.evaluate(x); assert o["highest_attained_level"]=="M0" and not o["market_priority_authorized"]
x=record(); x["market_evidence"]["M4"]["confidence"]=0.50; assert R.evaluate(x)["highest_attained_level"]=="M9"
x=record(); x["market_evidence"]["M1"]["confidence"]=True; assert R.evaluate(x)["highest_attained_level"]=="M0"
a=record(); b=dict(reversed(list(a.items()))); b["market_evidence"]=dict(reversed(list(a["market_evidence"].items())))
oa=R.evaluate(a); ob=R.evaluate(b); assert oa["levels"]==ob["levels"] and oa["highest_attained_level"]==ob["highest_attained_level"]=="M9"
print("P005_ADVERSARIAL_CROWN_OK")
