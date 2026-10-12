
from dataclasses import replace
from ontology.governed_network_effector import GovernedNetworkEffector,GovernedNetworkRequest
from ontology.scoped_handle_broker import ScopedHandleBroker
from ontology.credential_broker import CredentialBroker,TrustedCredentialResolver

class Claim:
    lease_id="L";reservation_id="R";claim_hash="C";adapter_id="A"
class Vault:
    def get_secret(self,name,provider="",requester=""): return "SECRET"
def handle(method="GET",target="api.example"):
    scope={"operations":[method],"targets":[target],"ambient_authority":False,
           "child_inheritance":False,"transferable":False}
    x=ScopedHandleBroker().issue(claim=Claim(),
      lease={"lease_id":"L","reservation_id":"R","operation_id":method,"expires_at":"2099-01-01T00:00:00Z"},
      registry_entry={"adapter_id":"A","effector_id":"NET"},requested_scope=scope,
      authorized_scope=scope,target_binding=target,audience="A",now_iso="2026-10-01T00:00:00Z")
    assert x["status"]=="HANDLE_ISSUED";return x["handle"]
def use(h,method="POST",target="api.example"):
    r={"status":"ACTIVE","expires_at":"2099-01-01T00:00:00Z","credential_ref":"cred://x",
       "allowed_operations":[method],"allowed_targets":[target],"ambient_authority":False,
       "transferable":False,"child_inheritance":False}
    x=CredentialBroker().authorize_use(handle=h,credential_record=r,requested_operation=method,
      requested_target=target,audience="A",now_iso="2026-10-01T00:00:00Z")
    assert x["status"]=="CREDENTIAL_USE_AUTHORIZED";return x["use"]
def resolver():
    return TrustedCredentialResolver(vault=Vault(),credential_registry={
      "cred://x":{"status":"ACTIVE","provider":"openai","secret_name":"key"}})
def test_anonymous_get_requires_handle_and_uses_injected_transport():
    seen={}
    def tr(**kw):seen.update(kw);return {"status_code":200}
    e=GovernedNetworkEffector(transport=tr)
    r=GovernedNetworkRequest("GET","https://api.example/x",{})
    assert e.execute(request=r,handle=None,brokered_use=None,adapter_id="A",effector_id="NET",now_iso="2026-10-01T00:00:00Z")["status"]=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"
    x=e.execute(request=r,handle=handle(),brokered_use=None,adapter_id="A",effector_id="NET",now_iso="2026-10-01T00:00:00Z")
    assert x["status"]=="EFFECT_CONFIRMED" and seen["url"]==r.url
def test_ambient_authorization_header_is_forbidden():
    e=GovernedNetworkEffector(transport=lambda **k:{})
    r=GovernedNetworkRequest("GET","https://api.example/x",{"Authorization":"Bearer RAW"})
    assert e.execute(request=r,handle=handle(),brokered_use=None,adapter_id="A",effector_id="NET",now_iso="2026-10-01T00:00:00Z")["reason"]=="ambient_credential_header_forbidden"
def test_brokered_secret_only_reaches_transport():
    seen={}
    def tr(**kw):seen.update(kw);return {"status_code":200}
    h=handle("POST");u=use(h)
    e=GovernedNetworkEffector(transport=tr,credential_resolver=resolver())
    r=GovernedNetworkRequest("POST","https://api.example/v1",{},b"{}")
    x=e.execute(request=r,handle=h,brokered_use=u,adapter_id="A",effector_id="NET",now_iso="2026-10-01T00:00:00Z")
    assert x["status"]=="EFFECT_CONFIRMED"
    assert seen["headers"]["Authorization"]=="Bearer SECRET"
    assert "SECRET" not in repr(x)
def test_wrong_target_fails_before_transport():
    called=[]
    e=GovernedNetworkEffector(transport=lambda **k:called.append(k))
    r=GovernedNetworkRequest("GET","https://other.example/x",{})
    x=e.execute(request=r,handle=handle(),brokered_use=None,adapter_id="A",effector_id="NET",now_iso="2026-10-01T00:00:00Z")
    assert x["reason"]=="target_mismatch" and not called
def test_timeout_is_indeterminate_and_not_blind_retry():
    def tr(**kw):raise TimeoutError()
    e=GovernedNetworkEffector(transport=tr)
    r=GovernedNetworkRequest("GET","https://api.example/x",{},idempotent=True)
    x=e.execute(request=r,handle=handle(),brokered_use=None,adapter_id="A",effector_id="NET",now_iso="2026-10-01T00:00:00Z")
    assert x["status"]=="EFFECT_STATE_INDETERMINATE" and x["retry_allowed"] is False
