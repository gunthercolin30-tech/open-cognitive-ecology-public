from ontology.acee_causal_effect_analyzer import AceeCausalEffectAnalyzer
def main():
 r=AceeCausalEffectAnalyzer().step(inputs={"impact_evaluation":{"comparison_valid":True,"impact_score":0.1,"ready_for_causal_analysis":True},"intervention":{"executed":True},"replications":[0.1,0.11,0.09],"counterfactual_effect":0.0,"alternative_explanations":[]},persist=False)
 assert r["causal_effect_resolved"] is True and r["functional_conclusion_only"] is True and r["phenomenology_undetermined"] is True
 for k in ["consciousness_proven","subjectivity_proven","qualia_proven","phenomenology_proven","selection_decision_made","rollback_executed","acee11_called"]: assert r[k] is False
 print("ACEE_CAUSAL_EFFECT_ANALYZER_FINAL_LOCK_OK")
if __name__=="__main__": main()
