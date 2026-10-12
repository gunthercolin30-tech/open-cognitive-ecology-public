from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine
c=build_context(); c["forecast_horizons"]=[float("nan"),float("inf"),-1,0,1,999999]
c["trend_signals"].update({"stability":float("nan"),"resilience":float("inf"),"diversity":-float("inf")})
r=EcologicalPredictionEngine().step(c,False)
assert r["forecast_horizon"]==[1]
for row in r["ecological_forecast"]:
 for v in row["predicted_values"].values(): assert 0.0<=v<=1.0
print("AW12_NUMERIC_ROBUSTNESS_OK")
