from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine
r=EcologicalPredictionEngine().step(build_context(),False)
for k in ("collective_consciousness_proven","collective_subjectivity_proven","collective_qualia_proven","collective_phenomenology_proven","consciousness_proven","subjectivity_proven","qualia_proven","phenomenology_proven"): assert r[k] is False
assert r["functional_conclusion_only"] is True and r["phenomenology_undetermined"] is True
print("AW12_EPISTEMIC_GUARD_OK")
