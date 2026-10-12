from pathlib import Path
import sys,math
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from validation.p004_evidence_ladder import EvidenceLadder
from validation.p004_test_support import record
R=EvidenceLadder()
for bad in (None,[],42):
    try: R.evaluate(bad)
    except ValueError: pass
    else: raise AssertionError("invalid payload accepted")
x=record(); x["evidence"]["E0"]["confidence"]=float("nan")
assert R.evaluate(x)["highest_attained_level"] is None
x=record(); x["evidence"]["E3"]["evidence_refs"]=[]
assert R.evaluate(x)["highest_attained_level"]=="E2"
x=record(n=4,claimed="E11"); o=R.evaluate(x)
assert o["highest_attained_level"]=="E3" and not o["claim_authorized"]
x=record(); x["claimed_level"]="E12"
try: R.evaluate(x)
except ValueError: pass
else: raise AssertionError("E12 accepted")
print("P004_ADVERSARIAL_OK")
