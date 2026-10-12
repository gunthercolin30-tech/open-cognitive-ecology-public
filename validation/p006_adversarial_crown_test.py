from pathlib import Path
import sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p006_go_rethink_stop import preregister,open_campaign,evaluate
from validation.p006_test_support import criteria,observations

import copy
with tempfile.TemporaryDirectory() as d:
    reg=preregister(criteria(),Path(d),"2026-09-15T12:00:00+00:00")
    camp=open_campaign(reg,Path(d),"2026-09-15T12:01:00+00:00")
    # Unknown never silently becomes GO.
    for key in ("needs_change","confidence_collapse","hard_safety_failure"):
        x=observations(reg["criteria_hash"],camp); x["values"][key]=None
        assert evaluate(reg,x)["decision"]=="RETHINK"
    # Invalid non-boolean evidence rejected.
    x=observations(reg["criteria_hash"],camp); x["values"]["needs_change"]=1
    try: evaluate(reg,x)
    except ValueError: pass
    else: raise AssertionError("integer accepted as boolean evidence")
    # Deterministic under value-map permutation.
    a=observations(reg["criteria_hash"],camp,needs_change=True)
    b=copy.deepcopy(a); b["values"]=dict(reversed(list(b["values"].items())))
    assert evaluate(reg,a)==evaluate(reg,b)
    # Higher constraints dominate bounded change.
    x=observations(reg["criteria_hash"],camp,needs_change=True,confidence_collapse=True)
    assert evaluate(reg,x)["decision"]=="RETHINK"
print("P006_ADVERSARIAL_CROWN_OK")
