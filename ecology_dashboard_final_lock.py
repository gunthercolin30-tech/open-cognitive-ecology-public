from aw10_context import build_context
from ontology.ecology_dashboard import EcologyDashboard

result = EcologyDashboard().step(inputs=build_context(), persist=False)
assert result["dashboard_status"] == "RF_ECOLOGY_DASHBOARD_READY"
assert result["rf_ecology_dashboard_ready"] is True
assert result["exports"]["json"]
assert result["exports"]["markdown"]
assert "<!doctype html>" in result["exports"]["html"].lower()
assert result["collective_consciousness_proven"] is False
assert result["functional_conclusion_only"] is True
print("ECOLOGY_DASHBOARD_FINAL_LOCK_OK")
