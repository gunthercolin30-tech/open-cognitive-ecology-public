from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from validation.p004_evidence_ladder import EvidenceLadder
from validation.p004_test_support import record
R=EvidenceLadder()
a=R.evaluate(record(5,claimed="E4")); b=R.evaluate(record(5,claimed="E4"))
assert a==b and a["highest_attained_level"]=="E4" and a["claim_authorized"]
assert a["dependencies"]==[]
print("P004_NON_REGRESSION_OK")
