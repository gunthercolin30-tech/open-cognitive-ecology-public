from __future__ import annotations
import hashlib, json
from copy import deepcopy
from typing import Any, Mapping
from ontology.p161_authorization_token_binding import verify_token_integrity
from ontology.p161_authorization_token_lifecycle import refresh, TERMINAL, validate_lifecycle_temporal_context

PRIMITIVE="token_point_of_use_verifier"
VERSION="P162-C-v1"
UNKNOWN={None,"","UNKNOWN","UNRESOLVED","INCONCLUSIVE"}

def canonical_json(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
def sha(x): return hashlib.sha256(canonical_json(x).encode()).hexdigest()
def _m(x): return x if isinstance(x,Mapping) else {}
def _known(x):
    try: return x not in UNKNOWN
    except TypeError: return x is not None

def manifest():
    return {"primitive":PRIMITIVE,"version":VERSION,
      "laws":["VALID_TOKEN_AT_ISSUANCE!=VALID_TOKEN_AT_USE","TOKEN_CURRENT!=EXECUTION_ALLOWED",
      "TOKEN_AUTHENTICITY!=TOKEN_CURRENTNESS","TOKEN_CURRENTNESS!=RUNTIME_PRECONDITION_SATISFACTION",
      "TOKEN_USABLE_FOR_GATE!=EXECUTABLE","SIGNATURE!=AUTHORIZATION","COMMIT_BEFORE_USE",
      "TERMINAL_STATE_FINAL","UNKNOWN!=PERMISSION","VERIFICATION!=CONSUMPTION",
      "POINT_OF_USE_VERIFICATION!=EXECUTION"],
      "authorization_created":False,"reservation_created":False,"token_consumed":False,
      "capability_accessed":False,"execution_performed":False,"p162d_opened":False,
      "functional_only":True,"phenomenology_undetermined":True}

def _subset_budget(requested, available):
    if not isinstance(requested,Mapping) or not isinstance(available,Mapping): return False
    for k,v in requested.items():
        if k not in available: return False
        try:
            if float(v)>float(available[k]): return False
        except Exception:
            if v!=available[k]: return False
    return True

def verify_at_point_of_use(*, token, signing_key, issuance_event, lifecycle,
    registry_snapshot, revocation_snapshot, invocation_request, invocation_binding_manifest,
    capability_binding_receipt, current_dependency_vector, authority_snapshot,
    approval_consent_quorum_snapshot, human_integrity_snapshot, profile_snapshot,
    target_state_snapshot, pending_composition_snapshot, budget_snapshot, now, revalidate_after,
    clock_uncertain=False, clock_rollback=False):
    t=deepcopy(dict(_m(token))); body=dict(_m(t.get("body"))); inv=deepcopy(dict(_m(invocation_request)))
    bind=deepcopy(dict(_m(invocation_binding_manifest))); failures=[]; checks={}

    integ=verify_token_integrity(t,signing_key)
    checks["token_integrity"]=integ
    if integ.get("status")!="PASS": failures.append("TOKEN_INTEGRITY_INVALID")

    if _m(t.get("signature")).get("algorithm")!="HMAC-SHA256": failures.append("ALGORITHM_NOT_ALLOWED")
    tid=body.get("token_id"); th=t.get("token_hash")
    ev=dict(_m(issuance_event))
    if ev.get("status")!="COMMITTED" or ev.get("token_id")!=tid or ev.get("token_hash")!=th:
        failures.append("COMMITTED_ISSUANCE_NOT_PROVEN")
    token_issuer=body.get("signer_id")
    if not _known(token_issuer) or ev.get("issuer_id")!=token_issuer:
        failures.append("ISSUANCE_ISSUER_MISMATCH")

    temporal=validate_lifecycle_temporal_context(clock_uncertain=clock_uncertain,clock_rollback=clock_rollback)
    checks["temporal_context"]=temporal
    if temporal.get("status")!="SATISFIED": failures.append("TEMPORAL_CONTEXT_UNCERTAIN")

    lc_before=deepcopy(dict(_m(lifecycle)))
    lc=refresh(lc_before,t,now=now) if not failures or "TOKEN_INTEGRITY_INVALID" not in failures else lc_before
    checks["lifecycle_state"]=lc.get("state")
    if lc.get("token_id")!=tid or lc.get("token_hash")!=th: failures.append("LIFECYCLE_TOKEN_MISMATCH")
    if lc.get("state")!="CURRENT": failures.append("TOKEN_NOT_CURRENT")
    if lc.get("state") in TERMINAL: failures.append("TOKEN_TERMINAL")
    if lc.get("reservation") is not None: failures.append("TOKEN_ALREADY_RESERVED")
    if lc.get("max_uses") is not None and int(lc.get("consumed_uses",0))>=int(lc.get("max_uses")):
        failures.append("TOKEN_USE_LIMIT_REACHED")

    reg=dict(_m(registry_snapshot))
    if not _known(reg.get("version")) or reg.get("continuity_status")!="SATISFIED":
        failures.append("REGISTRY_CONTINUITY_UNCERTAIN")
    rs=dict(_m(revocation_snapshot))
    if not _known(rs.get("version")) or rs.get("status")!="SATISFIED" or rs.get("stale") is True:
        failures.append("REVOCATION_CURRENTNESS_UNCERTAIN")
    if rs.get("token_revoked") is True: failures.append("TOKEN_REVOKED")
    if rs.get("dependency_revoked") is True: failures.append("AUTHORIZATION_DEPENDENCY_REVOKED")

    expected=dict(_m(body.get("dependency_vector"))); current=dict(_m(current_dependency_vector))
    if not expected or expected!=current: failures.append("AUTHORIZATION_DEPENDENCY_DRIFT")

    au=dict(_m(authority_snapshot)); acq=dict(_m(approval_consent_quorum_snapshot))
    if au.get("status")!="VALID": failures.append("AUTHORITY_NOT_CURRENT")
    if acq.get("status")!="SATISFIED": failures.append("APPROVAL_CONSENT_QUORUM_NOT_CURRENT")

    hi=dict(_m(human_integrity_snapshot))
    if hi.get("required") is True:
        if hi.get("status")!="SATISFIED" or not _known(hi.get("snapshot_hash")): failures.append("HUMAN_INTEGRITY_NOT_CURRENT")
    elif hi.get("required") is not False: failures.append("HUMAN_INTEGRITY_REQUIREMENT_UNKNOWN")
    ps=dict(_m(profile_snapshot))
    if ps.get("status")!="SATISFIED" or not _known(ps.get("profile_hash")): failures.append("PROFILE_NOT_CURRENT")
    ts=dict(_m(target_state_snapshot))
    if ts.get("status")!="SATISFIED" or not _known(ts.get("snapshot_hash")): failures.append("TARGET_STATE_NOT_CURRENT")
    elif ts.get("target_binding")!=inv.get("target_binding"): failures.append("TARGET_STATE_BINDING_MISMATCH")
    pc=dict(_m(pending_composition_snapshot))
    if pc.get("status")!="SATISFIED" or not _known(pc.get("snapshot_hash")): failures.append("PENDING_COMPOSITION_STATE_UNCERTAIN")
    elif pc.get("has_conflicting_pending_composition") is True: failures.append("PENDING_COMPOSITION_CONFLICT")

    if inv.get("authorization_token_id")!=tid or inv.get("authorization_token_hash")!=th:
        failures.append("INVOCATION_TOKEN_BINDING_MISMATCH")
    if inv.get("action_digest")!=body.get("action_digest"): failures.append("ACTION_BINDING_MISMATCH")
    if body.get("capabilities") and inv.get("capability_id") not in body.get("capabilities",[]):
        failures.append("CAPABILITY_BINDING_MISMATCH")
    if body.get("target") is not None and inv.get("target_binding")!=body.get("target"):
        failures.append("TARGET_BINDING_MISMATCH")
    if body.get("purpose") is not None and inv.get("purpose_id")!=body.get("purpose"):
        failures.append("PURPOSE_BINDING_MISMATCH")
    if bind.get("token",{}).get("token_id")!=tid or bind.get("token",{}).get("token_hash")!=th:
        failures.append("INVOCATION_MANIFEST_TOKEN_MISMATCH")
    if bind.get("executor",{}).get("executor_id")!=inv.get("executor_id") or bind.get("executor",{}).get("executor_instance_id")!=inv.get("executor_instance_id"):
        failures.append("EXECUTOR_BINDING_MISMATCH")
    if bind.get("capability",{}).get("capability_id")!=inv.get("capability_id") or bind.get("operation",{}).get("operation_id")!=inv.get("operation_id"):
        failures.append("CAPABILITY_OPERATION_BINDING_MISMATCH")
    if bind.get("environment",{}).get("environment")!=inv.get("environment"):
        failures.append("ENVIRONMENT_BINDING_MISMATCH")
    if bind.get("arguments",{}).get("digest")!=inv.get("arguments_digest"):
        failures.append("ARGUMENT_BINDING_MISMATCH")

    cb=dict(_m(capability_binding_receipt))
    if cb.get("verification_status")!="BOUND_VERIFIED": failures.append("CAPABILITY_BINDING_NOT_CURRENT")
    if cb.get("capability_id")!=inv.get("capability_id"): failures.append("CAPABILITY_RECEIPT_ID_MISMATCH")
    if cb.get("capability_version")!=inv.get("capability_version"): failures.append("CAPABILITY_RECEIPT_VERSION_MISMATCH")
    if cb.get("implementation_identity")!=inv.get("capability_implementation_id"): failures.append("CAPABILITY_RECEIPT_IMPLEMENTATION_MISMATCH")
    if cb.get("invocation_request_id")!=inv.get("invocation_request_id"): failures.append("CAPABILITY_RECEIPT_INVOCATION_MISMATCH")

    bs=dict(_m(budget_snapshot))
    if bs.get("status")!="SATISFIED" or not _known(bs.get("snapshot_hash")):
        failures.append("BUDGET_CURRENTNESS_UNCERTAIN")
    elif not _subset_budget(inv.get("budget",{}),bs.get("available_budget",{})):
        failures.append("BUDGET_EXCEEDED")

    if not _known(revalidate_after) or not _known(now) or revalidate_after<=now:
        failures.append("REVALIDATE_AFTER_INVALID")

    critical=[reg.get("version"),rs.get("version"),cb.get("binding_receipt_hash"),bs.get("snapshot_hash"),
              inv.get("invocation_request_hash"),inv.get("arguments_digest")]
    if any(not _known(x) for x in critical): failures.append("CRITICAL_BINDING_UNKNOWN")

    status="TOKEN_USABLE_FOR_GATE" if not failures else "TOKEN_NOT_USABLE_FOR_GATE"
    verification={"schema":"oce.p162c.point_of_use_token_verification.v1","version":VERSION,
      "status":status,"token_id":tid,"token_hash":th,"invocation_request_id":inv.get("invocation_request_id"),
      "checks":checks,"failures":sorted(set(failures)),
      "authorization_created":False,"reservation_created":False,"token_consumed":False,
      "capability_accessed":False,"execution_performed":False,"p162d_opened":False,
      "functional_only":True,"phenomenology_undetermined":True}
    verification["verification_hash"]=sha(verification)
    receipt={"schema":"oce.p162c.point_of_use_token_verification_receipt.v1","version":VERSION,
      "status":status,"verification_hash":verification["verification_hash"],"token_id":tid,"token_hash":th,
      "invocation_request_id":inv.get("invocation_request_id"),
      "token_state_version":sha({"lifecycle_hash":lc.get("lifecycle_hash"),"last_event_seq":lc.get("last_event_seq"),"state":lc.get("state")}),
      "registry_version":reg.get("version"),"revocation_snapshot_version":rs.get("version"),
      "dependency_snapshot_hash":sha(current),"capability_binding_receipt_hash":cb.get("binding_receipt_hash"),
      "human_integrity_snapshot_hash":hi.get("snapshot_hash"),"profile_snapshot_hash":ps.get("profile_hash"),"target_state_snapshot_hash":ts.get("snapshot_hash"),"pending_composition_snapshot_hash":pc.get("snapshot_hash"),
      "budget_snapshot_hash":bs.get("snapshot_hash"),"binding_results":{"token":tid==inv.get("authorization_token_id"),
      "action":inv.get("action_digest")==body.get("action_digest"),"capability":inv.get("capability_id") in body.get("capabilities",[]),
      "target":inv.get("target_binding")==body.get("target"),"purpose":inv.get("purpose_id")==body.get("purpose"),
      "executor":bind.get("executor",{}).get("executor_id")==inv.get("executor_id"),
      "environment":bind.get("environment",{}).get("environment")==inv.get("environment"),
      "arguments":bind.get("arguments",{}).get("digest")==inv.get("arguments_digest")},
      "revalidate_after":revalidate_after,
      "authorization_created":False,"reservation_created":False,"token_consumed":False,
      "capability_accessed":False,"execution_performed":False,"p162d_opened":False,
      "functional_only":True,"phenomenology_undetermined":True}
    receipt["receipt_hash"]=sha(receipt)
    return {"status":status,"verification":verification,"receipt":receipt,
      "lifecycle_observed":lc,"lifecycle_input_unchanged":lc_before==dict(_m(lifecycle)),**manifest()}
