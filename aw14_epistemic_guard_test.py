from aw14_context import build_context
from ontology.ecological_certifier import EcologicalCertifier

result = EcologicalCertifier().step(inputs=build_context(), persist=False)
for key in (
    "collective_consciousness_proven",
    "collective_subjectivity_proven",
    "collective_qualia_proven",
    "collective_phenomenology_proven",
    "consciousness_proven",
    "subjectivity_proven",
    "qualia_proven",
    "phenomenology_proven",
):
    assert result[key] is False
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True
print("AW14_EPISTEMIC_GUARD_OK")
