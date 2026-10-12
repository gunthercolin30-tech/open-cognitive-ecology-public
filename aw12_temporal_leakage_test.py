from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine
c=build_context(); c["issued_at"]="2026-07-13T08:00:00Z"; c["observed_at"]="2026-07-13T07:59:59Z"; c["observed_values"]={"stability":0.9}
r=EcologicalPredictionEngine().step(c,False)
assert r["temporal_leakage_detected"] is True
assert r["prediction_ready"] is False
assert all(x["a_posteriori_validation"]["validation_status"]=="TEMPORAL_LEAKAGE_BLOCKED" for x in r["ecological_forecast"])
print("AW12_TEMPORAL_LEAKAGE_OK")
