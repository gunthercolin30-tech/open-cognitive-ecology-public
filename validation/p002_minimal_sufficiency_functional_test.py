from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from ontology.strategy_selection import StrategySelection
s=StrategySelection()
c=[
 {"candidate_id":"neural","candidate_type":"small_neural","quality":.95,"risk":.1,"governance_admissible":True,"constraints_satisfied":True,"execution_cost":8},
 {"candidate_id":"rule","candidate_type":"rule","quality":.82,"risk":.1,"governance_admissible":True,"constraints_satisfied":True,"execution_cost":1},
 {"candidate_id":"cache","candidate_type":"cache","quality":.60,"risk":.05,"governance_admissible":True,"constraints_satisfied":True,"execution_cost":.1},
]
r=s.select_minimal_sufficient(c,minimum_quality=.8,maximum_risk=.2)
assert r["status"]=="SELECTED" and r["selected_candidate"]["candidate_id"]=="rule"
assert r["functional_conclusion_only"] is True and r["phenomenology_undetermined"] is True
print("P002_FUNCTIONAL_OK")
