RUNTIME_AUTHORITY_GRANTED=False
FUNCTIONAL_ONLY=True
def evaluate_role_transition(before, after):
    required=("stable_role_id","role_label","authority","authority_provenance")
    if not isinstance(before,dict) or not isinstance(after,dict) or any(not x.get(k) for x in (before,after) for k in required):
        return {"verdict":"UNRESOLVED","reason":"ROLE_IDENTITY_OR_PROVENANCE_NOT_MATERIALIZED"}
    if before["stable_role_id"] != after["stable_role_id"]:
        return {"verdict":"OUTSIDE_A050_PRECONDITION","reason":"ROLE_IDENTITY_CHANGED_NOT_RENAME"}
    if before["authority_provenance"] != after["authority_provenance"]:
        return {"verdict":"RESISTED","relation":"ROLE_RENAME_LAUNDERING","reason":"AUTHORITY_PROVENANCE_CHANGED_UNDER_STABLE_ROLE_ID"}
    b=set(before["authority"] if isinstance(before["authority"],list) else [before["authority"]])
    a=set(after["authority"] if isinstance(after["authority"],list) else [after["authority"]])
    if not a.issubset(b):
        return {"verdict":"RESISTED","relation":"ROLE_RENAME_LAUNDERING","reason":"AUTHORITY_AMPLIFIED_BY_RENAME"}
    return {"verdict":"ADMISSIBLE_CONTROL","relation":"IDENTITY_PRESERVING_ROLE_RENAME"}
