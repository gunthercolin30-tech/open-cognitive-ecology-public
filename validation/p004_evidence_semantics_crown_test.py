from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from validation.p004_evidence_ladder import EvidenceLadder,LEVELS
from validation.p004_test_support import record
R=EvidenceLadder()
x=record(); x["evidence"]["E3"]["confidence"]=0.50
o=R.evaluate(x); assert o["highest_attained_level"]=="E11" and o["claim_authorized"]
print("P004_SEMANTICS_THRESHOLD_BOUNDARY_OK")
x=record(); x["evidence"]["E2"]["confidence"]=True
o=R.evaluate(x); assert o["highest_attained_level"]=="E1"
print("P004_SEMANTICS_BOOL_CONFIDENCE_REJECTED_OK")
x=record(); x["evidence"]["E4"]["evidence_refs"]=["claim:c"]
o=R.evaluate(x); assert o["highest_attained_level"]=="E3" and not o["claim_authorized"] and o["levels"][4]["reason"]=="self_support_forbidden"
print("P004_SEMANTICS_SELF_SUPPORT_REJECTED_OK")
x=record(); x["evidence"]["E6"]["refutation_refs"]=["counterexample:ce-001"]
o=R.evaluate(x); assert o["highest_attained_level"]=="E5" and not o["claim_authorized"] and o["levels"][6]["reason"]=="explicit_refutation_present"
print("P004_SEMANTICS_REFUTATION_DOMINATES_OK")
assert tuple(level for level,_ in LEVELS)==tuple(f"E{i}" for i in range(12))
print("P004_SEMANTICS_CANONICAL_ORDER_OK")
a=record(); b=dict(reversed(list(a.items()))); b["evidence"]=dict(reversed(list(a["evidence"].items())))
oa=R.evaluate(a); ob=R.evaluate(b)
assert oa["highest_attained_level"]==ob["highest_attained_level"]=="E11" and oa["claim_authorized"]==ob["claim_authorized"]==True and oa["levels"]==ob["levels"]
print("P004_SEMANTICS_PERMUTATION_DETERMINISM_OK")
x=record(); x["evidence"]["E8"]["evidence_refs"]=["opaque:artifact-17"]
o=R.evaluate(x); assert o["levels"][8]["state"]=="SUPPORTED"
print("P004_SEMANTICS_OPAQUE_REF_SCOPE_EXPLICIT_OK")
print("P004_EVIDENCE_SEMANTICS_CROWN_OK")
