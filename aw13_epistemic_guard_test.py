from aw13_context import build_context
from ontology.civilization_theorem_checker import CivilizationTheoremChecker
result = CivilizationTheoremChecker().step(build_context(), persist=False)
for key in ("collective_consciousness_proven","collective_subjectivity_proven","collective_qualia_proven","collective_phenomenology_proven","consciousness_proven","subjectivity_proven","qualia_proven","phenomenology_proven"): assert result[key] is False
assert result["functional_conclusion_only"] is True and result["phenomenology_undetermined"] is True
print("AW13_EPISTEMIC_GUARD_OK")
