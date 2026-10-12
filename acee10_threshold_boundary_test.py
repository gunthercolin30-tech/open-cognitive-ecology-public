from copy import deepcopy
from ontology.acee_selection_policy import AceeSelectionPolicy
BASE={"selection_id":"test","impact_evaluation":{"comparison_valid":True,"impact_score":0.12,"metric_classifications":{"closure_pressure":"unchanged"}},"causal_analysis":{"ready_for_selection":True,"causal_effect_resolved":True,"causal_probability":0.9,"causal_confidence":0.9,"effect_size":0.12,"effect_direction":"beneficial"},"stability_evidence":{"stability_score":0.9},"simplicity_evidence":{"simplicity_score":0.8},"reversibility_evidence":{"mean_reversibility_score":0.9,"reversibility_assured":True},"non_closure_evidence":{"closure_pressure":0.1,"non_closure_score":0.9},"constitutional_evidence":{"compliant":True,"constitutional_compliance_score":0.9},"governance_evidence":{"approved":True,"governance_score":0.9}}
def main():
 a=deepcopy(BASE); a["thresholds"]={"minimum_causal_confidence":0.9}; assert AceeSelectionPolicy().step(inputs=a)["decision"]=="accept"
 b=deepcopy(BASE); b["thresholds"]={"minimum_causal_confidence":0.9000001}; assert AceeSelectionPolicy().step(inputs=b)["decision"]=="sandbox_longer"
 c=deepcopy(BASE); c["thresholds"]={"minimum_stability_score":0.9}; assert AceeSelectionPolicy().step(inputs=c)["decision"]=="accept"
 d=deepcopy(BASE); d["thresholds"]={"minimum_stability_score":0.9000001}; assert AceeSelectionPolicy().step(inputs=d)["decision"]=="sandbox_longer"
 print("ACEE10_THRESHOLD_BOUNDARY_OK")
if __name__=="__main__": main()
