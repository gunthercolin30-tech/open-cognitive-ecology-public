import json,tempfile
from pathlib import Path
from ontology.acee_causal_effect_analyzer import AceeCausalEffectAnalyzer
def main():
 with tempfile.TemporaryDirectory() as d:
  r=AceeCausalEffectAnalyzer(root=Path(d)).step(inputs={"analysis_id":"p","impact_evaluation":{"comparison_valid":True,"impact_score":0.1,"ready_for_causal_analysis":True},"intervention":{"executed":True},"replications":[0.1,0.11],"counterfactual_effect":0.0,"alternative_explanations":[]},persist=True)
  assert json.loads(Path(r["latest_path"]).read_text())["analysis_hash"]==r["analysis_hash"]
  assert Path(r["history_path"]).read_text().count("\n")==1
 print("ACEE9_PERSISTENCE_ROUND_TRIP_OK")
if __name__=="__main__": main()
