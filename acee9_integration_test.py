from ontology.acee_impact_evaluator import AceeImpactEvaluator
from ontology.acee_causal_effect_analyzer import AceeCausalEffectAnalyzer
def main():
 b={"error_count":0,"modules_discovered":100,"active_primitives":90,"stability_score":0.9,"governance_score":0.9,"evolution_score":0.8,"closure_pressure":0.1,"runtime_score":0.9}; a=dict(b); a["runtime_score"]=0.95
 i=AceeImpactEvaluator().step(inputs={"before":b,"after":a},persist=False)
 c=AceeCausalEffectAnalyzer().step(inputs={"impact_evaluation":i,"intervention":{"executed":True},"replications":[i["impact_score"],i["impact_score"],i["impact_score"]],"counterfactual_effect":-0.1,"alternative_explanations":[]},persist=False)
 assert i["ready_for_selection"] is False and c["ready_for_selection"] is True and c["acee11_called"] is False
 print("ACEE9_ACEE8_ACEE10_ACEE11_INTEGRATION_OK")
if __name__=="__main__": main()
