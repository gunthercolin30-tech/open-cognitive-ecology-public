from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine

result = EcologicalPredictionEngine().step(inputs=build_context(), persist=False)
assert result["prediction_status"] == "RF_ECOLOGY_PREDICTION_READY"
assert result["prediction_ready"] is True
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True
assert result["temporal_leakage_detected"] is False
print("ECOLOGICAL_PREDICTION_ENGINE_FINAL_LOCK_OK")
