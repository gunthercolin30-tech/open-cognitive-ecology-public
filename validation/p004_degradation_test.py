from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from validation.p004_evidence_ladder import EvidenceLadder
from validation.p004_test_support import record
R=EvidenceLadder()
x=record(); x["evidence"]["E4"]["satisfied"]=False
o=R.evaluate(x); assert o["highest_attained_level"]=="E3" and not o["claim_authorized"]
x=record(); del x["evidence"]["E6"]
o=R.evaluate(x); assert o["highest_attained_level"]=="E5" and not o["levels"][7]["attained"]
x=record(); x["evidence"]["E2"]["confidence"]=0.49
o=R.evaluate(x); assert o["highest_attained_level"]=="E1"
print("P004_DEGRADATION_OK")
