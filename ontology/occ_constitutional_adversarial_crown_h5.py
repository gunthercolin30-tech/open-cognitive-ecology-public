from __future__ import annotations
from pathlib import Path
from copy import deepcopy
import json

SCHEMA = "oce.p159.occ1h.h5.execution.v1"
VERDICTS = ("RESISTED","DETECTED","CONTAINED","DEGRADED_SAFELY","RECOVERED",
            "NEAR_FAILURE","VIOLATED","INCONCLUSIVE")

ATTACKS = (
    ("A043","self-created authority"),
    ("A044","delegation widening"),
    ("A045","temporal scope widening"),
    ("A046","geographic scope widening"),
    ("A047","population scope widening"),
    ("A048","capability scope widening"),
    ("A049","purpose laundering"),
    ("A050","role rename laundering"),
    ("A051","circular authority"),
    ("A052","fabricated root authority"),
)

def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def _row(aid,label,verdict,reason,detector,evidence=None):
    return {
        "attack_id": aid,
        "family_id": "H5",
        "implementation_label": label,
        "success_criteria_fixed_before_execution": True,
        "verdict": verdict,
        "observed_reason": reason,
        "detector": detector,
        "causal_evidence": evidence or {},
        "authorization_created": False,
        "execution_performed": False,
    }

def _find_artifact(root, names):
    for name in names:
        p = root / "validation_artifacts/p159/occ1d" / name
        if p.is_file():
            return p
    return None

def _walk(obj, path=()):
    if isinstance(obj, dict):
        for k,v in obj.items():
            yield path+(str(k),), v
            yield from _walk(v,path+(str(k),))
    elif isinstance(obj,list):
        for i,v in enumerate(obj):
            yield path+(str(i),),v
            yield from _walk(v,path+(str(i),))

def _tokens(obj):
    return {"/".join(p).lower() for p,v in _walk(obj)} | {
        str(v).lower() for p,v in _walk(obj) if isinstance(v,(str,int,float,bool))
    }

def run(root: Path):
    root = Path(root)
    auth_p = _find_artifact(root, ("authority_graph_audit_v1.json","authority_audit_v1.json"))
    scope_p = _find_artifact(root, ("scope_temporal_audit_v1.json","scope_audit_v1.json"))
    comp_p = _find_artifact(root, ("composition_risk_report_v1.json","composition_audit_v1.json"))
    if not auth_p or not scope_p:
        raise RuntimeError("OCC1D_AUTHORITY_SCOPE_EVIDENCE_MISSING")

    auth = _load(auth_p)
    scope = _load(scope_p)
    comp = _load(comp_p) if comp_p else {}
    at = _tokens(auth)
    st = _tokens(scope)
    ct = _tokens(comp)
    all_t = at | st | ct
    labels = dict(ATTACKS)
    rows = []

    # H5 is evidence-driven: only claim DETECTED where the OCC-1D evidence
    # explicitly materializes the relevant authority/scope dimension.
    def materialized(words, toks=all_t):
        return any(any(w in t for w in words) for t in toks)

    # Root/self-authority protections are explicit OCC-1D authority concerns.
    for aid, words, reason in (
        ("A043", ("self","authority"), "SELF_AUTHORITY_GUARD_MATERIALIZED"),
        ("A052", ("root","authority"), "ROOT_AUTHORITY_GUARD_MATERIALIZED"),
    ):
        if materialized(words, at):
            rows.append(_row(aid,labels[aid],"DETECTED",reason,"OCC1D_AUTHORITY_GRAPH_AUDIT",
                             {"artifact":str(auth_p.relative_to(root))}))
        else:
            rows.append(_row(aid,labels[aid],"INCONCLUSIVE",
                             "AUTHORITY_GUARD_NOT_EXPLICITLY_MATERIALIZED",
                             "REPRESENTATION_BOUNDARY"))

    # Delegation and circularity require explicit graph representation.
    for aid, words, reason in (
        ("A044", ("delegat",), "DELEGATION_BOUNDARY_MATERIALIZED"),
        ("A051", ("circular","cycle"), "AUTHORITY_CYCLE_GUARD_MATERIALIZED"),
    ):
        if materialized(words, at):
            rows.append(_row(aid,labels[aid],"DETECTED",reason,"OCC1D_AUTHORITY_GRAPH_AUDIT",
                             {"artifact":str(auth_p.relative_to(root))}))
        else:
            rows.append(_row(aid,labels[aid],"INCONCLUSIVE",
                             "REQUIRED_AUTHORITY_GRAPH_FEATURE_NOT_MATERIALIZED",
                             "REPRESENTATION_BOUNDARY"))

    # Scope dimensions: do not invent absent source fields.
    scope_specs = (
        ("A045",("temporal","time","expiry","sunset"),"TEMPORAL_SCOPE_BOUNDARY_MATERIALIZED"),
        ("A046",("geograph","jurisdiction","location"),"GEOGRAPHIC_SCOPE_BOUNDARY_MATERIALIZED"),
        ("A047",("population","subject","actor"),"POPULATION_SCOPE_BOUNDARY_MATERIALIZED"),
        ("A048",("capability","action","operation"),"CAPABILITY_SCOPE_BOUNDARY_MATERIALIZED"),
        ("A049",("purpose","intent"),"PURPOSE_SCOPE_BOUNDARY_MATERIALIZED"),
    )
    for aid,words,reason in scope_specs:
        if materialized(words, st):
            rows.append(_row(aid,labels[aid],"DETECTED",reason,"OCC1D_SCOPE_TEMPORAL_AUDIT",
                             {"artifact":str(scope_p.relative_to(root))}))
        else:
            rows.append(_row(aid,labels[aid],"INCONCLUSIVE",
                             "SCOPE_DIMENSION_NOT_EXPLICITLY_MATERIALIZED",
                             "REPRESENTATION_BOUNDARY"))

    # Role-renaming laundering needs a role identity/alias semantic relation,
    # not merely a string named "role".
    if materialized(("role_alias","role_identity","rename"), at):
        rows.append(_row("A050",labels["A050"],"DETECTED",
                         "ROLE_IDENTITY_GUARD_MATERIALIZED","OCC1D_AUTHORITY_GRAPH_AUDIT",
                         {"artifact":str(auth_p.relative_to(root))}))
    else:
        rows.append(_row("A050",labels["A050"],"INCONCLUSIVE",
                         "ROLE_RENAME_SEMANTICS_NOT_MATERIALIZED","REPRESENTATION_BOUNDARY"))

    # Preserve canonical order.
    byid={r["attack_id"]:r for r in rows}
    rows=[byid["A%03d"%i] for i in range(43,53)]
    counts={v:sum(r["verdict"]==v for r in rows) for v in VERDICTS}
    return {
        "schema":SCHEMA, "version":"P159-OCC1H-H5-evidence-bound-v1",
        "family_id":"H5","scenario_count":10,"rows":rows,"verdict_counts":counts,
        "evidence_bound":True,"success_criteria_fixed_before_execution":True,
        "inconclusive_not_resisted":True,"normative_auto_rewrite":False,
        "authorization_created":False,"execution_performed":False,
        "functional_only":True,"phenomenology_undetermined":True,
        "occ1h_closed":False,"occ1i_opened":False,
        "p159_final_lock":False,"p160_opened":False,
    }
