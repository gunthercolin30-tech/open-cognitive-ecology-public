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
    # Criteria cannot be rewritten after registration.
    tampered=copy.deepcopy(reg); tampered["criteria"]["conditions"][0]["severity"]="INFO"
    try: evaluate(tampered,observations(reg["criteria_hash"],camp))
    except ValueError: pass
    else: raise AssertionError("tampered criteria accepted")
    # Evidence must bind to the preregistration hash.
    x=observations("0"*64,camp)
    try: evaluate(reg,x)
    except ValueError: pass
    else: raise AssertionError("unbound evidence accepted")
    # Precedence: STOP > RETHINK > CHANGE.
    x=observations(reg["criteria_hash"],camp,needs_change=True,confidence_collapse=True,hard_safety_failure=True)
    assert evaluate(reg,x)["decision"]=="STOP_COMPONENT"
print("P006_ADVERSARIAL_OK")
