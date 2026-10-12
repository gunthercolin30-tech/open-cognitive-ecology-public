from aw14_context import build_context
from ontology.ecological_certifier import EcologicalCertifier

result = EcologicalCertifier().step(inputs=build_context(), persist=False)
assert result["certification_status"] == "RF_ECOLOGY_COMPLETE"
assert result["ecology_complete"] is True
assert result["missing_modules"] == []
assert len(result["evidence_manifest"]) == 14
assert len(result["test_manifest"]) == 14
assert len(result["certification_hash"]) == 64
assert result["collective_consciousness_proven"] is False
assert result["collective_subjectivity_proven"] is False
assert result["collective_qualia_proven"] is False
assert result["collective_phenomenology_proven"] is False
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True
print("ECOLOGICAL_CERTIFIER_FINAL_LOCK_OK")
