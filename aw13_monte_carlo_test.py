import math
import random
from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker

checker = CivilizationTheoremChecker()

def run(seed):
    rng = random.Random(seed)
    outputs = []
    for _ in range(300):
        context = build_context()
        context["property_scores"] = {
            name: rng.random() for name in checker.PROPERTY_ORDER
        }
        result = checker.step(context, persist=False)
        assert result["property_count"] == 11
        assert math.isfinite(result["mean_confidence"])
        assert 0.0 <= result["mean_confidence"] <= 1.0
        assert all(status in {
            "VALIDATED", "PARTIALLY_VALIDATED", "NOT_VALIDATED",
            "INSUFFICIENT_EVIDENCE", "NOT_APPLICABLE",
        } for status in result["property_statuses"].values())
        outputs.append(result["civilization_test_hash"])
    return outputs

first = run(1337)
second = run(1337)
third = run(7331)
assert first == second
assert first != third
assert len(set(first)) > 250
print("AW13_MONTE_CARLO_OK")
