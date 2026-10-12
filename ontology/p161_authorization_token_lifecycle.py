from __future__ import annotations
import hashlib,json
from copy import deepcopy
from typing import Any,Mapping

PRIMITIVE="p161_authorization_token_lifecycle";VERSION="P161-H-v1"
TERMINAL={"CONSUMED","REVOKED","EXPIRED","INVALIDATED"}
def _canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _hash(x):return hashlib.sha256(_canon(x).encode()).hexdigest()
def _m(x):return x if isinstance(x,Mapping) else {}

def manifest():
 return {"primitive":PRIMITIVE,"version":VERSION,
 "laws":["TOKEN_CURRENT!=EXECUTION_ALLOWED","TERMINAL_STATE_NEVER_CURRENT",
 "REVOCATION_PRECEDES_USE","EXPIRY_PRECEDES_USE","SINGLE_USE_AT_MOST_ONCE",
 "LIFECYCLE!=CAPABILITY","LIFECYCLE!=EXECUTION"],
 "capability_created":False,"execution_performed":False,"p162_opened":False,
 "functional_only":True,"phenomenology_undetermined":True}

def initialize_lifecycle(token:Mapping[str,Any],*,max_uses:int|None=None):
 t=dict(_m(token));b=_m(t.get("body"));policy=b.get("use_policy")
 if policy not in {"SINGLE_USE","BOUNDED_MULTI_USE","REVALIDATE_EACH_USE"}:
  return {"status":"INVALIDATED","reason":"UNKNOWN_USE_POLICY","terminal":True}
 if policy=="SINGLE_USE":limit=1
 elif policy=="BOUNDED_MULTI_USE":
  if not isinstance(max_uses,int) or max_uses<1:return {"state":"INVALIDATED","reason":"INVALID_USE_LIMIT","terminal":True}
  limit=max_uses
 else:limit=None
 x={"schema":"oce.p161h.token_lifecycle.v1","token_id":b.get("token_id"),"token_hash":t.get("token_hash"),
 "state":"NOT_YET_VALID","use_policy":policy,"max_uses":limit,"consumed_uses":0,"reservation":None,
 "revoked_at":None,"revocation_reason":None,"last_event_seq":0,
 "capability_created":False,"execution_performed":False,"p162_opened":False}
 x["lifecycle_hash"]=_hash(x);return x

def _rehash(x):
 y=dict(x);y.pop("lifecycle_hash",None);y["lifecycle_hash"]=_hash(y);return y

def refresh(lifecycle:Mapping[str,Any],token:Mapping[str,Any],*,now:str):
 x=dict(_m(lifecycle));b=_m(_m(token).get("body"));v=_m(b.get("validity"))
 if x.get("state") in TERMINAL:return _rehash(x)
 nb,na=v.get("not_before"),v.get("not_after")
 if not nb or not na:return transition_terminal(x,"INVALIDATED",now,"MISSING_VALIDITY")
 if now<nb:x["state"]="NOT_YET_VALID"
 elif now>=na:x=transition_terminal(x,"EXPIRED",now,"VALIDITY_ENDED")
 elif x.get("state")=="NOT_YET_VALID":x["state"]="CURRENT"
 return _rehash(x)

def transition_terminal(lifecycle,state,at,reason):
 x=dict(_m(lifecycle))
 if x.get("state") in TERMINAL:return _rehash(x)
 if state not in TERMINAL:raise ValueError("terminal state required")
 x.update(state=state,reservation=None,last_event_seq=int(x.get("last_event_seq",0))+1)
 if state=="REVOKED":x.update(revoked_at=at,revocation_reason=reason)
 else:x["terminal_reason"]=reason
 return _rehash(x)

def revoke(lifecycle,*,now:str,reason:str):
 return transition_terminal(lifecycle,"REVOKED",now,reason or "REVOKED")

def reserve_for_use(lifecycle:Mapping[str,Any],token:Mapping[str,Any],*,now:str,reservation_id:str,
 current_token_hash:str,revalidation_passed:bool=False):
 x=refresh(lifecycle,token,now=now)
 if x.get("state")!="CURRENT":return {"status":"REFUSED","reason":"TOKEN_NOT_CURRENT","lifecycle":x}
 if x.get("token_hash")!=current_token_hash:return {"status":"REFUSED","reason":"TOKEN_HASH_DRIFT","lifecycle":x}
 if x.get("reservation") is not None:return {"status":"REFUSED","reason":"ALREADY_RESERVED","lifecycle":x}
 if x.get("use_policy")=="REVALIDATE_EACH_USE" and not revalidation_passed:
  return {"status":"REFUSED","reason":"REVALIDATION_REQUIRED","lifecycle":x}
 if x.get("max_uses") is not None and int(x.get("consumed_uses",0))>=int(x["max_uses"]):
  x=transition_terminal(x,"CONSUMED",now,"USE_LIMIT_REACHED")
  return {"status":"REFUSED","reason":"USE_LIMIT_REACHED","lifecycle":x}
 x["state"]="RESERVED_FOR_USE";x["reservation"]={"reservation_id":reservation_id,"reserved_at":now}
 x["last_event_seq"]=int(x.get("last_event_seq",0))+1;x=_rehash(x)
 return {"status":"RESERVED","lifecycle":x,"execution_performed":False,"p162_opened":False}

def consume_reserved(lifecycle:Mapping[str,Any],*,now:str,reservation_id:str):
 x=dict(_m(lifecycle));r=_m(x.get("reservation"))
 if x.get("state")!="RESERVED_FOR_USE" or r.get("reservation_id")!=reservation_id:
  return {"status":"REFUSED","reason":"NO_MATCHING_RESERVATION","lifecycle":_rehash(x)}
 x["consumed_uses"]=int(x.get("consumed_uses",0))+1;x["reservation"]=None
 limit=x.get("max_uses")
 if x.get("use_policy")=="SINGLE_USE" or (limit is not None and x["consumed_uses"]>=limit):
  x["state"]="CONSUMED";x["terminal_reason"]="USE_LIMIT_REACHED"
 else:x["state"]="CURRENT"
 x["last_event_seq"]=int(x.get("last_event_seq",0))+1;x=_rehash(x)
 return {"status":"CONSUMED_USE","lifecycle":x,"execution_performed":False,"p162_opened":False}

# P161_CANONICAL_COMPLETION_AFGH_V1
CONSUMPTION_INDETERMINATE="CONSUMPTION_INDETERMINATE"
FAILED_AFTER_EFFECT="FAILED_AFTER_EFFECT"
def token_tombstone(token_id,token_hash,terminal_state,reason,at):
    return {"type":"TokenTombstone","token_id":token_id,"token_hash":token_hash,"terminal_state":terminal_state,"reason":reason,"at":at,"resurrectable":False}
def validate_lifecycle_temporal_context(*,clock_uncertain=False,clock_rollback=False):
    return {"status":"UNKNOWN","reason":"TEMPORAL_CONTEXT_UNCERTAIN"} if (clock_uncertain or clock_rollback) else {"status":"SATISFIED"}
def propagate_dependency_revocation(lifecycle,*,dependency_revoked,reason="DEPENDENCY_REVOKED"):
    x=dict(lifecycle)
    if dependency_revoked:
        x["state"]="REVOKED";x["terminal_reason"]=reason
    return x
