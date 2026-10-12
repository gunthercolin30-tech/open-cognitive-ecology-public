from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker

checker = CivilizationTheoremChecker()
target = "distributed_memory"

one = build_context()
one["property_evidence"] = {target: [{"evidence_id": "E1", "quality": 0.9}]}
r1 = checker.step(one, False)
assert r1["property_statuses"][target] == "INSUFFICIENT_EVIDENCE"

many = build_context()
many["property_evidence"] = {target: [
    {"evidence_id": f"E{i}", "quality": 0.9} for i in range(1000)
]}
r2 = checker.step(many, False)
item2 = next(x for x in r2["property_tests"] if x["property"] == target)
assert item2["observations"]["evidence_count"] == 1000
assert r2["property_statuses"][target] == "VALIDATED"

duplicates = build_context()
duplicates["property_evidence"] = {target: [
    {"evidence_id": "DUP", "quality": 0.9},
    {"evidence_id": "DUP", "quality": 0.9},
]}
r3 = checker.step(duplicates, False)
item3 = next(x for x in r3["property_tests"] if x["property"] == target)
assert item3["observations"]["evidence_count"] == 2
assert all(0.0 <= ev["quality"] <= 1.0 for ev in item3["evidence"])

malformed = build_context()
malformed["property_evidence"] = {target: [None, "raw", {"quality": float("nan")}]}
r4 = checker.step(malformed, False)
item4 = next(x for x in r4["property_tests"] if x["property"] == target)
assert item4["observations"]["evidence_count"] == 3
assert all(0.0 <= ev["quality"] <= 1.0 for ev in item4["evidence"])
print("AW13_EVIDENCE_ROBUSTNESS_OK")
