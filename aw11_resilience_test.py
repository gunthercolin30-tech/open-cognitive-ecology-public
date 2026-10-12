from copy import deepcopy
from aw11_context import build_context
from ontology.ecological_stability_analyzer import EcologicalStabilityAnalyzer

engine = EcologicalStabilityAnalyzer()
base = build_context()
nominal = engine.step(inputs=base, persist=False)
degraded = deepcopy(base)
degraded["civilizational_memory"]["loss_tolerance_score"] = 0.0
degraded["civilizational_memory"]["availability_score"] = 0.1
degraded["civilizational_memory"]["recovery_status"] = "RECOVERY_UNAVAILABLE"
low = engine.step(inputs=degraded, persist=False)
assert low["resilience_score"] <= nominal["resilience_score"]
assert low["robustness_score"] <= nominal["robustness_score"]
print("AW11_RESILIENCE_OK")
