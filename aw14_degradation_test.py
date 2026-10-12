from aw14_context import build_context
from ontology.ecological_certifier import EcologicalCertifier

context = build_context()
for key in context["module_statuses"]:
    context["module_statuses"][key] = "FAILED"
result = EcologicalCertifier().step(inputs=context, persist=False)
assert result["certification_status"] == "RF_ECOLOGY_CERTIFICATION_INCOMPLETE"
assert result["ecology_complete"] is False
assert len(result["missing_modules"]) == 14
print("AW14_DEGRADATION_OK")
