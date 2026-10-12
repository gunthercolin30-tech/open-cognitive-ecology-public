from ontology.acee_causal_effect_analyzer import AceeCausalEffectAnalyzer
def main():
 r=AceeCausalEffectAnalyzer().step(inputs={"impact_evaluation":{"comparison_valid":False}},persist=False)
 assert r["causal_status"]=="ACEE_CAUSAL_EFFECT_DEGRADED" and r["causal_effect_resolved"] is False and r["blocking_reasons"]
 print("ACEE9_DEGRADATION_OK")
if __name__=="__main__": main()
