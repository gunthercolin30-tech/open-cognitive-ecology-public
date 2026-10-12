from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p005_product_market_evidence_ladder import ProductMarketEvidenceLadder
from validation.p005_test_support import record
o=ProductMarketEvidenceLadder().evaluate(record())
assert o["highest_attained_level"]=="M9" and o["claim_authorized"] and o["market_priority_authorized"]
assert o["functional_conclusion_only"] and o["phenomenology_undetermined"]
print("P005_FUNCTIONAL_OK")
