import random
from collections import Counter
from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker

checker = CivilizationTheoremChecker()
rng = random.Random(20260713)
counts = Counter()
confidences = []

for _ in range(600):
    context = build_context()
    context["property_scores"] = {
        name: rng.random() for name in checker.PROPERTY_ORDER
    }
    result = checker.step(context, persist=False)
    counts.update(result["property_statuses"].values())
    confidences.extend(item["confidence"] for item in result["property_tests"])

sample_count = 600 * len(checker.PROPERTY_ORDER)
assert counts["VALIDATED"] > sample_count * 0.15
assert counts["PARTIALLY_VALIDATED"] > sample_count * 0.18
assert counts["NOT_VALIDATED"] > sample_count * 0.45
mean_confidence = sum(confidences) / len(confidences)
assert 0.45 < mean_confidence < 0.55
assert min(confidences) < 0.01
assert max(confidences) > 0.99
print("AW13_STATISTICAL_VALIDATION_OK")
