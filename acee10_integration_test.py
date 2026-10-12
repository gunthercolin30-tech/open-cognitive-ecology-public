from ontology.acee_impact_evaluator import AceeImpactEvaluator
from ontology.acee_causal_effect_analyzer import AceeCausalEffectAnalyzer
from ontology.acee_selection_policy import AceeSelectionPolicy
def main():
 b={"error_count":0,"modules_discovered":100,"active_primitives":90,"stability_score":0.9,"governance_score":0.9,"evolution_score":0.8,"closure_pressure":0.1,"runtime_score":0.9}; a=dict(b); a["runtime_score"]=0.95
 i=AceeImpactEvaluator().step(inputs={"before":b,"after":a},persist=False)
 c=AceeCausalEffectAnalyzer().step(inputs={"impact_evaluation":i,"intervention":{"executed":True},"replications":[i["impact_score"]]*3,"counterfactual_effect":-0.1,"alternative_explanations":[]},persist=False)
 x={"selection_id":"test","impact_evaluation":{"comparison_valid":True,"impact_score":0.12,"metric_classifications":{"closure_pressure":"unchanged"}},"causal_analysis":{"ready_for_selection":True,"causal_effect_resolved":True,"causal_probability":0.9,"causal_confidence":0.9,"effect_size":0.12,"effect_direction":"beneficial"},"stability_evidence":{"stability_score":0.9},"simplicity_evidence":{"simplicity_score":0.8},"reversibility_evidence":{"mean_reversibility_score":0.9,"reversibility_assured":True},"non_closure_evidence":{"closure_pressure":0.1,"non_closure_score":0.9},"constitutional_evidence":{"compliant":True,"constitutional_compliance_score":0.9},"governance_evidence":{"approved":True,"governance_score":0.9}}; x["impact_evaluation"]=i; x["causal_analysis"]=c
 s=AceeSelectionPolicy().step(inputs=x,persist=False)
 assert i["ready_for_selection"] is False and c["ready_for_selection"] is True and s["decision"]=="accept"
 assert s["acee11_called"] is False and s["rollback_executed"] is False
 print("ACEE10_ACEE8_ACEE9_ACEE11_INTEGRATION_OK")
if __name__=="__main__": main()
