from copy import deepcopy
from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker

checker = CivilizationTheoremChecker()
properties = checker.PROPERTY_ORDER

for target in properties:
    base = build_context()
    baseline = checker.step(base, persist=False)

    cases = []

    validated = deepcopy(base)
    validated["property_scores"][target] = 0.90
    cases.append((validated, "VALIDATED"))

    partial = deepcopy(base)
    partial["property_scores"][target] = 0.65
    cases.append((partial, "PARTIALLY_VALIDATED"))

    rejected = deepcopy(base)
    rejected["property_scores"][target] = 0.20
    cases.append((rejected, "NOT_VALIDATED"))

    insufficient = deepcopy(base)
    insufficient["property_evidence"] = {
        target: [{"evidence_id": "ONLY-ONE", "quality": 0.95}]
    }
    cases.append((insufficient, "INSUFFICIENT_EVIDENCE"))

    not_applicable = deepcopy(base)
    not_applicable["property_applicability"] = {target: False}
    cases.append((not_applicable, "NOT_APPLICABLE"))

    for context, expected in cases:
        result = checker.step(context, persist=False)
        assert result["property_statuses"][target] == expected, (target, expected)
        for other in properties:
            if other != target:
                assert result["property_statuses"][other] == baseline["property_statuses"][other]

print("AW13_PROPERTY_MATRIX_OK")
