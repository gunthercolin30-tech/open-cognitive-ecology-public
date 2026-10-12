from copy import deepcopy
from pathlib import Path
import json
import pytest
from ontology.p160_normative_decision_persistence import *
from validation.p160g_normative_decision_sealing_defensive_crown_v1_test import build

def test_manifest_boundaries():
    m=manifest();assert m["boundaries"]=={"authorization_created":False,"authorization_token_created":False,"execution_performed":False,"p161_opened":False}

def test_jp_sealed_roundtrip_and_immutable_store(tmp_path):
    d=build();r=P160JRuntime(tmp_path);rc=r.commit(d,"e1");assert rc["new_status"]=="COMMITTED";assert r.store.load(rc["decision_id"])==d
    bad=deepcopy(d);bad["eligibility"]="INELIGIBLE"
    with pytest.raises(ValueError):r.store.persist(bad)

def test_jp_journal_idempotency_and_duplicate_conflict(tmp_path):
    j=NormativeDecisionJournal(tmp_path);a=j.append("x",{"v":1});b=j.append("x",{"v":1});assert a==b and j.verify()
    with pytest.raises(ValueError):j.append("x",{"v":2})

def test_jp_corruption_detection(tmp_path):
    j=NormativeDecisionJournal(tmp_path);j.append("x",{"v":1});p=j.path;p.write_text(p.read_text().replace('"v":1','"v":2'));assert not j.verify()

def test_jr_restart_reconstructs_committed_without_authorization(tmp_path):
    d=build();r=P160JRuntime(tmp_path);r.commit(d,"e1");x=P160JRuntime(tmp_path).startup_reconcile();assert x["startup_state"]=="STARTUP_VALID";assert x["authorization_created"] is False

def test_jr_terminal_no_revive(tmp_path):
    d=build();r=P160JRuntime(tmp_path);did=r.commit(d,"e1")["decision_id"];r.transition(did,"EXPIRED","expiry","e2")
    with pytest.raises(ValueError):r.transition(did,"COMMITTED","revive","e3")

def test_jr_registry_not_ultimate_truth(tmp_path):
    d=build();r=P160JRuntime(tmp_path);did=r.commit(d,"e1")["decision_id"];r.registry.state["decisions"][did]["status"]="EXPIRED"
    r.registry.path.write_text(json.dumps(r.registry.state,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    x=P160JRuntime(tmp_path).startup_reconcile();assert x["startup_state"]=="STARTUP_RECONCILIATION_REQUIRED"

def test_jr_temporal_continuity():
    assert temporal_continuity("TRUSTED",clock_rollback=True)=="RECONSTRUCTED";assert temporal_continuity("TRUSTED",continuity_proven=False)=="UNCERTAIN"

def test_jb_restore_requires_all_proofs():
    good={k:True for k in ("lineage_valid","constitutional_version_compatible","revocations_preserved","supersessions_preserved","journal_continuity","profile_compatible","authority_compatible","expiry_preserved")}
    assert restore_eligibility(good)["status"]=="RESTORE_ELIGIBLE";good["revocations_preserved"]=False;assert restore_eligibility(good)["status"]=="RESTORE_REJECTED"

def test_jb_branch_conflict_not_newest_wins():
    x=reconcile_branches({"journal_hash":"a","ancestry":[],"timestamp":999},{"journal_hash":"b","ancestry":[],"timestamp":1});assert x["status"]=="CONTINUITY_UNCERTAIN" and x["selected"] is None

def test_jm_roundtrip_preserves_unknown_contested_expiry_scope_conditions_semantics():
    x={"status":"UNKNOWN","conflict":"CONTESTED","expiry":"2030Z","scope":["a"],"conditions":[{"x":1}],"semantic_hash":"abc"};assert roundtrip(x)==x

def test_jm_unsupported_critical_field_rejected():
    x={"critical_fields":["semantic_hash","new_critical"]};assert migrate_record(x,["semantic_hash"])["status"]=="MIGRATION_REJECTED"

def test_jm_explicit_normative_delta():
    x={"critical_fields":["semantic_hash"],"semantic_hash":"a"};y=migrate_record(x,["semantic_hash"],{"semantic_hash":["a","b"]});assert y["record"]["migration_status"]=="EXPLICIT_NORMATIVE_DELTA"

def test_jc_dependency_vector_change_requires_revalidation():
    assert compare_dependency_vector({"profile_version":"1"},{"profile_version":"2"})["status"]=="REVALIDATE_REQUIRED"

def test_jc_shared_target_detected():
    d1=build();d2=deepcopy(d1);x=concurrent_decision_context([d1,d2]);assert x["interaction_uncertainty"] is True and x["authorization_created"] is False

def test_jc_dependency_drift_at_startup(tmp_path):
    d=build();r=P160JRuntime(tmp_path);did=r.commit(d,"e1")["decision_id"];dep=dependency_vector(d);dep["profile_version"]="changed"
    x=P160JRuntime(tmp_path).startup_reconcile({did:dep});assert "MATERIAL_DEPENDENCY_DRIFT:"+did in x["issues"]

def test_jt_expired_never_revived_by_clock_model():
    assert temporal_continuity("INVALID",clock_rollback=True)=="INVALID"

def test_boundary_commit_is_not_authorization(tmp_path):
    d=build();x=P160JRuntime(tmp_path).commit(d,"e1");assert x["authorization_created"] is False and x["authorization_token_created"] is False and x["execution_performed"] is False and x["p161_opened"] is False
