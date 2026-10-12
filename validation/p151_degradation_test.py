from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from ontology.cognitive_economic_efficiency import CognitiveEconomicEfficiency
from validation.p151_test_support import value,costs
e=CognitiveEconomicEfficiency(); c=costs(); del c["energy"]; r=e.evaluate(verified_economic_value=value(),costs=c,unit="EUR",period_id="T"); assert r["status"]=="UNKNOWN" and r["cee"] is None
c=costs(); c["api"]["measured"]=False; assert e.evaluate(verified_economic_value=value(),costs=c,unit="EUR",period_id="T")["status"]=="UNKNOWN"
print("P151_DEGRADATION_OK")
