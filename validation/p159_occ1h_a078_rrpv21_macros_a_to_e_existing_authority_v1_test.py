from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
P=R/"validation_artifacts/p159/occ1h/a078/a078_rrpv21_macros_a_to_e_existing_authority_v1.json"
def d(): return json.loads(P.read_text())
def test_identity_and_gap(): assert d()["scenario"]=="A078" and d()["RRP_C"]["final_disposition_candidate"]=="ROOT_UNDETERMINED + BLOCKING"
def test_boundary(): assert d()["RRP_D"]["runtime_consumer_materialized"] is False and d()["RRP_D"]["p160_required_for_bounded_assurance_experiment"] is False
def test_authority(): assert d()["RRP_E"]["rrp20"]=="EXISTING_NORMATIVE_AUTHORITY_SUFFICIENT" and d()["RRP_E"]["new_normative_degrees_of_freedom"]==0
def test_no_opening(): assert d()["boundaries"]=={"occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False}
