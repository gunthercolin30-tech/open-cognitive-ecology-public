from copy import deepcopy
from aw10_context import build_context
from ontology.ecology_dashboard import EcologyDashboard

D = EcologyDashboard()
context = build_context()
original = deepcopy(context)
first = D.step(inputs=context, persist=False)
second = D.step(inputs=deepcopy(context), persist=False)
assert context == original
assert first["dashboard_hash"] == second["dashboard_hash"]
assert first["export_integrity"] == second["export_integrity"]
assert first["exports"] == second["exports"]
assert first["persisted"] is False
print("AW10_NON_REGRESSION_OK")
