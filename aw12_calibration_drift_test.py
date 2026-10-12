from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine
c=build_context(); e=EcologicalPredictionEngine(); base=e.step(c,False)
c["observed_at"]="2026-08-13T08:00:00Z"; c["observed_values"]={"stability":base["ecological_forecast"][0]["predicted_values"]["stability"],"resilience":base["ecological_forecast"][0]["predicted_values"]["resilience"]}; c["previous_prediction"]=base
r=e.step(c,False); v=r["ecological_forecast"][0]["a_posteriori_validation"]
assert v["calibration_score"]==1.0
assert v["false_positive_count"]==0 and v["false_negative_count"]==0
assert r["drift_score"]==0.0
c["ecological_stability"]["stability_score"]=0.0
assert e.step(c,False)["drift_score"]>0.0
print("AW12_CALIBRATION_DRIFT_OK")
