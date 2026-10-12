from ontology.acee_causal_effect_analyzer import AceeCausalEffectAnalyzer
def main():
 for bad in [float("nan"),float("inf"),"x"]:
  r=AceeCausalEffectAnalyzer().step(inputs={"impact_evaluation":{"comparison_valid":True,"impact_score":bad,"ready_for_causal_analysis":True},"intervention":{"executed":True},"replications":[0.1],"counterfactual_effect":0.0},persist=False)
  assert r["causal_effect_resolved"] is False
 print("ACEE9_NUMERIC_ROBUSTNESS_OK")
if __name__=="__main__": main()
