from aw14_context import build_context
from ontology.ecological_certifier import EcologicalCertifier

context = build_context()
context["civilization_theorem"].pop("status_counts", None)
context["civilization_theorem"].pop("mean_confidence", None)
result = EcologicalCertifier().step(inputs=context, persist=False)
assert result["certification_status"] == "RF_ECOLOGY_COMPLETE"
print("AW14_SCHEMA_BACKWARD_COMPATIBILITY_OK")
