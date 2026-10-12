from ontology.p160_normative_decision_persistence import *
from validation.p160g_normative_decision_sealing_defensive_crown_v1_test import build
def test_transaction_order_and_precommit_unusable(tmp_path):
 x=P160JRuntime(tmp_path).commit(build(),"tx");assert [z["stage"] for z in x["transaction_stages"]]==["PREPARE","VALIDATE","SEAL","PERSIST","COMMIT"];assert [z["usable"] for z in x["transaction_stages"]]==[False,False,False,False,True]
def test_receipt_complete(tmp_path):
 x=P160JRuntime(tmp_path).commit(build(),"tx")
 for k in ("transition_id","decision_id","previous_status","new_status","reason","source_event","timestamp","journal_hash","registry_version","receipt_hash"):assert k in x
 assert x["timestamp"].endswith("Z")
def test_transaction_idempotent(tmp_path):
 r=P160JRuntime(tmp_path);d=build();a=r.commit(d,"tx");b=r.commit(d,"tx");assert a["decision_id"]==b["decision_id"];assert len(r.journal.entries())==5
def test_restart_states_preserved():
 for s in ("UNKNOWN","PENDING","REVIEW_REQUIRED","ARBITRATION_PENDING","REVOKED","EXPIRED","STALE","SEALED"):assert preserve_restart_state(s)==s
def test_all_startup_states_reachable():
 assert classify_startup_state([])=="STARTUP_VALID";assert classify_startup_state(["NONCRITICAL_CACHE"],True)=="STARTUP_DEGRADED";assert classify_startup_state(["REGISTRY_X"])=="STARTUP_RECONCILIATION_REQUIRED";assert classify_startup_state(["JOURNAL_CONTINUITY_INVALID"])=="STARTUP_CONTINUITY_UNCERTAIN";assert classify_startup_state(["SAFE_MODE_REQUIRED:constitution"])=="STARTUP_SAFE_MODE_REQUIRED"
def test_authority_consumption_planned_only():
 x=planned_authority_consumption("human:1",{"budget":1});assert x["effective_consumption"] is False and x["authorization_created"] is False
def test_decision_not_execution():
 x=decision_execution_separation("COMMITTED",False);assert x["execution_inferred_from_decision"] is False and x["retroactive_authorization"] is False
def test_trace_helper():
 assert [x["stage"] for x in transactional_creation_trace(build())]==["PREPARE","VALIDATE","SEAL","PERSIST","COMMIT"]
def test_replay_ignores_precommit_stages(tmp_path):
 r=P160JRuntime(tmp_path);did=r.commit(build(),"tx")["decision_id"];assert P160JRuntime(tmp_path).startup_reconcile()["reconstructed"][did]["status"]=="COMMITTED"
