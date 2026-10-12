from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine
r=EcologicalPredictionEngine().step(build_context(),False)
required={"prediction_status","forecast_horizon","prediction_confidence","prediction_uncertainty","ecological_forecast","predicted_coalitions","predicted_conflicts","predicted_merges","predicted_fragmentations","predicted_resilience","predicted_diversity","predicted_memory_continuity","predicted_future_openness","alternative_scenarios","risk_forecast","protective_forecast","prediction_timestamp_utc","prediction_hash"}
assert required <= set(r)
assert r["collective_subjectivity_proven"] is False
print("AW12_NON_REGRESSION_OK")
