from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];P=R/"validation_artifacts/p159/occ1h/a071/a071_rrpv21_macros_a_to_e_existing_authority_v1.json"
def d():return json.loads(P.read_text())
def test_identity_and_gap():
 x=d();assert x["scenario"]=="A071";assert x["identity"]=="SHARED_BUG";assert x["RRP_A"]["qualification"]=="SHARED_TCB_BUG_RESISTANCE_NOT_EMPIRICALLY_MATERIALIZED"
def test_fail_closed_materiality():
 x=d();assert x["RRP_C"]["status"]=="ROOT_UNDETERMINED + BLOCKING";assert x["RRP_C"]["rrp12"]=="BLOCKING_INCONCLUSIVE"
def test_existing_authority_and_minimality():
 x=d();e=x["RRP_E"];assert e["rrp20"]=="EXISTING_NORMATIVE_AUTHORITY_SUFFICIENT";assert e["technical_remediation_authorized"] is True;assert e["rrp19"]["new_normative_degrees_of_freedom"]==0
def test_boundaries():
 x=d();assert x["RRP_F"]["status"]=="NOT_OPENED";assert x["boundaries"]=={"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False}
