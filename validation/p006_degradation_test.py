from pathlib import Path
import sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p006_go_rethink_stop import preregister,open_campaign,evaluate
from validation.p006_test_support import criteria,observations

with tempfile.TemporaryDirectory() as d:
    reg=preregister(criteria(),Path(d),"2026-09-15T12:00:00+00:00")
    camp=open_campaign(reg,Path(d),"2026-09-15T12:01:00+00:00")
    x=observations(reg["criteria_hash"],camp); x["values"].pop("needs_change")
    o=evaluate(reg,x)
    assert o["decision"]=="RETHINK" and o["reason"]=="UNKNOWN_OR_INCOMPLETE_EVIDENCE"
print("P006_DEGRADATION_OK")
