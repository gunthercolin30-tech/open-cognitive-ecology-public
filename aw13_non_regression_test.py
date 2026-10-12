from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker
result = CivilizationTheoremChecker().step(build_context(), persist=False)
required = {"civilization_theorem_status","properties_tested","property_count","property_tests","property_statuses","status_counts","mean_confidence","limitations","civilization_test_hash","functional_conclusion_only","phenomenology_undetermined"}
assert required <= set(result)
assert tuple(item["property"] for item in result["property_tests"]) == CivilizationTheoremChecker.PROPERTY_ORDER
print("AW13_NON_REGRESSION_OK")
