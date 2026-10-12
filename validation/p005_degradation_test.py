from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p005_product_market_evidence_ladder import ProductMarketEvidenceLadder
from validation.p005_test_support import record
x=record(); x["market_evidence"]["M3"]["satisfied"]=False
o=ProductMarketEvidenceLadder().evaluate(x)
assert o["highest_attained_level"]=="M2" and not o["claim_authorized"]
print("P005_DEGRADATION_OK")
