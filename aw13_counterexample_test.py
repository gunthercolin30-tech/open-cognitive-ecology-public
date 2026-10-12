from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker
context = build_context(); context["counterexamples"] = {"coordination": [{"id":"CE-1"}]}
result = CivilizationTheoremChecker().step(context, persist=False)
item = next(x for x in result["property_tests"] if x["property"] == "coordination")
assert item["counterexamples"] and item["confidence"] < context["property_scores"]["coordination"]
print("AW13_COUNTEREXAMPLE_OK")
