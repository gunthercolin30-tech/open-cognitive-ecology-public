from __future__ import annotations
from copy import deepcopy
from typing import Any, Mapping
import hashlib, json

PRIMITIVE = "p160_authority_requirements_resolution"
VERSION = "P160-F-v1"
SCHEMA = "oce.p160f.authority_requirements_resolution.v1"
FUNCTIONAL_ONLY = True
PHENOMENOLOGY_UNDETERMINED = True

AUTHORITY_CLASSES = (
    "OPERATIONAL","SUPERVISORY","GOVERNANCE","CONSTITUTIONAL","HUMAN_RESERVED",
    "CONSTITUENT","EMERGENCY","REVIEW","APPEAL","RECOVERY",
)
AUTHORITY_STATUSES = (
    "VALID","INVALID","EXPIRED","REVOKED","UNAVAILABLE","UNDETERMINED","CONFLICTING",
    "INSUFFICIENT_SCOPE","INSUFFICIENT_AUTHORITY_CLASS",
    "SEPARATION_OF_DUTIES_UNSATISFIED","QUORUM_UNSATISFIED","HUMAN_RESERVED_UNAVAILABLE",
)
HOLDER_STATUSES = ("ACTIVE","TEMPORARILY_UNAVAILABLE","SUSPENDED","REVOKED","EXPIRED","UNKNOWN")
REQUIREMENT_MODES = ("ALL_OF","ANY_OF","N_OF_M","SEQUENTIAL_APPROVAL")
ENVIRONMENTS = ("PRODUCTION","SHADOW","SIMULATION","TEST","RECOVERY")
CONFLICT_OUTCOMES = ("DISCLOSE","RECUSAL_REQUIRED","SECOND_REVIEW_REQUIRED","INVALID")

DOCTRINES = {
    "authority_authorization_separation": True,
    "authority_dimensionality": True,
    "human_absence_non_succession": True,
    "authority_non_aggregation": True,
    "separation_of_duties": True,
    "authority_freshness": True,
}
BOUNDARIES = {
    "authority_created": False,
    "authorization_created": False,
    "execution_performed": False,
    "p160g_opened": False,
    "p161_opened": False,
}

def canonical_json(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",",":"), ensure_ascii=False)
def canonical_sha256(v: Any) -> str:
    return hashlib.sha256(canonical_json(v).encode("utf-8")).hexdigest()
def _map(v): return dict(v) if isinstance(v, Mapping) else {}
def _list(v): return list(v) if isinstance(v, (list,tuple)) else []
def _present(v): return v is not None and v != "" and v != [] and v != {}
def _set(v): return set(_list(v))
def _fail(status, request_id, bindings, trace, **extra):
    x = {
        "schema":SCHEMA,"version":VERSION,"resolution_id":"",
        "request_id":request_id,"decision_context":deepcopy(bindings),
        "required_authority":{},"candidate_holders":[],"resolved_holder":None,
        "authority_provenance":[],"scope":{},"purpose":None,"temporal_bounds":{},
        "delegability":None,"separation_of_duties":{},"human_reserved":False,
        "quorum":{},"review_requirements":[],"appeal_requirements":[],
        "uncertainty":[status],"authority_status":status,"trace":list(trace),
        **BOUNDARIES,
    }
    x.update(extra); x["resolution_hash"]=canonical_sha256({k:v for k,v in x.items() if k!="resolution_hash"})
    x["resolution_id"]="p160f-"+x["resolution_hash"][:24]
    return x

def _bindings(request, runtime_context, constitutional_snapshot, compiled_profile, ccad_resolution):
    r,c,s,p,e = map(_map,(request,runtime_context,constitutional_snapshot,compiled_profile,ccad_resolution))
    return {
        "request_id":r.get("request_id"),
        "runtime_context_fingerprint":c.get("runtime_context_fingerprint") or c.get("decision_context_fingerprint"),
        "constitutional_snapshot_hash":r.get("constitutional_snapshot_hash") or s.get("constitutional_snapshot_hash") or s.get("snapshot_hash"),
        "compiled_profile_hash":r.get("compiled_profile_hash") or p.get("compiled_profile_hash") or p.get("profile_hash"),
        "ccad_resolution_hash":e.get("resolution_hash"),
    }

def _scope_subset(child, parent):
    c,p=_map(child),_map(parent)
    for axis in ("resource","subject","geography","purpose","time","action_class","risk"):
        cv,pv=c.get(axis),p.get(axis)
        if cv is None: continue
        if pv is None: return False
        cs = set(cv if isinstance(cv,(list,tuple,set)) else [cv])
        ps = set(pv if isinstance(pv,(list,tuple,set)) else [pv])
        if not cs.issubset(ps): return False
    return True

def _holder_valid(h, req, environment):
    status=h.get("status","UNKNOWN")
    if status!="ACTIVE": return False, status
    if h.get("environment","PRODUCTION") != environment: return False, "ENVIRONMENT_MISMATCH"
    if req.get("authority_class") not in _set(h.get("authority_classes")): return False, "INSUFFICIENT_AUTHORITY_CLASS"
    if not _scope_subset(req.get("scope",{}),h.get("scope",{})): return False, "INSUFFICIENT_SCOPE"
    if req.get("purpose") and req.get("purpose") not in _set(h.get("purposes")): return False, "INSUFFICIENT_SCOPE"
    if not _present(h.get("provenance")): return False, "UNDETERMINED"
    if h.get("revoked") is True: return False, "REVOKED"
    if h.get("expired") is True: return False, "EXPIRED"
    return True, "VALID"

def _resolve_authority_requirements_v1(
    request: Mapping[str,Any],
    runtime_context: Mapping[str,Any],
    constitutional_snapshot: Mapping[str,Any],
    compiled_profile: Mapping[str,Any],
    ccad_resolution: Mapping[str,Any],
    authority_context: Mapping[str,Any],
) -> dict:
    r,c,s,p,e,a = map(_map,(request,runtime_context,constitutional_snapshot,compiled_profile,ccad_resolution,authority_context))
    rid=r.get("request_id"); bindings=_bindings(r,c,s,p,e); trace=[]
    if not rid or any(not _present(bindings[k]) for k in ("runtime_context_fingerprint","constitutional_snapshot_hash","compiled_profile_hash")):
        return _fail("UNDETERMINED",rid,bindings,["BINDING_INCOMPLETE"])
    if e.get("authority_created") is True or e.get("authorization_created") is True:
        return _fail("INVALID",rid,bindings,["UPSTREAM_AUTHORITY_BOUNDARY_VIOLATION"])
    req=_map(a.get("authority_requirement"))
    cls=req.get("authority_class")
    if cls not in AUTHORITY_CLASSES:
        return _fail("UNDETERMINED",rid,bindings,["AUTHORITY_CLASS_UNDETERMINED"])
    mode=req.get("mode","ALL_OF")
    if mode not in REQUIREMENT_MODES:
        return _fail("UNDETERMINED",rid,bindings,["REQUIREMENT_MODE_UNSUPPORTED"])
    environment=a.get("environment","PRODUCTION")
    if environment not in ENVIRONMENTS:
        return _fail("UNDETERMINED",rid,bindings,["ENVIRONMENT_UNSUPPORTED"])
    human_reserved = cls in ("HUMAN_RESERVED","CONSTITUENT") or req.get("human_reserved") is True
    candidates=[]; rejected=[]
    for raw in _list(a.get("holders")):
        h=_map(raw); ok,why=_holder_valid(h,req,environment)
        (candidates if ok else rejected).append(deepcopy(h) if ok else {"holder_id":h.get("holder_id"),"reason":why})
    if human_reserved:
        candidates=[h for h in candidates if h.get("kind")=="HUMAN"]
        if not candidates:
            succession=_map(a.get("succession_rule"))
            if not (succession.get("preexisting") is True and succession.get("valid") is True):
                return _fail("HUMAN_RESERVED_UNAVAILABLE",rid,bindings,
                    ["HUMAN_ABSENCE_NON_SUCCESSION"],human_reserved=True,candidate_holders=[],
                    authority_succession_rule=deepcopy(succession),rejected_holders=rejected)
            sid=succession.get("successor_holder_id")
            candidates=[h for h in _list(a.get("holders")) if h.get("holder_id")==sid and h.get("kind")=="HUMAN" and _holder_valid(h,req,environment)[0]]
            if not candidates:
                return _fail("HUMAN_RESERVED_UNAVAILABLE",rid,bindings,["PREEXISTING_SUCCESSION_NOT_USABLE"],
                    human_reserved=True,authority_succession_rule=deepcopy(succession),rejected_holders=rejected)
    # Delegation is accepted only as a bounded derivative of an explicit parent.
    by_id={h.get("holder_id"):h for h in _list(a.get("holders")) if h.get("holder_id")}
    bounded=[]
    for h in candidates:
        parent_id=h.get("parent_authority_id")
        if parent_id:
            parent=by_id.get(parent_id)
            if not parent or not _scope_subset(h.get("scope",{}),parent.get("scope",{})):
                rejected.append({"holder_id":h.get("holder_id"),"reason":"DELEGATION_SCOPE_AMPLIFICATION"}); continue
            if not _set(h.get("authority_classes")).issubset(_set(parent.get("authority_classes"))):
                rejected.append({"holder_id":h.get("holder_id"),"reason":"DELEGATION_CLASS_AMPLIFICATION"}); continue
        bounded.append(h)
    candidates=bounded
    # Conflict of interest never disappears by aggregation.
    coi=_map(a.get("conflict_of_interest"))
    outcome=coi.get("outcome")
    if outcome=="INVALID":
        return _fail("INVALID",rid,bindings,["AUTHORITY_CONFLICT_INVALID"],authority_conflict_assessment=deepcopy(coi))
    if outcome=="RECUSAL_REQUIRED":
        recused=set(_list(coi.get("holder_ids"))); candidates=[h for h in candidates if h.get("holder_id") not in recused]
    sod=_map(a.get("separation_of_duties"))
    pairs=_list(sod.get("forbidden_role_pairs"))
    roles_by_holder={h.get("holder_id"):set(_list(h.get("roles"))) for h in candidates}
    for left,right in pairs:
        for hid,roles in roles_by_holder.items():
            if left in roles and right in roles:
                return _fail("SEPARATION_OF_DUTIES_UNSATISFIED",rid,bindings,["SOD_CONFLICT",hid],
                    candidate_holders=deepcopy(candidates),separation_of_duties=deepcopy(sod))
    q=_map(req.get("quorum")); n=q.get("n",1)
    if isinstance(n,bool) or not isinstance(n,int) or n<1: return _fail("QUORUM_UNSATISFIED",rid,bindings,["QUORUM_INVALID"])
    required_roles=set(_list(q.get("required_roles")))
    available_roles=set().union(*(set(_list(h.get("roles"))) for h in candidates)) if candidates else set()
    if len(candidates)<n or not required_roles.issubset(available_roles):
        return _fail("QUORUM_UNSATISFIED",rid,bindings,["QUORUM_OR_ROLE_UNSATISFIED"],
            candidate_holders=deepcopy(candidates),quorum=deepcopy(q),rejected_holders=rejected)
    # Multiple valid holders are preserved unless the constitutional requirement itself identifies one.
    resolved=None
    required_holder=req.get("required_holder_id")
    if required_holder:
        matches=[h for h in candidates if h.get("holder_id")==required_holder]
        if not matches: return _fail("UNAVAILABLE",rid,bindings,["REQUIRED_HOLDER_UNAVAILABLE"],candidate_holders=deepcopy(candidates))
        resolved=deepcopy(matches[0])
    elif len(candidates)==1 and n==1:
        resolved=deepcopy(candidates[0])
    provenance=[{"holder_id":h.get("holder_id"),"chain":deepcopy(h.get("provenance"))} for h in candidates]
    result={
        "schema":SCHEMA,"version":VERSION,"request_id":rid,"decision_context":bindings,
        "required_authority":deepcopy(req),"candidate_holders":deepcopy(candidates),
        "resolved_holder":resolved,"authority_provenance":provenance,
        "scope":deepcopy(req.get("scope",{})),"purpose":req.get("purpose"),
        "temporal_bounds":deepcopy(req.get("temporal_bounds",{})),
        "delegability":req.get("delegability",False),"separation_of_duties":deepcopy(sod),
        "human_reserved":human_reserved,"quorum":deepcopy(q),
        "review_requirements":deepcopy(req.get("review_requirements",[])),
        "appeal_requirements":deepcopy(req.get("appeal_requirements",[])),
        "authority_conflict_assessment":deepcopy(coi),
        "authority_escalation_path":deepcopy(a.get("escalation_path",{})),
        "authority_succession_rule":deepcopy(a.get("succession_rule",{})),
        "review_authority_requirement":deepcopy(a.get("review_authority_requirement",{})),
        "break_glass_authority":deepcopy(a.get("break_glass_authority",{})),
        "authority_context_fingerprint":a.get("authority_context_fingerprint"),
        "uncertainty":[],"authority_status":"VALID","trace":["AUTHORITY_REQUIREMENTS_RESOLVED"],
        "rejected_holders":rejected,**BOUNDARIES,
    }
    # Break-glass is descriptive only and cannot override DNA/constitutional bounds.
    bg=_map(result["break_glass_authority"])
    if bg:
        if not (bg.get("recovery_specific") is True and bg.get("temporary") is True and bg.get("audited") is True
                and bg.get("auto_expiring") is True and bg.get("dna_override") is False):
            return _fail("INVALID",rid,bindings,["BREAK_GLASS_INVALID"],break_glass_authority=deepcopy(bg))
    payload={k:v for k,v in result.items() if k not in ("resolution_id","resolution_hash")}
    result["resolution_hash"]=canonical_sha256(payload)
    result["resolution_id"]="p160f-"+result["resolution_hash"][:24]
    return result

def verify_authority_resolution(v: Mapping[str,Any]) -> dict:
    x=_map(v)
    checks={
        "known_status":x.get("authority_status") in AUTHORITY_STATUSES,
        "never_authorized":x.get("authority_status")!="AUTHORIZED",
        "no_authority_creation":x.get("authority_created") is False,
        "no_authorization":x.get("authorization_created") is False,
        "no_execution":x.get("execution_performed") is False,
        "no_p160g":x.get("p160g_opened") is False,
        "no_p161":x.get("p161_opened") is False,
    }
    return {"ok":all(checks.values()),"checks":checks}

def manifest() -> dict:
    return {
        "primitive":PRIMITIVE,"version":VERSION,"schema":SCHEMA,
        "authority_classes":AUTHORITY_CLASSES,"authority_statuses":AUTHORITY_STATUSES,
        "holder_statuses":HOLDER_STATUSES,"requirement_modes":REQUIREMENT_MODES,
        "environments":ENVIRONMENTS,"doctrines":DOCTRINES,"boundaries":BOUNDARIES,
        "reuses":["P095/R19 human authority semantics","P099 non-amplification semantics",
                  "P160-C authority derivation boundary","P160-E authority_requirements output"],
        "does_not_call":["P095.authorize","P098.resolve_conflict"],
    }

# --- P160-F v1.1 defensive refinement ---
_REQUIRED_PROVENANCE_V11=("role","mandate","governance","constitution","dna","genesis")

def _p160f_parse_utc(v):
    if not isinstance(v,str) or not v: return None
    try:
        from datetime import datetime, timezone
        s=v[:-1]+"+00:00" if v.endswith("Z") else v
        d=datetime.fromisoformat(s)
        if d.tzinfo is None: d=d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)
    except Exception:
        return None

def _p160f_now(c):
    from datetime import datetime, timezone
    raw=c.get("evaluated_at") or c.get("current_time") or c.get("timestamp")
    return _p160f_parse_utc(raw) or datetime.now(timezone.utc)

def _p160f_provenance_complete(v):
    seq=[str(x).strip().lower().replace("_"," ") for x in _list(v)]
    seq=["governance" if x in ("governance grant","governance") else x for x in seq]
    pos=-1
    for required in _REQUIRED_PROVENANCE_V11:
        try: pos=seq.index(required,pos+1)
        except ValueError: return False
    return True

def resolve_authority_requirements(request, runtime_context, constitutional_snapshot,
                                   compiled_profile, ccad_resolution, authority_context):
    r,c,s,p,e,a=map(_map,(request,runtime_context,constitutional_snapshot,compiled_profile,ccad_resolution,authority_context))
    rid=r.get("request_id"); bindings=_bindings(r,c,s,p,e)

    if not _present(e.get("resolution_hash")):
        return _fail("UNDETERMINED",rid,bindings,["CCAD_RESOLUTION_HASH_MISSING"])
    if not _present(a.get("authority_context_fingerprint")):
        return _fail("UNDETERMINED",rid,bindings,["AUTHORITY_CONTEXT_FINGERPRINT_MISSING"])

    supplied_snapshot=s.get("constitutional_snapshot_hash") or s.get("snapshot_hash")
    supplied_profile=p.get("compiled_profile_hash") or p.get("profile_hash")
    if r.get("constitutional_snapshot_hash") and supplied_snapshot and r.get("constitutional_snapshot_hash")!=supplied_snapshot:
        return _fail("INVALID",rid,bindings,["CONSTITUTIONAL_SNAPSHOT_MISMATCH"])
    if r.get("compiled_profile_hash") and supplied_profile and r.get("compiled_profile_hash")!=supplied_profile:
        return _fail("INVALID",rid,bindings,["COMPILED_PROFILE_MISMATCH"])

    req=_map(a.get("authority_requirement"))
    temporal=_map(req.get("temporal_bounds"))
    now=_p160f_now(c)
    vf=_p160f_parse_utc(temporal.get("valid_from"))
    ex=_p160f_parse_utc(temporal.get("expires_at"))
    if temporal.get("valid_from") and vf is None:
        return _fail("UNDETERMINED",rid,bindings,["TEMPORAL_BOUND_INVALID"])
    if temporal.get("expires_at") and ex is None:
        return _fail("UNDETERMINED",rid,bindings,["TEMPORAL_BOUND_INVALID"])
    if vf is not None and now<vf:
        return _fail("UNAVAILABLE",rid,bindings,["AUTHORITY_NOT_YET_VALID"])
    if ex is not None and now>=ex:
        return _fail("EXPIRED",rid,bindings,["AUTHORITY_REQUIREMENT_EXPIRED"])

    holders=[_map(h) for h in _list(a.get("holders"))]
    ids=[h.get("holder_id") for h in holders if h.get("holder_id")]
    if len(ids)!=len(set(ids)):
        return _fail("QUORUM_UNSATISFIED",rid,bindings,["DUPLICATE_HOLDER_IDENTITY"])

    for h in holders:
        if h.get("status","UNKNOWN")=="ACTIVE" and not _p160f_provenance_complete(h.get("provenance")):
            return _fail("UNDETERMINED",rid,bindings,["AUTHORITY_PROVENANCE_INCOMPLETE"])

    mode=req.get("mode","ALL_OF")
    roles_by_holder={h.get("holder_id"):set(_list(h.get("roles"))) for h in holders}

    if mode=="SEQUENTIAL_APPROVAL":
        seq=_list(req.get("sequence"))
        if not seq:
            return _fail("UNDETERMINED",rid,bindings,["SEQUENTIAL_APPROVAL_SEQUENCE_MISSING"])
        chosen=[]
        for role in seq:
            eligible=[hid for hid,roles in roles_by_holder.items() if role in roles]
            if not eligible:
                return _fail("QUORUM_UNSATISFIED",rid,bindings,["SEQUENTIAL_APPROVAL_ROLE_MISSING",role])
            chosen.append(eligible[0])
        if len(set(chosen))!=len(chosen):
            return _fail("SEPARATION_OF_DUTIES_UNSATISFIED",rid,bindings,["SEQUENTIAL_APPROVAL_NOT_INDEPENDENT"])
    elif mode=="ANY_OF":
        alts=_list(req.get("alternatives"))
        if alts:
            ok=False
            for alt0 in alts:
                alt=_map(alt0)
                for h in holders:
                    if (not alt.get("role") or alt.get("role") in set(_list(h.get("roles")))) and (not alt.get("holder_id") or alt.get("holder_id")==h.get("holder_id")):
                        ok=True
            if not ok:
                return _fail("QUORUM_UNSATISFIED",rid,bindings,["ANY_OF_UNSATISFIED"])
    elif mode=="ALL_OF":
        needed=set(_list(req.get("all_of_roles")))
        have=set().union(*(set(_list(h.get("roles"))) for h in holders)) if holders else set()
        if needed and not needed.issubset(have):
            return _fail("QUORUM_UNSATISFIED",rid,bindings,["ALL_OF_UNSATISFIED"])
    elif mode=="N_OF_M":
        q=_map(req.get("quorum"))
        n=req.get("n",q.get("n"))
        m=req.get("m",q.get("m"))
        if isinstance(n,bool) or not isinstance(n,int) or isinstance(m,bool) or not isinstance(m,int) or n<1 or m<n:
            return _fail("QUORUM_UNSATISFIED",rid,bindings,["N_OF_M_INVALID"])
        if len(set(ids))<n:
            return _fail("QUORUM_UNSATISFIED",rid,bindings,["N_OF_M_UNSATISFIED"])

    used=set()
    for label,key in (("REVIEW","review_requirements"),("APPEAL","appeal_requirements")):
        for rr0 in _list(req.get(key)):
            rr=_map(rr0); role=rr.get("role")
            eligible=[h for h in holders if (not role or role in set(_list(h.get("roles")))) and (rr.get("independent") is not True or h.get("holder_id") not in used)]
            if not eligible:
                return _fail("UNAVAILABLE",rid,bindings,[label+"_AUTHORITY_UNAVAILABLE"])
            if rr.get("independent") is True:
                used.add(eligible[0].get("holder_id"))

    esc=_map(a.get("escalation_path"))
    if esc:
        if esc.get("preexisting") is not True:
            return _fail("INVALID",rid,bindings,["ESCALATION_PATH_NOT_PREEXISTING"])
        if esc.get("from_class") and esc.get("to_class") and esc.get("from_class")!=esc.get("to_class"):
            return _fail("INSUFFICIENT_AUTHORITY_CLASS",rid,bindings,["ESCALATION_AUTHORITY_EXPANSION_FORBIDDEN"])

    return _resolve_authority_requirements_v1(request,runtime_context,constitutional_snapshot,compiled_profile,ccad_resolution,authority_context)
