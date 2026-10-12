from copy import deepcopy
from aw11_context import build_context
from ontology.ecological_stability_analyzer import EcologicalStabilityAnalyzer

engine = EcologicalStabilityAnalyzer()
empty = engine.step(inputs={}, persist=False)
assert empty["ecological_stability_analysis_ready"] is False
ctx = build_context()
ctx["civilizational_memory"]["availability_score"] = 0.0
ctx["civilizational_memory"]["loss_tolerance_score"] = 0.0
ctx["civilizational_memory"]["future_openness_preservation_score"] = 0.0
ctx["collective_rf_analysis"]["centralization_risk_score"] = 1.0
ctx["collective_rf_analysis"]["local_autonomy_score"] = 0.0
result = engine.step(inputs=ctx, persist=False)
assert result["ecological_stability_analysis_ready"] is False
assert result["fragility_score"] > empty["fragility_score"] or result["risk_factors"]
print("AW11_DEGRADATION_OK")
