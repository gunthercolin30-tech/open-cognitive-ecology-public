from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from ontology.strategy_selection import StrategySelection, PRIMITIVE_NAME, MATURITY_LEVEL
s=StrategySelection()
r=s.evaluate(prioritization=.7,decision_making=.8,goal_directedness=.6,controllability=.9)
assert PRIMITIVE_NAME=="STRATEGY_SELECTION" and MATURITY_LEVEL=="FOUNDATIONAL_COMPLETE"
assert 0 <= r["strategy_selection_index"] <= 1
assert s.validate(prioritization=.7,decision_making=.8,goal_directedness=.6,controllability=.9)["valid"]
print("P002_NON_REGRESSION_OK")
