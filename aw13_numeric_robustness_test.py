import math
from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker
context = build_context(); context["property_scores"].update({"coordination":float("nan"),"resilience":float("inf"),"diversity":float("-inf")})
result = CivilizationTheoremChecker().step(context, persist=False)
assert result["property_statuses"]["coordination"] == "NOT_VALIDATED"
assert result["property_statuses"]["resilience"] == "NOT_VALIDATED"
assert result["property_statuses"]["diversity"] == "NOT_VALIDATED" and math.isfinite(result["mean_confidence"])
print("AW13_NUMERIC_ROBUSTNESS_OK")
