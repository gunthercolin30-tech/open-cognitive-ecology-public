import json,tempfile
from pathlib import Path
from ontology.acee_selection_policy import AceeSelectionPolicy
def main():
 with tempfile.TemporaryDirectory() as d:
  r=AceeSelectionPolicy(root=Path(d)).step(inputs={"selection_id":"test","impact_evaluation":{"comparison_valid":True,"impact_score":0.12,"metric_classifications":{"closure_pressure":"unchanged"}},"causal_analysis":{"ready_for_selection":True,"causal_effect_resolved":True,"causal_probability":0.9,"causal_confidence":0.9,"effect_size":0.12,"effect_direction":"beneficial"},"stability_evidence":{"stability_score":0.9},"simplicity_evidence":{"simplicity_score":0.8},"reversibility_evidence":{"mean_reversibility_score":0.9,"reversibility_assured":True},"non_closure_evidence":{"closure_pressure":0.1,"non_closure_score":0.9},"constitutional_evidence":{"compliant":True,"constitutional_compliance_score":0.9},"governance_evidence":{"approved":True,"governance_score":0.9}},persist=True)
  assert json.loads(Path(r["latest_path"]).read_text())["selection_hash"]==r["selection_hash"]
  assert Path(r["history_path"]).read_text().count("\n")==1
 print("ACEE10_PERSISTENCE_ROUND_TRIP_OK")
if __name__=="__main__": main()
