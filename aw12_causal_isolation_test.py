import copy
from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine

engine = EcologicalPredictionEngine()
baseline_context = build_context()
baseline = engine.step(inputs=baseline_context, persist=False)
changed_context = copy.deepcopy(baseline_context)
original = changed_context["ecological_stability"]["resilience_score"]
changed_context["ecological_stability"]["resilience_score"] = max(0.0, original - 0.35)
changed = engine.step(inputs=changed_context, persist=False)
assert baseline["predicted_resilience"] != changed["predicted_resilience"]
for metric in ("stability", "diversity", "memory_continuity", "future_openness", "centralization_risk"):
    before = [row["predicted_values"][metric] for row in baseline["ecological_forecast"]]
    after = [row["predicted_values"][metric] for row in changed["ecological_forecast"]]
    assert before == after, metric
assert baseline["predicted_conflicts"] == changed["predicted_conflicts"]
assert baseline["predicted_fragmentations"] == changed["predicted_fragmentations"]
print("AW12_CAUSAL_ISOLATION_OK")
