from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker

result = CivilizationTheoremChecker().step(inputs=build_context(), persist=False)
assert result["civilization_theorem_status"] == "RF_CIVILIZATION_PROPERTIES_TESTED"
assert result["properties_tested"] is True
assert result["property_count"] == 11
assert len(result["property_tests"]) == 11
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True
print("AW13_FAST_ACCEPTANCE_OK")
