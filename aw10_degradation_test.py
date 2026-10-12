from copy import deepcopy
from aw10_context import build_context
from ontology.ecology_dashboard import EcologyDashboard

D = EcologyDashboard()
assert D.step(inputs={}, persist=False)["rf_ecology_dashboard_ready"] is False
context = build_context()
context.pop("collective_rf_analysis")
assert D.step(inputs=context, persist=False)["rf_ecology_dashboard_ready"] is False
context = build_context()
context["civilizational_memory"] = {}
assert D.step(inputs=context, persist=False)["rf_ecology_dashboard_ready"] is False
print("AW10_DEGRADATION_OK")
