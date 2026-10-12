from copy import deepcopy
from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker
checker = CivilizationTheoremChecker(); context = build_context()
a = checker.step(context, persist=False); b = checker.step(context, persist=False)
assert a["civilization_test_hash"] == b["civilization_test_hash"]
changed = deepcopy(context); changed["property_scores"]["coordination"] = 0.20
c = checker.step(changed, persist=False)
assert c["property_statuses"]["coordination"] == "NOT_VALIDATED"
assert c["civilization_test_hash"] != a["civilization_test_hash"]
print("AW13_FUNCTIONAL_OK")
