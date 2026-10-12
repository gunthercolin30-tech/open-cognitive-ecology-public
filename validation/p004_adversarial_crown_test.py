from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from validation.p004_evidence_ladder import EvidenceLadder
from validation.p004_test_support import record
R=EvidenceLadder()
# High-level evidence cannot leapfrog a missing lower level.
x=record(); x["evidence"]["E1"]["satisfied"]=False
o=R.evaluate(x); assert o["highest_attained_level"]=="E0" and not any(v["attained"] for v in o["levels"][2:])
# A supported lower claim remains authorized even when higher levels are unknown.
x=record(5,claimed="E4"); o=R.evaluate(x); assert o["claim_authorized"] and o["highest_attained_level"]=="E4"
# Low-confidence payment cannot authorize E9+.
x=record(); x["evidence"]["E9"]["confidence"]=0.1
o=R.evaluate(x); assert o["highest_attained_level"]=="E8" and not o["claim_authorized"]
# Explicit negative evidence blocks all later promotion.
x=record(); x["evidence"]["E10"]["satisfied"]=False
o=R.evaluate(x); assert o["highest_attained_level"]=="E9" and not o["levels"][11]["attained"]
print("P004_ADVERSARIAL_CROWN_OK")
