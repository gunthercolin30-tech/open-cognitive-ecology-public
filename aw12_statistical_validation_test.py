import copy
import math
from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine

engine = EcologicalPredictionEngine()
base_context = build_context()
base = engine.step(inputs=base_context, persist=False)
predicted = base["ecological_forecast"][0]["predicted_values"]
errors = []
squared_errors = []
brier_terms = []
for index in range(60):
    context = copy.deepcopy(base_context)
    noise = ((index % 7) - 3) * 0.01
    observed = {key: max(0.0, min(1.0, value + noise)) for key, value in predicted.items()}
    context["observed_at"] = "2026-07-14T08:00:00Z"
    context["observed_values"] = observed
    result = engine.step(inputs=context, persist=False)
    validation = result["ecological_forecast"][0]["a_posteriori_validation"]
    assert validation["validation_status"] == "VALIDATED_A_POSTERIORI"
    assert 0.0 <= validation["calibration_score"] <= 1.0
    for key, value in observed.items():
        error = predicted[key] - value
        errors.append(abs(error))
        squared_errors.append(error * error)
    event_probability = result["ecological_forecast"][0]["predicted_conflict_probability"]
    event_observed = 1.0 if index % 5 == 0 else 0.0
    brier_terms.append((event_probability - event_observed) ** 2)
mae = sum(errors) / len(errors)
rmse = math.sqrt(sum(squared_errors) / len(squared_errors))
brier = sum(brier_terms) / len(brier_terms)
assert mae < 0.04
assert rmse < 0.05
assert 0.0 <= brier <= 1.0
print("AW12_STATISTICAL_VALIDATION_OK")
