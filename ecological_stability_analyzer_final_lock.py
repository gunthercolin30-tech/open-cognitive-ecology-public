from aw11_context import build_context
from ontology.ecological_stability_analyzer import EcologicalStabilityAnalyzer

result = EcologicalStabilityAnalyzer().step(inputs=build_context(), persist=False)
assert result["status"] == "ECOLOGICAL_STABILITY_ANALYSIS_READY"
assert result["ecological_stability_analysis_ready"] is True
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True
print("ECOLOGICAL_STABILITY_ANALYZER_FINAL_LOCK_OK")
