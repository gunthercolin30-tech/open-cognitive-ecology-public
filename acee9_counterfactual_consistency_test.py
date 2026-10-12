from ontology.acee_causal_effect_analyzer import AceeCausalEffectAnalyzer
def run(c): return AceeCausalEffectAnalyzer().step(inputs={"impact_evaluation":{"comparison_valid":True,"impact_score":0.2,"ready_for_causal_analysis":True},"intervention":{"executed":True},"replications":[0.2,0.21,0.19],"counterfactual_effect":c,"alternative_explanations":[]},persist=False)
def main():
 assert run(0.0)["counterfactual_consistency"]>run(0.19)["counterfactual_consistency"]
 print("ACEE9_COUNTERFACTUAL_CONSISTENCY_OK")
if __name__=="__main__": main()
