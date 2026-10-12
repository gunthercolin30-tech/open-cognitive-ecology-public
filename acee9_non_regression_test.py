from ontology.acee_causal_effect_analyzer import AceeCausalEffectAnalyzer
def main():
 r=AceeCausalEffectAnalyzer().step(inputs={"impact_evaluation":{"comparison_valid":True,"impact_score":-0.2,"ready_for_causal_analysis":True},"intervention":{"executed":True},"replications":[-0.2,-0.18,-0.22],"counterfactual_effect":0.0,"alternative_explanations":[]},persist=False)
 assert r["causal_effect_resolved"] is True and r["effect_direction"]=="harmful" and r["rollback_executed"] is False
 print("ACEE9_NON_REGRESSION_OK")
if __name__=="__main__": main()
