from ontology.acee_causal_effect_analyzer import AceeCausalEffectAnalyzer
def main():
 r=AceeCausalEffectAnalyzer().step(inputs={"analysis_id":"fast","impact_evaluation":{"comparison_valid":True,"impact_score":0.12,"normalized_deltas":{"runtime_score":0.12},"ready_for_causal_analysis":True},"intervention":{"executed":True},"replications":[0.11,0.12,0.13,0.12],"counterfactual_effect":0.0,"alternative_explanations":[]},persist=False)
 assert r["causal_status"]=="ACEE_CAUSAL_EFFECT_RESOLVED" and r["ready_for_selection"] is True
 assert r["selection_decision_made"] is False and r["rollback_executed"] is False and r["acee11_called"] is False
 print("ACEE9_FAST_ACCEPTANCE_OK")
if __name__=="__main__": main()
