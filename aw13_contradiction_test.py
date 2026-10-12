from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker
context = build_context(); context["contradictions"] = {"resilience": [{"id":"C-1"}]}
result = CivilizationTheoremChecker().step(context, persist=False)
assert result["property_statuses"]["resilience"] == "NOT_VALIDATED"
print("AW13_CONTRADICTION_OK")
