from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker

result = CivilizationTheoremChecker().step(inputs=build_context(), persist=False)
assert result["civilization_theorem_status"] == "RF_CIVILIZATION_PROPERTIES_TESTED"
assert result["properties_tested"] is True
assert result["property_count"] == 11
assert all(item["test_hash"] for item in result["property_tests"])
assert result["collective_consciousness_proven"] is False
assert result["collective_subjectivity_proven"] is False
assert result["collective_qualia_proven"] is False
assert result["collective_phenomenology_proven"] is False
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True
print("CIVILIZATION_THEOREM_CHECKER_FINAL_LOCK_OK")
