from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker

checker = CivilizationTheoremChecker()
target = "coordination"
base = checker.step(build_context(), False)
base_item = next(x for x in base["property_tests"] if x["property"] == target)

for payload in (
    [{}],
    [None, "invalid", 42],
    [{"id": "DUP"}, {"id": "DUP"}],
    [{"id": f"CE-{i}"} for i in range(100)],
):
    context = build_context()
    context["counterexamples"] = {target: payload}
    result = checker.step(context, False)
    item = next(x for x in result["property_tests"] if x["property"] == target)
    assert item["observations"]["counterexample_count"] == len(payload)
    assert item["confidence"] == round(base_item["confidence"] * 0.5, 6)
    assert result["property_statuses"][target] == "VALIDATED"

print("AW13_COUNTEREXAMPLE_ROBUSTNESS_OK")
