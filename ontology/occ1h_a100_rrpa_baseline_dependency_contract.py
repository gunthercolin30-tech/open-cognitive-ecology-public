import json
from pathlib import Path
ROOT=Path.home()/"open-cognitive-ecology"
def baseline():
 d=json.loads((ROOT/"validation_artifacts/p159/occ1h/root_blocker_resolution_matrix_v1.json").read_text())
 row=next(x for x in d["rows"] if x["scenario_id"]=="A100")
 return {
  "scenario_id":"A100","canonical_attack_id":"A100","label":"CIS→permanent sovereignty",
  "family":"Cross-Layer / Compound","family_id":"H10",
  "structural_group":"G7_CIS_SOVEREIGNTY_TRANSITION","independent_group":True,
  "root":True,"current_verdict":"INCONCLUSIVE","applicability":"APPLICABILITY_UNDETERMINED",
  "qualification":"CIS_SOVEREIGNTY_TRANSITION_NOT_MATERIALIZED",
  "historical_reason":"CIS_TO_PERMANENT_SOVEREIGNTY_TRANSITION_NOT_EXECUTABLY_MATERIALIZED",
  "resolution_category":"P159_MECHANISM_REQUIRED","dependency_blockers":[],
  "automatic_resolution_forbidden":True,
  "transition_materialized":False,"production_runtime_modified":False,
  "criticality_changed":False,"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,
  "rrp0":"BASELINE_FROZEN","rrp1":"DEPENDENCY_CLOSURE_ESTABLISHED",
  "rrp2":"GAP_CAUSALLY_QUALIFIED","rrp3":"BASELINE_REPRODUCED",
  "rrp4":"RESOLUTION_CONTRACT_FROZEN",
  "resolution_contract":{
   "preserve_root_criticality":True,"preserve_historical_inconclusive":True,
   "no_positive_verdict_without_empirical_proof":True,"no_automatic_resolution":True,
   "no_production_sovereignty_transition_creation":True,
   "fail_closed_on_identity_or_evidence_drift":True}}
