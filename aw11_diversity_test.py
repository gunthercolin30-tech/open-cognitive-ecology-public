from copy import deepcopy
from aw11_context import build_context
from ontology.ecological_stability_analyzer import EcologicalStabilityAnalyzer

engine = EcologicalStabilityAnalyzer()
base = build_context()
nominal = engine.step(inputs=base, persist=False)
homogeneous = deepcopy(base)
records = homogeneous["multi_rf_registry"]["registry"]
for record in records:
    record["lineage_id"] = "ONE-LINEAGE"
    record["rf_type"] = "ONE-TYPE"
    record["capabilities"] = []
    record["roles"] = []
low = engine.step(inputs=homogeneous, persist=False)
assert low["effective_diversity_score"] <= nominal["effective_diversity_score"]
assert low["diversity_score"] <= nominal["diversity_score"]
print("AW11_DIVERSITY_OK")
