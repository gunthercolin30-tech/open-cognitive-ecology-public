from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from ontology.strategy_selection import StrategySelection
s=StrategySelection()
c=[
 {"candidate_id":"b","quality":.9,"risk":.1,"governance_admissible":True,"constraints_satisfied":True,"execution_cost":1,"coordination_cost":1},
 {"candidate_id":"a","quality":.9,"risk":.1,"governance_admissible":True,"constraints_satisfied":True,"execution_cost":1,"coordination_cost":1},
 {"candidate_id":"cheap_risky","quality":1,"risk":.9,"governance_admissible":True,"constraints_satisfied":True,"execution_cost":0},
]
r1=s.select_minimal_sufficient(c,minimum_quality=.8,maximum_risk=.2)
r2=s.select_minimal_sufficient(list(reversed(c)),minimum_quality=.8,maximum_risk=.2)
assert r1["selected_candidate"]["candidate_id"]=="a" and r1==r2
d=[dict(x) for x in c[:2]]; d[1]["execution_cost"]=.5
assert s.select_minimal_sufficient(d,minimum_quality=.8,maximum_risk=.2)["selected_candidate"]["candidate_id"]=="a"
e=[
 {"candidate_id":"external","quality":.95,"risk":.1,"governance_admissible":True,"constraints_satisfied":True,"execution_cost":.1,"governance_cost":3,"maintenance_cost":1},
 {"candidate_id":"local","quality":.85,"risk":.1,"governance_admissible":True,"constraints_satisfied":True,"execution_cost":2},
]
assert s.select_minimal_sufficient(e,minimum_quality=.8,maximum_risk=.2)["selected_candidate"]["candidate_id"]=="local"
print("P002_ADVERSARIAL_OK")
