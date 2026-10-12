from ontology.acee_selection_policy import AceeSelectionPolicy
def main():
 r=AceeSelectionPolicy().step(inputs={"selection_id":"test","impact_evaluation":{"comparison_valid":True,"impact_score":-0.2,"metric_classifications":{"closure_pressure":"unchanged"}},"causal_analysis":{"ready_for_selection":True,"causal_effect_resolved":True,"causal_probability":0.9,"causal_confidence":0.9,"effect_size":-0.2,"effect_direction":"harmful"},"stability_evidence":{"stability_score":0.9},"simplicity_evidence":{"simplicity_score":0.8},"reversibility_evidence":{"mean_reversibility_score":0.9,"reversibility_assured":True},"non_closure_evidence":{"closure_pressure":0.1,"non_closure_score":0.9},"constitutional_evidence":{"compliant":True,"constitutional_compliance_score":0.9},"governance_evidence":{"approved":True,"governance_score":0.9}},persist=False)
 assert r["decision"]=="rollback" and r["rollback_requested"] is True and r["rollback_executed"] is False and r["acee11_called"] is False
 print("ACEE10_NON_REGRESSION_OK")
if __name__=="__main__": main()
