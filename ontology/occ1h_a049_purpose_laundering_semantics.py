SCHEMA="oce.p159.occ1h.a049.purpose_laundering_semantics.v1"
RELATION="PURPOSE_LAUNDERING"
FUNCTIONAL_ONLY=True
RUNTIME_AUTHORITY_GRANTED=False
def classify(actions, aggregate_purpose):
    if not isinstance(actions,list) or not actions:
        return {"status":"UNRESOLVED","reason":"ACTIONS_NOT_MATERIALIZED"}
    if not isinstance(aggregate_purpose,str) or not aggregate_purpose:
        return {"status":"UNRESOLVED","reason":"AGGREGATE_PURPOSE_NOT_MATERIALIZED"}
    governed=set()
    for a in actions:
        if not isinstance(a,dict):
            return {"status":"UNRESOLVED","reason":"ACTION_NOT_STRUCTURED"}
        p=a.get("governed_purpose"); prov=a.get("provenance")
        if not isinstance(p,str) or not p:
            return {"status":"UNRESOLVED","reason":"PURPOSE_BOUND_NOT_MATERIALIZED"}
        if not isinstance(prov,str) or not prov:
            return {"status":"UNRESOLVED","reason":"PROVENANCE_NOT_MATERIALIZED"}
        if a.get("individually_admissible") is not True:
            return {"status":"OUTSIDE_A049_PRECONDITION","reason":"CONSTITUENT_NOT_INDIVIDUALLY_ADMISSIBLE"}
        governed.add(p)
    if aggregate_purpose not in governed:
        return {"status":"RESISTED","relation":RELATION,"reason":"AGGREGATE_PURPOSE_OUTSIDE_GOVERNED_CONSTITUENT_PURPOSE_BOUNDS"}
    return {"status":"ADMISSIBLE_CONTROL","reason":"AGGREGATE_PURPOSE_WITHIN_GOVERNED_BOUND"}
