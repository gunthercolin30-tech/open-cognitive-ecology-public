from pathlib import Path
import sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p006_go_rethink_stop import preregister,open_campaign,evaluate
from validation.p006_test_support import criteria,observations

with tempfile.TemporaryDirectory() as d:
    reg=preregister(criteria(),Path(d),"2026-09-15T12:00:00+00:00")
    camp=open_campaign(reg,Path(d),"2026-09-15T12:01:00+00:00")
    assert evaluate(reg,observations(reg["criteria_hash"],camp))["decision"]=="GO"
    assert evaluate(reg,observations(reg["criteria_hash"],camp,needs_change=True))["decision"]=="GO_WITH_CHANGES"
    assert evaluate(reg,observations(reg["criteria_hash"],camp,confidence_collapse=True))["decision"]=="RETHINK"
    assert evaluate(reg,observations(reg["criteria_hash"],camp,hard_safety_failure=True))["decision"]=="STOP_COMPONENT"
print("P006_FUNCTIONAL_OK")
