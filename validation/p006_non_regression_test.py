from pathlib import Path
import sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p006_go_rethink_stop import preregister,open_campaign,evaluate
from validation.p006_test_support import criteria,observations

from validation.p006_go_rethink_stop import DECISIONS
assert DECISIONS==("GO","GO_WITH_CHANGES","RETHINK","STOP_COMPONENT")
with tempfile.TemporaryDirectory() as d:
    reg=preregister(criteria(),Path(d),"2026-09-15T12:00:00+00:00")
    camp=open_campaign(reg,Path(d),"2026-09-15T12:01:00+00:00")
    reg2=preregister(criteria(),Path(d),"2099-01-01T00:00:00+00:00")
    assert reg==reg2
    o=evaluate(reg,observations(reg["criteria_hash"],camp))
    assert o["functional_conclusion_only"] and o["phenomenology_undetermined"]
print("P006_NON_REGRESSION_OK")
