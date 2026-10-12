from ontology.acee_causal_effect_analyzer import AceeCausalEffectAnalyzer
def main():
 r=AceeCausalEffectAnalyzer().step(inputs={"impact_evaluation":{"comparison_valid":True,"impact_score":0.2,"ready_for_causal_analysis":True},"intervention":{"executed":True},"replications":[0.2,0.21],"counterfactual_effect":0.19,"alternative_explanations":["external_load"]},persist=False)
 assert r["confounding_detected"] is True and r["causal_effect_resolved"] is False and r["ready_for_selection"] is False
 print("ACEE9_CONFOUNDED_EFFECT_OK")
if __name__=="__main__": main()
