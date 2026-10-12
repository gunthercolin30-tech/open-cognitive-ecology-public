from aw10_context import build_context
from ontology.ecology_dashboard import EcologyDashboard

result = EcologyDashboard().step(inputs=build_context(), persist=False)
assert result["collective_consciousness_proven"] is False
assert result["collective_subjectivity_proven"] is False
assert result["collective_qualia_proven"] is False
assert result["collective_phenomenology_proven"] is False
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True
assert "No collective consciousness" in result["exports"]["html"]
print("AW10_EPISTEMIC_GUARD_OK")
