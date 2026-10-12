from copy import deepcopy
from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker
checker = CivilizationTheoremChecker(); context = build_context(); first = checker.step(context, persist=False)
second_context = deepcopy(context); second_context["property_scores"]["prediction_capacity"] = 0.20
second = checker.step(second_context, persist=False)
assert first["civilization_test_hash"] != second["civilization_test_hash"]
assert first["property_statuses"]["prediction_capacity"] != second["property_statuses"]["prediction_capacity"]
print("AW13_NON_REPRODUCIBILITY_OK")
