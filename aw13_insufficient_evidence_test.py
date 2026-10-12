from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker
context = build_context(); context["property_evidence"] = {"distributed_memory": [{"evidence_id":"ONLY-1","quality":0.95}]}
result = CivilizationTheoremChecker().step(context, persist=False)
assert result["property_statuses"]["distributed_memory"] == "INSUFFICIENT_EVIDENCE"
print("AW13_INSUFFICIENT_EVIDENCE_OK")
