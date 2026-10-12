import random
from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker

checker = CivilizationTheoremChecker()
base = build_context()
reference = checker.step(base, persist=False)
items = list(base["property_scores"].items())

for seed in range(50):
    shuffled = list(items)
    random.Random(seed).shuffle(shuffled)
    context = build_context()
    context["property_scores"] = dict(shuffled)
    result = checker.step(context, persist=False)
    assert result["civilization_test_hash"] == reference["civilization_test_hash"]
    assert result["status_counts"] == reference["status_counts"]
    assert result["mean_confidence"] == reference["mean_confidence"]
    assert tuple(item["property"] for item in result["property_tests"]) == checker.PROPERTY_ORDER

print("AW13_PROPERTY_ORDER_PERMUTATION_OK")
