from aw14_context import build_context
from ontology.ecological_certifier import EcologicalCertifier

result = EcologicalCertifier().step(inputs=build_context(), persist=False)
assert result["certification_status"] == "RF_ECOLOGY_COMPLETE"
assert result["ecology_complete"] is True
assert len(result["certified_modules"]) == 14
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True
print("AW14_FAST_ACCEPTANCE_OK")
