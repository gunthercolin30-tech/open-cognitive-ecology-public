from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p154_cardinal_economic_hypotheses import evaluate
from validation.p154_test_support import reg,evidence
r=reg("H1")
o=evaluate(r,evidence(r,-0.1,external_signal=False)); assert o["status"]=="UNKNOWN" and o["decision"]=="RETHINK"
o=evaluate(r,evidence(r,-0.1)); assert o["status"]=="NOT_SUPPORTED" and o["decision"]=="RETHINK"
o=evaluate(r,evidence(r,-0.1,durable_failure=True)); assert o["status"]=="DURABLY_FALSIFIED" and o["decision"]=="STOP_COMPONENT"
print("P154_DEGRADATION_OK")
