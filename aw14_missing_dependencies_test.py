from aw14_context import build_context
from ontology.ecological_certifier import EcologicalCertifier

for module in EcologicalCertifier.REQUIRED_MODULES:
    context = build_context()
    context["module_statuses"][module] = "MISSING"
    result = EcologicalCertifier().step(inputs=context, persist=False)
    assert result["ecology_complete"] is False
    assert module in result["missing_modules"]
print("AW14_MISSING_DEPENDENCIES_OK")
