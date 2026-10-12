from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine
c=build_context(); a=EcologicalPredictionEngine().step(c,False)
c["forecast_horizons"]=[30,1,7,7]
b=EcologicalPredictionEngine().step(c,False)
assert a["prediction_hash"]==b["prediction_hash"]
print("AW12_ORDER_INVARIANCE_OK")
