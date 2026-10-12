"""P162-G4 Credential Broker — opaque, bounded, non-causal credential mediation."""
from dataclasses import dataclass
from hashlib import sha256
from threading import RLock
import json

@dataclass(frozen=True)
class BrokeredCredentialUse:
    broker_use_id: str
    lease_id: str
    reservation_id: str
    claim_hash: str
    handle_id: str
    adapter_id: str
    effector_id: str
    credential_ref: str
    allowed_operation: str
    target_binding: object
    audience: str
    expires_at: str
    raw_secret_disclosed: bool = False
    single_use: bool = True
    transferable: bool = False
    child_inheritance: bool = False
    ambient_authority: bool = False

class CredentialBroker:
    """Issues an opaque one-shot credential-use grant. Never returns secret material."""
    _FORBIDDEN_SECRET_KEYS = {
        "secret","raw_secret","password","token","api_key","private_key",
        "credential_value","access_token","refresh_token"
    }

    def __init__(self):
        self._lock = RLock()
        self._issued = {}
        self._consumed = set()

    @classmethod
    def _contains_secret_material(cls, obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if str(k).lower() in cls._FORBIDDEN_SECRET_KEYS:
                    return True
                if cls._contains_secret_material(v):
                    return True
        elif isinstance(obj, (list, tuple)):
            return any(cls._contains_secret_material(x) for x in obj)
        return False

    def authorize_use(self, *, handle, credential_record, requested_operation,
                      requested_target, audience, now_iso):
        if handle is None:
            return {"status":"CREDENTIAL_USE_BLOCKED","reason":"missing_scoped_handle","use":None}
        if credential_record is None or self._contains_secret_material(credential_record):
            return {"status":"CREDENTIAL_USE_BLOCKED","reason":"raw_secret_material_forbidden","use":None}
        if credential_record.get("status") != "ACTIVE":
            return {"status":"CREDENTIAL_USE_BLOCKED","reason":"credential_not_active","use":None}
        if str(credential_record.get("expires_at","")) <= str(now_iso):
            return {"status":"CREDENTIAL_USE_BLOCKED","reason":"credential_expired","use":None}
        if credential_record.get("credential_ref") in (None,"","UNKNOWN","UNDETERMINED"):
            return {"status":"CREDENTIAL_USE_BLOCKED","reason":"credential_ref_undetermined","use":None}
        if audience != handle.audience or audience != handle.adapter_id:
            return {"status":"CREDENTIAL_USE_BLOCKED","reason":"wrong_audience","use":None}
        if requested_operation != handle.operation_id:
            return {"status":"CREDENTIAL_USE_BLOCKED","reason":"operation_outside_handle","use":None}
        if requested_target != handle.target_binding:
            return {"status":"CREDENTIAL_USE_BLOCKED","reason":"target_outside_handle","use":None}
        allowed_ops = credential_record.get("allowed_operations", [])
        if requested_operation not in allowed_ops:
            return {"status":"CREDENTIAL_USE_BLOCKED","reason":"credential_operation_not_allowed","use":None}
        allowed_targets = credential_record.get("allowed_targets", [])
        if requested_target not in allowed_targets:
            return {"status":"CREDENTIAL_USE_BLOCKED","reason":"credential_target_not_allowed","use":None}
        if credential_record.get("ambient_authority") is True:
            return {"status":"CREDENTIAL_USE_BLOCKED","reason":"ambient_authority_forbidden","use":None}
        if credential_record.get("transferable") is True:
            return {"status":"CREDENTIAL_USE_BLOCKED","reason":"transfer_forbidden","use":None}
        if credential_record.get("child_inheritance") is True:
            return {"status":"CREDENTIAL_USE_BLOCKED","reason":"child_inheritance_forbidden","use":None}

        payload = {
            "lease_id":handle.lease_id,
            "reservation_id":handle.reservation_id,
            "claim_hash":handle.claim_hash,
            "handle_id":handle.handle_id,
            "adapter_id":handle.adapter_id,
            "effector_id":handle.effector_id,
            "credential_ref":credential_record["credential_ref"],
            "allowed_operation":requested_operation,
            "target_binding":requested_target,
            "audience":audience,
            "expires_at":min(str(handle.expires_at), str(credential_record["expires_at"])),
        }
        broker_use_id = sha256(
            json.dumps(payload, sort_keys=True, separators=(",",":"), default=str).encode()
        ).hexdigest()
        with self._lock:
            if broker_use_id in self._issued:
                return {"status":"CREDENTIAL_USE_BLOCKED","reason":"duplicate_credential_use","use":self._issued[broker_use_id]}
            use = BrokeredCredentialUse(broker_use_id=broker_use_id, **payload)
            self._issued[broker_use_id] = use
            return {
                "status":"CREDENTIAL_USE_AUTHORIZED",
                "reason":None,
                "use":use,
                "raw_secret_disclosed":False,
                "effector_called":False,
                "real_world_effect_performed":False,
            }

    def consume_once(self, broker_use_id):
        with self._lock:
            if broker_use_id not in self._issued or broker_use_id in self._consumed:
                return False
            self._consumed.add(broker_use_id)
            return True

    @staticmethod
    def public_record(use):
        """Serialization safe for executor/audit surfaces; contains no secret value."""
        if use is None:
            return None
        return {
            "broker_use_id":use.broker_use_id,
            "lease_id":use.lease_id,
            "reservation_id":use.reservation_id,
            "claim_hash":use.claim_hash,
            "handle_id":use.handle_id,
            "adapter_id":use.adapter_id,
            "effector_id":use.effector_id,
            "credential_ref":use.credential_ref,
            "allowed_operation":use.allowed_operation,
            "target_binding":use.target_binding,
            "audience":use.audience,
            "expires_at":use.expires_at,
            "raw_secret_disclosed":False,
            "single_use":True,
            "transferable":False,
            "child_inheritance":False,
            "ambient_authority":False,
        }

class TrustedCredentialResolver:
    # TCB-only bridge from opaque credential_ref to vault secret material.
    def __init__(self, *, vault, credential_registry):
        self._vault=vault
        self._registry=dict(credential_registry or {})
        self._lock=RLock()
        self._resolved=set()

    def resolve_for_effector(self, *, brokered_use, adapter_id, effector_id,
                             operation, target, now_iso):
        if brokered_use is None:
            return {"status":"CREDENTIAL_RESOLUTION_BLOCKED","reason":"missing_brokered_use","secret":None}
        checks=[
            (brokered_use.raw_secret_disclosed is False,"invalid_brokered_use"),
            (brokered_use.adapter_id==adapter_id,"adapter_mismatch"),
            (brokered_use.effector_id==effector_id,"effector_mismatch"),
            (brokered_use.allowed_operation==operation,"operation_mismatch"),
            (brokered_use.target_binding==target,"target_mismatch"),
            (str(brokered_use.expires_at)>str(now_iso),"credential_use_expired"),
        ]
        for ok,reason in checks:
            if not ok:return {"status":"CREDENTIAL_RESOLUTION_BLOCKED","reason":reason,"secret":None}
        ref=brokered_use.credential_ref
        record=self._registry.get(ref)
        if not isinstance(record,dict):
            return {"status":"CREDENTIAL_RESOLUTION_BLOCKED","reason":"credential_ref_unknown","secret":None}
        if record.get("status")!="ACTIVE":
            return {"status":"CREDENTIAL_RESOLUTION_BLOCKED","reason":"credential_not_active","secret":None}
        if record.get("provider") in (None,"","UNKNOWN","UNDETERMINED"):
            return {"status":"CREDENTIAL_RESOLUTION_BLOCKED","reason":"provider_undetermined","secret":None}
        name=record.get("secret_name")
        if name in (None,"","UNKNOWN","UNDETERMINED"):
            return {"status":"CREDENTIAL_RESOLUTION_BLOCKED","reason":"secret_name_undetermined","secret":None}
        key=brokered_use.broker_use_id
        with self._lock:
            if key in self._resolved:
                return {"status":"CREDENTIAL_RESOLUTION_BLOCKED","reason":"credential_resolution_replay","secret":None}
            self._resolved.add(key)
        secret=self._vault.get_secret(str(name),provider=str(record["provider"]),
                                      requester="trusted_effector:"+str(effector_id))
        if not secret:
            return {"status":"CREDENTIAL_RESOLUTION_BLOCKED","reason":"secret_unavailable","secret":None}
        return {"status":"CREDENTIAL_RESOLVED_FOR_EFFECTOR","reason":None,"secret":secret,
                "credential_ref":ref,"provider":record["provider"],
                "raw_secret_disclosed_to_capability":False,
                "raw_secret_disclosed_to_executor":False,
                "resolution_scope":"TRUSTED_EFFECTOR_TCB_ONLY","single_use":True}

    @staticmethod
    def public_record(result):
        if not isinstance(result,dict):return None
        return {k:v for k,v in result.items() if k!="secret"}
