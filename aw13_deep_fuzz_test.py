import math
import random
from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker

checker = CivilizationTheoremChecker()
rng = random.Random(130013)
weird = [None, True, False, "", "bad", b"bytes", [], (), set(), {}, float("nan"), float("inf"), float("-inf"), -10**9, 10**9]

for index in range(500):
    if index < len(weird):
        source = weird[index]
    else:
        context = build_context()
        name = rng.choice(checker.PROPERTY_ORDER)
        context["property_scores"][name] = rng.choice(weird)
        context[rng.choice(["property_evidence", "counterexamples", "contradictions", "property_applicability"])] = rng.choice(weird)
        source = context
    try:
        result = checker.step(source, persist=False)
    except (TypeError, ValueError):
        continue
    assert result["property_count"] == 11
    assert math.isfinite(result["mean_confidence"])
    assert len(result["civilization_test_hash"]) == 64
    assert all(math.isfinite(item["confidence"]) for item in result["property_tests"])

print("AW13_DEEP_FUZZ_OK")
