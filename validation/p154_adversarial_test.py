from pathlib import Path
import sys,copy
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p154_cardinal_economic_hypotheses import preregister,evaluate
from validation.p154_test_support import reg,evidence
try:
 preregister(hypothesis_id="H7",protocol="x",baseline={"name":"b","provenance":"p"},target_family="f",next_reevaluation_date="d",preregistered_at="t"); raise AssertionError
except ValueError: pass
r=reg("H2"); bad=copy.deepcopy(r); bad["threshold"]=-999
try: evaluate(bad,evidence(r)); raise AssertionError
except ValueError: pass
try: evaluate(r,evidence(r,hypothesis_id="H3")); raise AssertionError
except ValueError: pass
print("P154_ADVERSARIAL_OK")
