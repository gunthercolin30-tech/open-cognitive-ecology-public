from copy import deepcopy
from math import inf, nan
from aw11_context import build_context
from ontology.ecological_stability_analyzer import EcologicalStabilityAnalyzer

for bad in (nan, inf, -inf, "bad"):
    ctx = build_context()
    ctx["civilizational_memory"]["loss_tolerance_score"] = bad
    result = EcologicalStabilityAnalyzer().step(inputs=ctx, persist=False)
    for key in ("stability_score", "resilience_score", "diversity_score", "fragility_score", "robustness_score"):
        assert 0.0 <= result[key] <= 1.0
print("AW11_NUMERIC_ROBUSTNESS_OK")
