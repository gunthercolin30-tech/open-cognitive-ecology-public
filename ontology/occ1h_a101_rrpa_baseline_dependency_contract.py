from pathlib import Path
import hashlib
ROOT=Path.home()/"open-cognitive-ecology"
def evidence():
 p=ROOT/"ontology/occ1h_a101_post_a075_current_evidence.py"
 t=p.read_text(encoding="utf-8")
 required=["A075_CURRENT_VERDICT=\"RESISTED\"","CURRENT_VERDICT=\"INCONCLUSIVE\"","REACHABILITY_CLASSIFICATION=\"PATH_NOT_MATERIALIZED\"","CONFIRMED_EXECUTABLE_A101_EDGES=0"]
 ok=all(x in t for x in required)
 return {"scenario":"A101","rrp0":"BASELINE_FROZEN","rrp1":"DEPENDENCY_CLOSURE_ESTABLISHED","rrp2":"GAP_CAUSALLY_QUALIFIED","rrp3":"BASELINE_REPRODUCED" if ok else "BASELINE_DIVERGED","rrp4":"RESOLUTION_CONTRACT_FROZEN","historical_dependency":"A075","a075_current_verdict":"RESISTED","current_gap":"NO_CONFIRMED_EXECUTABLE_ACEE_TO_OCC1F_PATH_AND_A101_SPECIFIC_EMPIRICAL_RESISTANCE_NOT_PROVEN","reachability":"PATH_NOT_MATERIALIZED","confirmed_executable_a101_edges":0,"resolution_contract":"Do not infer resistance from A075 resolution or similarly named ACEE/OCC1F components. Promote only from explicit governed executable ACEE-to-OCC1F weakening-path evidence and A101-specific empirical discrimination; otherwise remain fail-closed.","criticality_changed":False,"verdict_changed":False,"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False,"functional_only":True,"phenomenology_undetermined":True}
