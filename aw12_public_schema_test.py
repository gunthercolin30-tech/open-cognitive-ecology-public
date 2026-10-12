from aw12_context import build_context
from ontology.ecological_prediction_engine import EcologicalPredictionEngine

result = EcologicalPredictionEngine().step(inputs=build_context(), persist=False)
top_level = {
    "primitive", "step", "public_schema_version", "prediction_status", "prediction_ready",
    "prediction_id", "issued_at", "prediction_timestamp_utc", "forecast_horizon",
    "current_state", "ecological_forecast", "predicted_coalitions", "predicted_conflicts",
    "predicted_merges", "predicted_fragmentations", "predicted_resilience",
    "predicted_diversity", "predicted_memory_continuity", "predicted_future_openness",
    "prediction_confidence", "prediction_uncertainty", "alternative_scenarios",
    "risk_forecast", "protective_forecast", "drift_score", "temporal_leakage_detected",
    "prediction_hash", "epistemic_scope", "collective_consciousness_proven",
    "collective_subjectivity_proven", "collective_qualia_proven",
    "collective_phenomenology_proven", "consciousness_proven", "subjectivity_proven",
    "qualia_proven", "phenomenology_proven", "functional_conclusion_only",
    "phenomenology_undetermined", "persisted", "output_path", "history_path",
}
assert top_level <= set(result)
assert len(result["prediction_hash"]) == 64
assert result["prediction_id"].startswith("AW12-")
assert len(result["ecological_forecast"]) == len(result["forecast_horizon"])
row_schema = {
    "forecast_horizon", "target_time", "predicted_values",
    "predicted_conflict_probability", "predicted_fragmentation_probability",
    "predicted_merge_probability", "predicted_coalition_probability",
    "prediction_confidence", "prediction_uncertainty", "falsification_conditions",
    "a_posteriori_validation",
}
validation_schema = {
    "observed_values", "absolute_error", "relative_error", "directional_accuracy",
    "false_positive_count", "false_negative_count", "calibration_score", "validation_status",
}
for row in result["ecological_forecast"]:
    assert row_schema <= set(row)
    assert validation_schema <= set(row["a_posteriori_validation"])
    assert set(row["predicted_values"]) == {
        "stability", "resilience", "diversity", "memory_continuity",
        "future_openness", "centralization_risk",
    }
print("AW12_PUBLIC_SCHEMA_OK")
