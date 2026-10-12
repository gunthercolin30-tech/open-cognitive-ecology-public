from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p154_cardinal_economic_hypotheses import preregister
def reg(hid="H1",threshold=None):
    kw={} if threshold is None else {"threshold":threshold}
    return preregister(hypothesis_id=hid,protocol="synthetic P154 validation protocol",baseline={"name":"synthetic comparator","provenance":"synthetic_test_fixture"},target_family="synthetic_validation_family",next_reevaluation_date="2026-10-15",preregistered_at="2026-09-15T16:00:00+00:00",**kw)
def evidence(r,result=1.0,**overrides):
    d={"hypothesis_id":r["hypothesis_id"],"preregistration_hash":r["preregistration_hash"],"verified":True,"external_signal":True,"provenance":"synthetic_test_fixture","result":result,"confidence":0.9,"uncertainty":0.1,"replications":2,"durable_failure":False}
    d.update(overrides); return d
