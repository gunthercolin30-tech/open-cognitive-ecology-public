from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from ontology.cognitive_economic_efficiency import CognitiveEconomicEfficiency
from validation.p151_test_support import value,costs
e=CognitiveEconomicEfficiency()
def reject(f):
 try:f()
 except ValueError:return
 raise AssertionError("invalid evidence accepted")
c=costs(); c["compute"]["amount"]=-1; reject(lambda:e.evaluate(verified_economic_value=value(),costs=c,unit="EUR",period_id="T"))
c=costs(); c["human"]["unit"]="USD"; reject(lambda:e.evaluate(verified_economic_value=value(),costs=c,unit="EUR",period_id="T"))
r=e.evaluate(verified_economic_value=value(verified=False),costs=costs(),unit="EUR",period_id="T"); assert r["status"]=="UNKNOWN"
print("P151_ADVERSARIAL_OK")
