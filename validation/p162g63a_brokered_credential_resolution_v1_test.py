
from dataclasses import replace
from ontology.credential_broker import CredentialBroker, TrustedCredentialResolver
from ontology.scoped_handle_broker import ScopedHandleBroker

class Vault:
    def __init__(self): self.calls=[]
    def get_secret(self,name,provider="",requester=""):
        self.calls.append((name,provider,requester)); return "TOP_SECRET"

def chain():
    class C:
        lease_id="L"; reservation_id="R"; claim_hash="C"; adapter_id="A"
    lease={"lease_id":"L","reservation_id":"R","operation_id":"POST",
           "expires_at":"2099-01-01T00:00:00Z"}
    registry={"adapter_id":"A","effector_id":"E"}
    scope={"operations":["POST"],"targets":["api.example"],
           "ambient_authority":False,"child_inheritance":False,"transferable":False}
    hb=ScopedHandleBroker()
    h=hb.issue(claim=C(),lease=lease,registry_entry=registry,
               requested_scope=scope,authorized_scope=scope,
               target_binding="api.example",audience="A",
               now_iso="2026-10-01T00:00:00Z")
    assert h["status"]=="HANDLE_ISSUED"; h=h["handle"]
    cb=CredentialBroker()
    rec={"status":"ACTIVE","expires_at":"2099-01-01T00:00:00Z",
         "credential_ref":"cred://openai/main","allowed_operations":["POST"],
         "allowed_targets":["api.example"],"ambient_authority":False,
         "transferable":False,"child_inheritance":False}
    u=cb.authorize_use(handle=h,credential_record=rec,requested_operation="POST",
                       requested_target="api.example",audience="A",
                       now_iso="2026-10-01T00:00:00Z")
    assert u["status"]=="CREDENTIAL_USE_AUTHORIZED"
    return u["use"]

def resolver():
    v=Vault()
    return v,TrustedCredentialResolver(vault=v,credential_registry={
      "cred://openai/main":{"status":"ACTIVE","provider":"openai",
                            "secret_name":"openai_api_key"}})

def test_valid_resolution_is_tcb_only_and_public_record_redacts():
    v,r=resolver();u=chain()
    x=r.resolve_for_effector(brokered_use=u,adapter_id="A",effector_id="E",
      operation="POST",target="api.example",now_iso="2026-10-01T00:00:00Z")
    assert x["status"]=="CREDENTIAL_RESOLVED_FOR_EFFECTOR"
    assert x["secret"]=="TOP_SECRET"
    assert x["raw_secret_disclosed_to_capability"] is False
    assert x["raw_secret_disclosed_to_executor"] is False
    assert "secret" not in r.public_record(x)
    assert v.calls==[("openai_api_key","openai","trusted_effector:E")]

def test_unknown_ref_fails_closed():
    v,r=resolver();u=replace(chain(),credential_ref="UNKNOWN_REF")
    x=r.resolve_for_effector(brokered_use=u,adapter_id="A",effector_id="E",
      operation="POST",target="api.example",now_iso="2026-10-01T00:00:00Z")
    assert x["status"]=="CREDENTIAL_RESOLUTION_BLOCKED"
    assert x["secret"] is None and not v.calls

def test_wrong_binding_fails_before_vault():
    v,r=resolver();u=chain()
    x=r.resolve_for_effector(brokered_use=u,adapter_id="WRONG",effector_id="E",
      operation="POST",target="api.example",now_iso="2026-10-01T00:00:00Z")
    assert x["status"]=="CREDENTIAL_RESOLUTION_BLOCKED" and not v.calls

def test_resolution_is_one_shot():
    v,r=resolver();u=chain()
    kw=dict(brokered_use=u,adapter_id="A",effector_id="E",operation="POST",
            target="api.example",now_iso="2026-10-01T00:00:00Z")
    assert r.resolve_for_effector(**kw)["status"]=="CREDENTIAL_RESOLVED_FOR_EFFECTOR"
    assert r.resolve_for_effector(**kw)["reason"]=="credential_resolution_replay"
    assert len(v.calls)==1

def test_expired_fails_closed():
    v,r=resolver();u=replace(chain(),expires_at="2020-01-01T00:00:00Z")
    x=r.resolve_for_effector(brokered_use=u,adapter_id="A",effector_id="E",
      operation="POST",target="api.example",now_iso="2026-10-01T00:00:00Z")
    assert x["reason"]=="credential_use_expired" and not v.calls
