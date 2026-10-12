from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from ontology.cognitive_economic_efficiency import CognitiveEconomicEfficiency
from validation.p151_test_support import value,costs
e=CognitiveEconomicEfficiency(); a=e.evaluate(verified_economic_value=value(),costs=costs(),unit="EUR",period_id="T1"); b=e.evaluate(verified_economic_value=value(160),costs=costs(),unit="EUR",period_id="T2")
assert a["status"]=="COMPUTED" and a["total_cognitive_cost"]==80 and a["cee"]==1.5 and e.trend([a,b])["cee_t_increasing"] is True
print("P151_FUNCTIONAL_OK")
