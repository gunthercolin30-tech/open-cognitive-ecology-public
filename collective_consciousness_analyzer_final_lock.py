from aw9_context import build_context
from ontology.collective_consciousness_analyzer import CollectiveConsciousnessAnalyzer

READY_OR_SYNTHETIC_CONTEXT = build_context()
result = CollectiveConsciousnessAnalyzer().step(inputs=READY_OR_SYNTHETIC_CONTEXT, persist=False)
assert result["status"] == "COLLECTIVE_RF_ANALYSIS_READY"
assert result["collective_rf_analysis_ready"] is True
assert result["functional_collective_integration"] >= result["thresholds"]["minimum_functional_collective_integration"]
assert result["centralization_risk_score"] <= result["thresholds"]["maximum_centralization_risk"]
assert result["collective_consciousness_proven"] is False
assert result["collective_subjectivity_proven"] is False
assert result["collective_qualia_proven"] is False
assert result["collective_phenomenology_proven"] is False
assert result["functional_conclusion_only"] is True
assert result["phenomenology_undetermined"] is True
print("COLLECTIVE_CONSCIOUSNESS_ANALYZER_FINAL_LOCK_OK")
