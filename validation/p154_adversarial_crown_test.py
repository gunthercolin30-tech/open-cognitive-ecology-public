from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p154_cardinal_economic_hypotheses import evaluate
from validation.p154_test_support import reg,evidence
r=reg("H6")
for key,val in [("result",float("nan")),("confidence",1.1),("uncertainty",-0.1),("replications",0)]:
 try: evaluate(r,evidence(r,**{key:val})); raise AssertionError(key)
 except ValueError: pass
o=evaluate(r,evidence(r,verified=False)); assert o["decision"]=="RETHINK" and o["economic_hypothesis_empirically_proven"] is False
print("P154_ADVERSARIAL_CROWN_OK")
