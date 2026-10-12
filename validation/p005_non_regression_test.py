from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p005_product_market_evidence_ladder import ProductMarketEvidenceLadder,LEVELS
from validation.p005_test_support import record
assert tuple(x for x,_ in LEVELS)==tuple(f"M{i}" for i in range(10))
x=record("M0")
for i in range(1,10): x["market_evidence"].pop(f"M{i}")
o=ProductMarketEvidenceLadder().evaluate(x)
assert o["highest_attained_level"]=="M0" and o["claim_authorized"]
assert not o["market_priority_authorized"] and not o["external_market_signal_present"]
print("P005_NON_REGRESSION_OK")
