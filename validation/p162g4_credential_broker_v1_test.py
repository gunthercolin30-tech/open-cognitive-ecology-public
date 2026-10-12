import json
from concurrent.futures import ThreadPoolExecutor
from ontology.governed_execution_adapter import ExecutionClaim
from ontology.scoped_handle_broker import ScopedHandleBroker
from ontology.credential_broker import CredentialBroker

def claim():
    return ExecutionClaim("R1","L1","A1","EX1","2026",1,"CH")

def lease():
    return {"lease_id":"L1","reservation_id":"R1","operation_id":"WRITE",
            "expires_at":"2999-01-01T00:00:00+00:00"}

def registry():
    return {"adapter_id":"A1","effector_id":"FS1"}

def scope():
    return {"path":"/tmp/exact","operations":["WRITE"],
            "ambient_authority":False,"child_inheritance":False,"transferable":False}

def handle():
    b=ScopedHandleBroker()
    x=b.issue(claim=claim(),lease=lease(),registry_entry=registry(),
              requested_scope=scope(),authorized_scope=scope(),
              target_binding={"path":"/tmp/exact"},audience="A1",
              now_iso="2026-10-01T16:00:00+00:00")
    assert x["status"]=="HANDLE_ISSUED"
    return x["handle"]

def credential(**kw):
    d={"credential_ref":"vault://cred/1","status":"ACTIVE",
       "expires_at":"2999-01-01T00:00:00+00:00",
       "allowed_operations":["WRITE","DELETE"],
       "allowed_targets":[{"path":"/tmp/exact"},{"path":"/tmp/other"}],
       "ambient_authority":False,"transferable":False,"child_inheritance":False}
    d.update(kw); return d

def auth(b,cred=None,**kw):
    return b.authorize_use(handle=kw.get("handle",handle()),
        credential_record=cred if cred is not None else credential(),
        requested_operation=kw.get("requested_operation","WRITE"),
        requested_target=kw.get("requested_target",{"path":"/tmp/exact"}),
        audience=kw.get("audience","A1"),
        now_iso="2026-10-01T16:00:00+00:00")

def test_valid_use_is_opaque_and_noncausal():
    x=auth(CredentialBroker()); assert x["status"]=="CREDENTIAL_USE_AUTHORIZED"
    u=x["use"]; assert u.raw_secret_disclosed is False
    assert u.allowed_operation=="WRITE" and u.target_binding=={"path":"/tmp/exact"}
    assert not x["raw_secret_disclosed"] and not x["effector_called"] and not x["real_world_effect_performed"]

def test_broad_credential_does_not_widen_handle():
    assert auth(CredentialBroker(),requested_operation="DELETE")["reason"]=="operation_outside_handle"
    assert auth(CredentialBroker(),requested_target={"path":"/tmp/other"})["reason"]=="target_outside_handle"

def test_wrong_audience():
    assert auth(CredentialBroker(),audience="OTHER")["reason"]=="wrong_audience"

def test_revoked():
    assert auth(CredentialBroker(),credential(status="REVOKED"))["reason"]=="credential_not_active"

def test_expired():
    assert auth(CredentialBroker(),credential(expires_at="2020-01-01T00:00:00+00:00"))["reason"]=="credential_expired"

def test_unknown_ref():
    assert auth(CredentialBroker(),credential(credential_ref="UNKNOWN"))["reason"]=="credential_ref_undetermined"

def test_secret_field_rejected():
    c=credential(); c["raw_secret"]="DO_NOT_EXPOSE"
    assert auth(CredentialBroker(),c)["reason"]=="raw_secret_material_forbidden"

def test_nested_secret_field_rejected():
    c=credential(); c["metadata"]={"api_key":"DO_NOT_EXPOSE"}
    assert auth(CredentialBroker(),c)["reason"]=="raw_secret_material_forbidden"

def test_ambient_authority_rejected():
    assert auth(CredentialBroker(),credential(ambient_authority=True))["reason"]=="ambient_authority_forbidden"

def test_transfer_rejected():
    assert auth(CredentialBroker(),credential(transferable=True))["reason"]=="transfer_forbidden"

def test_child_inheritance_rejected():
    assert auth(CredentialBroker(),credential(child_inheritance=True))["reason"]=="child_inheritance_forbidden"

def test_credential_operation_policy_rechecked():
    assert auth(CredentialBroker(),credential(allowed_operations=["READ"]))["reason"]=="credential_operation_not_allowed"

def test_credential_target_policy_rechecked():
    assert auth(CredentialBroker(),credential(allowed_targets=[{"path":"/tmp/other"}]))["reason"]=="credential_target_not_allowed"

def test_duplicate_use_blocked():
    b=CredentialBroker(); assert auth(b)["status"]=="CREDENTIAL_USE_AUTHORIZED"
    assert auth(b)["reason"]=="duplicate_credential_use"

def test_single_use_consumption():
    b=CredentialBroker(); u=auth(b)["use"]
    assert b.consume_once(u.broker_use_id) is True
    assert b.consume_once(u.broker_use_id) is False

def test_concurrent_consumption_single_winner():
    b=CredentialBroker(); u=auth(b)["use"]
    with ThreadPoolExecutor(max_workers=8) as e:
        out=list(e.map(lambda _:b.consume_once(u.broker_use_id),range(20)))
    assert sum(out)==1

def test_public_record_has_no_secret_material():
    b=CredentialBroker(); u=auth(b)["use"]; r=b.public_record(u)
    text=json.dumps(r,sort_keys=True)
    assert "DO_NOT_EXPOSE" not in text
    assert r["raw_secret_disclosed"] is False
    assert r["credential_ref"]=="vault://cred/1"

def test_missing_handle():
    b=CredentialBroker()
    x=b.authorize_use(handle=None,credential_record=credential(),
        requested_operation="WRITE",requested_target={"path":"/tmp/exact"},
        audience="A1",now_iso="2026-10-01T16:00:00+00:00")
    assert x["reason"]=="missing_scoped_handle"
