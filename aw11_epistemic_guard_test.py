from aw11_context import build_context
from ontology.ecological_stability_analyzer import EcologicalStabilityAnalyzer

for ctx in (build_context(), {}):
    result = EcologicalStabilityAnalyzer().step(inputs=ctx, persist=False)
    assert result["collective_consciousness_proven"] is False
    assert result["collective_subjectivity_proven"] is False
    assert result["collective_qualia_proven"] is False
    assert result["collective_phenomenology_proven"] is False
    assert result["functional_conclusion_only"] is True
    assert result["phenomenology_undetermined"] is True
print("AW11_EPISTEMIC_GUARD_OK")
