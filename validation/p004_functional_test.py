from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from validation.p004_evidence_ladder import EvidenceLadder,LEVELS
from validation.p004_test_support import record
r=EvidenceLadder().evaluate(record())
assert r["highest_attained_level"]=="E11" and r["claim_authorized"]
assert [x["level"] for x in r["levels"]]==[x[0] for x in LEVELS]
assert r["functional_conclusion_only"] and r["phenomenology_undetermined"]
print("P004_FUNCTIONAL_OK")
