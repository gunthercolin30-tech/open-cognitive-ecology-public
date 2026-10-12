from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from ontology.cognitive_economic_efficiency import CognitiveEconomicEfficiency
from validation.p151_test_support import value,costs
e=CognitiveEconomicEfficiency(); assert e.evaluate(verified_economic_value=None,costs=costs(),unit="EUR",period_id="T")["status"]=="UNKNOWN"
assert e.evaluate(verified_economic_value=value(),costs=costs(0),unit="EUR",period_id="T")["status"]=="UNDEFINED_ZERO_COST"
c=costs(); c["energy"]["unit"]="USD"
try:e.evaluate(verified_economic_value=value(),costs=c,unit="EUR",period_id="T")
except ValueError:pass
else:raise AssertionError("mixed units accepted")
v=value(); v["provenance"]=""
try:e.evaluate(verified_economic_value=v,costs=costs(),unit="EUR",period_id="T")
except ValueError:pass
else:raise AssertionError("unproven value accepted")
r=e.evaluate(verified_economic_value=value(),costs=costs(),unit="EUR",period_id="T"); assert e.trend([r])["status"]=="UNKNOWN"
print("P151_ADVERSARIAL_CROWN_OK")
