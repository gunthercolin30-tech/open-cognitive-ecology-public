from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p154_cardinal_economic_hypotheses import HYPOTHESES,evaluate,hypothesis_table
from validation.p154_test_support import reg,evidence
assert len(HYPOTHESES)==7 and [x["hypothesis_id"] for x in hypothesis_table()]==["H1","H2","H3","H4","H5","H6","H7"]
for hid in ("H1","H2","H3","H5","H6"):
    r=reg(hid); assert evaluate(r,evidence(r,1.0))["decision"]=="GO"
r=reg("H4"); assert r["threshold"]==1.0 and evaluate(r,evidence(r,1.1))["decision"]=="GO"
r=reg("H7",0.25); assert evaluate(r,evidence(r,0.30))["decision"]=="GO"
print("P154_FUNCTIONAL_OK")
