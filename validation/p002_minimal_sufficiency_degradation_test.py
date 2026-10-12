from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from ontology.strategy_selection import StrategySelection
s=StrategySelection()
base={"quality":.9,"risk":.1,"constraints_satisfied":True}
r=s.select_minimal_sufficient([
 dict(base,candidate_id="cheap_bad_gov",governance_admissible=False,execution_cost=.01),
 dict(base,candidate_id="safe",governance_admissible=True,execution_cost=2),
],minimum_quality=.8,maximum_risk=.2)
assert r["selected_candidate"]["candidate_id"]=="safe"
none=s.select_minimal_sufficient([{"candidate_id":"bad","quality":.1,"risk":.9,"governance_admissible":False,"constraints_satisfied":False,"execution_cost":0}],minimum_quality=.8,maximum_risk=.2)
assert none["status"]=="NO_FEASIBLE_CANDIDATE" and none["selected_candidate"] is None
for bad in (float("nan"),float("inf"),-1):
    try:
        s.select_minimal_sufficient([{"candidate_id":"x","quality":.9,"risk":.1,"governance_admissible":True,"constraints_satisfied":True,"execution_cost":bad}],minimum_quality=.8,maximum_risk=.2)
    except ValueError: pass
    else: raise AssertionError("invalid cost accepted")
print("P002_DEGRADATION_OK")
