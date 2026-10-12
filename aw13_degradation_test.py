from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker
context = build_context()
for key in context["property_scores"]: context["property_scores"][key] = 0.10
result = CivilizationTheoremChecker().step(context, persist=False)
assert all(status == "NOT_VALIDATED" for status in result["property_statuses"].values())
assert result["mean_confidence"] <= 0.10
print("AW13_DEGRADATION_OK")
