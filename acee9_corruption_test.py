import tempfile
from pathlib import Path
from ontology.acee_causal_effect_analyzer import AceeCausalEffectAnalyzer
def main():
 with tempfile.TemporaryDirectory() as d:
  p=Path(d)/"acee_runtime"/"ACEE9_acee_causal_effect_analyzer"; p.mkdir(parents=True); (p/"causal_effect_history.jsonl").write_text("{bad\n")
  r=AceeCausalEffectAnalyzer(root=Path(d)).step(inputs={"impact_evaluation":{"comparison_valid":True,"impact_score":0.1,"ready_for_causal_analysis":True},"intervention":{"executed":True},"replications":[0.1],"counterfactual_effect":0.0},persist=False)
  assert r["history_corrupted"] is True and r["causal_effect_resolved"] is False
 print("ACEE9_CORRUPTION_OK")
if __name__=="__main__": main()
