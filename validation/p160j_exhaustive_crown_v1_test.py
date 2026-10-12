from copy import deepcopy
from pathlib import Path
import json, os, shutil
import pytest
from ontology.p160_normative_decision_persistence import *
from validation.p160g_normative_decision_sealing_defensive_crown_v1_test import build

# J-P Persistence
def test_jp_unknown_contested_review_postconditions_expiry_invalidation_roundtrip():
    x={"status":"UNKNOWN","conflict":"CONTESTED","review":"REQUIRED","postconditions":[{"id":"p1","status":"UNKNOWN"}],"expiry":"2030-01-01T00:00:00Z","lifecycle":"INVALIDATED"}
    assert roundtrip(x)==x

def test_jp_checkpoint_detects_corruption(tmp_path):
    j=NormativeDecisionJournal(tmp_path);j.append("a",{"x":1});entries=j.entries();cp=verified_checkpoint(entries)
    assert verify_checkpoint(cp,entries)
    bad=deepcopy(entries);bad[0]["payload"]["x"]=2
    assert not verify_checkpoint(cp,bad)

def test_jp_privacy_raw_personal_data_rejected_by_policy():
    assert privacy_safe_journal_payload({"decision_ref":"h","profile_hash":"x"})
    assert not privacy_safe_journal_payload({"raw_email":"person@example.invalid"})

# J-R Restart / crash / partial journal
def test_jr_crash_before_commit_leaves_no_committed_registry(tmp_path):
    d=build();r=P160JRuntime(tmp_path);r.store.persist(d)
    x=P160JRuntime(tmp_path).startup_reconcile()
    assert x["reconstructed"]=={} and x["authorization_created"] is False

def test_jr_partial_journal_detected(tmp_path):
    j=NormativeDecisionJournal(tmp_path);j.append("a",{"x":1})
    with j.path.open("a",encoding="utf-8") as f:f.write('{"event_id":"TORN"')
    with pytest.raises(json.JSONDecodeError):j.entries()

def test_jr_revocation_and_expiry_remain_terminal(tmp_path):
    d=build();r=P160JRuntime(tmp_path);did=r.commit(d,"c")["decision_id"];r.transition(did,"INVALIDATED","revocation","r")
    with pytest.raises(ValueError):r.transition(did,"COMMITTED","restart","x")

def test_jr_startup_dependency_drift_never_authorizes(tmp_path):
    d=build();r=P160JRuntime(tmp_path);did=r.commit(d,"c")["decision_id"];dep=dependency_vector(d);dep["authority_version"]="revoked"
    x=P160JRuntime(tmp_path).startup_reconcile({did:dep});assert x["startup_state"]=="STARTUP_RECONCILIATION_REQUIRED";assert x["authorization_created"] is False

# J-C Concurrency
def test_jc_duplicate_event_different_payload_conflicts(tmp_path):
    j=NormativeDecisionJournal(tmp_path);j.append("same",{"request":"a"})
    with pytest.raises(ValueError):j.append("same",{"request":"b"})

def test_jc_individually_eligible_shared_target_marks_interaction_uncertainty():
    a=build();b=deepcopy(a);x=concurrent_decision_context([a,b])
    assert x["interaction_uncertainty"] is True and x["authorization_created"] is False

@pytest.mark.parametrize("field",["profile_version","authority_version","target_version","emergency_version","related_actions_version","policy_version"])
def test_jc_material_races_require_revalidation(field):
    a={field:"v1"};b={field:"v2"};assert compare_dependency_vector(a,b)["status"]=="REVALIDATE_REQUIRED"

def test_jc_snapshot_version_vector_change_requires_retry():
    assert snapshot_consistency({"profile":1,"authority":4},{"profile":2,"authority":4})["status"]=="RETRY_REQUIRED"

def test_jc_cumulative_temporary_exceptions_detected():
    x=active_exception_context([{"class":"emergency","temporary":True,"active":True},{"class":"emergency","temporary":True,"active":True}])
    assert x["status"]=="CUMULATIVE_EXCEPTION_REVIEW_REQUIRED"

def test_jc_boundary_contract_contains_compare_and_authorize_inputs_only():
    d=build();x=p160_p161_boundary_contract(d)
    assert set(("decision_hash","dependency_vector","authority_state_hash","context_fingerprint","expiry"))<=set(x)
    assert x["authorization_created"] is False and x["execution_performed"] is False

# J-M Migration
def test_jm_unknown_never_default_valid():
    x={"critical_fields":["status"],"status":"UNKNOWN"};y=migrate_record(x,["status"]);assert y["record"]["status"]=="UNKNOWN"

def test_jm_pre_post_authority_expiry_historical_readability_preserved():
    x={"critical_fields":["semantic_hash"],"semantic_hash":"h","authority_status":"UNKNOWN","expiry":"2030Z","preconditions":[{"x":1}],"postconditions":[{"y":2}],"historical_version":"v1"}
    y=migrate_record(x,["semantic_hash"])["record"]
    for k in ("semantic_hash","authority_status","expiry","preconditions","postconditions","historical_version"):assert y[k]==x[k]

def test_jm_no_silent_default_for_missing_critical_field():
    x={"critical_fields":["new_required"],"semantic_hash":"h"};assert migrate_record(x,["semantic_hash"])["status"]=="MIGRATION_REJECTED"

# J-T Temporal
def test_jt_clock_forward_expiry_is_invalid_and_rollback_cannot_revive():
    assert temporal_expiry_state("TRUSTED",True,False)=="INVALID"
    assert temporal_expiry_state("INVALID",True,True)=="INVALID"

def test_jt_timezone_dst_presentation_does_not_change_canonical_hash():
    a={"instant":"2026-10-25T01:30:00Z","timezone_presentation":"Europe/Paris"}
    b=deepcopy(a);assert canonical_platform_vector(a)["sha256"]==canonical_platform_vector(b)["sha256"]

def test_jt_emergency_expiry_and_renewal_counter_preserved_roundtrip():
    x={"emergency_expiry":"2026-10-01T10:00:00Z","renewal_counter":3};assert roundtrip(x)==x

# J-B Backup/restore
def test_jb_real_isolated_backup_restore_preserves_terminal_state(tmp_path):
    src=tmp_path/"src";bak=tmp_path/"backup";dst=tmp_path/"restore"
    d=build();r=P160JRuntime(src);did=r.commit(d,"c")["decision_id"];r.transition(did,"EXPIRED","expiry","e")
    shutil.copytree(src,bak);shutil.copytree(bak,dst)
    rr=P160JRuntime(dst);assert rr.registry.get(did)["status"]=="EXPIRED";assert rr.startup_reconcile()["startup_state"]=="STARTUP_VALID"

def test_jb_missing_tail_detected(tmp_path):
    d=build();r=P160JRuntime(tmp_path);did=r.commit(d,"c")["decision_id"];r.transition(did,"EXPIRED","expiry","e")
    lines=r.journal.path.read_text().splitlines();r.journal.path.write_text(lines[0]+"\n")
    assert P160JRuntime(tmp_path).startup_reconcile()["startup_state"]=="STARTUP_RECONCILIATION_REQUIRED"

def test_jb_conflicting_branches_are_uncertain_not_newest():
    assert reconcile_branches({"journal_hash":"A","ancestry":[],"timestamp":999},{"journal_hash":"B","ancestry":[],"timestamp":1})["status"]=="CONTINUITY_UNCERTAIN"

# Cross-cutting annex requirements
def test_dependency_graph_material_propagation_only():
    g=[{"type":"DEPENDS_ON","source":"A","target":"B"},{"type":"REVIEWS","source":"C","target":"D"}]
    assert dependency_graph_validate(g)["status"]=="VALID";assert materially_dependent(g,"A")==["B"]

def test_profile_activation_invalidates_unconsumed_old_profile_by_default():
    d=build();d["decision_id"]="d1";d["bindings"]["compiled_profile_hash"]="old";d["consumed"]=False
    assert profile_activation_effect([d],"old","new")["d1"]=="REVALIDATE_REQUIRED"

def test_retroactive_review_never_authorizes_execution():
    x=retroactive_review(True,"REPAIR");assert x["retroactive_authorization"] is False and x["authorization_created"] is False

# J-X local canonical portability vectors (two-host proof remains external)
def test_jx_filesystem_ordering_canonical_equivalence():
    a={"b":2,"a":1};b={"a":1,"b":2};assert canonical_platform_vector(a)==canonical_platform_vector(b)

def test_jx_unicode_locale_canonical_equivalence():
    x={"status":"UNKNOWN","label":"éligibilité","n":1};assert canonical_platform_vector(roundtrip(x))==canonical_platform_vector(x)

def test_jx_portable_vector_has_no_platform_path_dependency():
    x={"decision_hash":"abc","timezone":"UTC","locale":"C"};v=canonical_platform_vector(x);assert "/" not in v["sha256"] and len(v["sha256"])==64
