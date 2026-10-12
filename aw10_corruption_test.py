from aw10_context import build_context
from ontology.ecology_dashboard import EcologyDashboard

context = build_context()
context["collective_rf_analysis"] = {"collective_rf_analysis_ready": True, "member_rf_ids": {"not": "a list"}}
result = EcologyDashboard().step(inputs=context, persist=False)
assert isinstance(result["exports"]["json"], str)
assert isinstance(result["exports"]["markdown"], str)
assert isinstance(result["exports"]["html"], str)
print("AW10_CORRUPTION_ROBUSTNESS_OK")
