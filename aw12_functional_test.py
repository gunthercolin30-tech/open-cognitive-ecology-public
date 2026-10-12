from copy import deepcopy
from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine
c=build_context(); e=EcologicalPredictionEngine()
a=e.step(c,False); b=e.step(deepcopy(c),False)
assert a["prediction_hash"]==b["prediction_hash"]
assert a["ecological_forecast"]==b["ecological_forecast"]
changed=deepcopy(c); changed["trend_signals"]["stability"]=-0.8
z=e.step(changed,False)
assert z["prediction_hash"]!=a["prediction_hash"]
assert z["predicted_resilience"]==a["predicted_resilience"]
assert z["ecological_forecast"][-1]["predicted_values"]["stability"] < a["ecological_forecast"][-1]["predicted_values"]["stability"]
print("AW12_FUNCTIONAL_OK")
