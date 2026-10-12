from ontology.acee_impact_evaluator import AceeImpactEvaluator
METRICS={"error_count":0,"modules_discovered":100,"active_primitives":90,"stability_score":0.9,"governance_score":0.91,"evolution_score":0.8,"closure_pressure":0.1,"runtime_score":0.92}
def main():
    before=dict(METRICS); after=dict(METRICS); after["stability_score"]=0.85
    r=AceeImpactEvaluator().step(inputs={"evaluation_id":"acee8-causal-boundary","before":before,"after":after},persist=False)
    assert r["comparison_valid"] is True
    assert r["observed_regression_signal"] is True
    assert "stability_regression" in r["observed_regression_reasons"]
    assert r["rollback_fields_deprecated"] is True
    assert r["causal_analysis_required"] is True
    assert r["ready_for_causal_analysis"] is True
    assert r["ready_for_selection"] is False
    assert r["causal_effect_resolved"] is False
    assert r["selection_decision_made"] is False
    assert r["rollback_executed"] is False
    print("ACEE8_CAUSAL_BOUNDARY_OK")
if __name__=="__main__": main()
