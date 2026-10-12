from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from ontology.strategy_selection import StrategySelection
r=StrategySelection().select_minimal_sufficient([{"candidate_id":"a","quality":.9,"risk":.1,"governance_admissible":True,"constraints_satisfied":True,"execution_cost":2,"coordination_cost":1,"governance_cost":1,"maintenance_cost":1},{"candidate_id":"b","quality":.9,"risk":.1,"governance_admissible":True,"constraints_satisfied":True,"execution_cost":3,"coordination_cost":1,"governance_cost":1,"maintenance_cost":1}],minimum_quality=.8,maximum_risk=.2)
assert r["selected_candidate"]["candidate_id"]=="a"
print("P151_P002_NON_REGRESSION_OK")
