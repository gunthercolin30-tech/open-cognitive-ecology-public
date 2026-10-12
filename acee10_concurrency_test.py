import json,tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from ontology.acee_selection_policy import AceeSelectionPolicy
PAYLOAD={"selection_id":"test","impact_evaluation":{"comparison_valid":True,"impact_score":0.12,"metric_classifications":{"closure_pressure":"unchanged"}},"causal_analysis":{"ready_for_selection":True,"causal_effect_resolved":True,"causal_probability":0.9,"causal_confidence":0.9,"effect_size":0.12,"effect_direction":"beneficial"},"stability_evidence":{"stability_score":0.9},"simplicity_evidence":{"simplicity_score":0.8},"reversibility_evidence":{"mean_reversibility_score":0.9,"reversibility_assured":True},"non_closure_evidence":{"closure_pressure":0.1,"non_closure_score":0.9},"constitutional_evidence":{"compliant":True,"constitutional_compliance_score":0.9},"governance_evidence":{"approved":True,"governance_score":0.9}}
def one(args):
 root,i=args; x=dict(PAYLOAD); x["selection_id"]=f"thread-{i}"; return AceeSelectionPolicy(root=Path(root)).step(inputs=x,persist=True)
def main():
 with tempfile.TemporaryDirectory() as d:
  with ThreadPoolExecutor(max_workers=8) as ex: rows=list(ex.map(one,[(d,i) for i in range(20)]))
  history=Path(rows[0]["history_path"]); lines=[json.loads(x) for x in history.read_text().splitlines() if x.strip()]
  assert len(lines)==20 and len({x["selection_id"] for x in lines})==20
 print("ACEE10_CONCURRENCY_OK")
if __name__=="__main__": main()
