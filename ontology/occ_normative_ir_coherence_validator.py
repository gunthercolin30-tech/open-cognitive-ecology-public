from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence, Tuple

from ontology import occ_normative_ir as nir
from ontology import occ_normative_ir_real_builder as real_builder
from ontology import occ_normative_ir_referential_validator as v2

PRIMITIVE="occ_normative_ir_coherence_validator"
VERSION="P159-OCC1B-V3-normative-coherence-v1"
PASS,FAIL="PASS","FAIL"

LEVEL_RANK={"GENESIS":0,"DNA_H":1,"DNA_L0":1,"DNA_L1":2,"CCAD":3,"CONSTITUTION":4,"GOVERNANCE":5,"POLICY":6}
HARD_RELATIONS={"CANNOT_OVERRIDE","SUBORDINATE_TO","REQUIRES_SATISFACTION_OF","PRECONDITION_FOR"}
AUTHORITY_CREATING_KEYS={"authority_granted","runtime_authority_granted","execution_enabled","may_override_dna","root_override_all"}
FORBIDDEN_ARBITRATION_KEYS={"winner","selected_norm","resolved_by_nir","automatic_resolution","conflict_winner"}
WEIGHT_KEYS={"weight","priority_score","utility_score","preference_weight"}

def _r(status,reason,**extra):
    out={"primitive":PRIMITIVE,"version":VERSION,"status":status,"reason":reason,
         "authorization_created":False,"authority_activated":False,"execution_performed":False,
         "occ1c_opened":False,"p160_opened":False,"v4_semantic_preservation_claimed":False,
         "functional_conclusion_only":True,"phenomenology_undetermined":True}
    out.update(deepcopy(extra)); return out

def _walk(obj,path="$"):
    yield path,obj
    if isinstance(obj,Mapping):
        for k,v in obj.items():
            yield from _walk(v,path+"."+str(k))
    elif isinstance(obj,(list,tuple)):
        for i,v in enumerate(obj):
            yield from _walk(v,path+"["+str(i)+"]")

def _node_level(node):
    raw=str(node.get("normative_level") or node.get("level") or "")
    return raw.upper().replace("-","_")

def validate_coherence(package_root:Path, graph_override=None):
    rr=v2.validate_real_nir_references(Path(package_root))
    if rr.get("status")!=PASS:
        return _r(FAIL,"V2_REFERENTIAL_VALIDATION_REQUIRED",v2_result=rr)
    built=real_builder.build_real_nir(Path(package_root))
    if built.get("status")!=PASS: return _r(FAIL,"REAL_NIR_BUILD_REQUIRED")
    graph=deepcopy(graph_override if graph_override is not None else built["package"]["graph"])
    issues=[]; nodes={n["node_id"]:n for n in graph.get("nodes",())}

    # Non-self-creation: no declarative field may activate execution or grant authority.
    for path,val in _walk(graph):
        key=path.rsplit(".",1)[-1]
        if key in AUTHORITY_CREATING_KEYS and val is True:
            issues.append(("AUTHORITY_OR_EXECUTION_AMPLIFICATION",path))
        if key in FORBIDDEN_ARBITRATION_KEYS and val not in (False,None,"","UNRESOLVED","UNKNOWN"):
            issues.append(("NIR_ARBITRATION_FORBIDDEN",path))
        if key in WEIGHT_KEYS:
            issues.append(("HARD_CONSTRAINT_WEIGHTING_FORBIDDEN",path))

    # UNKNOWN must remain an explicit admissible condition state.
    if "UNKNOWN" not in nir.CONDITION_STATES:
        issues.append(("UNKNOWN_SEMANTICS_MISSING","foundation"))

    # Relations are checked without resolving conflicts.
    for i,e in enumerate(graph.get("edges",())):
        typ=str(e.get("type") or e.get("edge_type") or "")
        src=str(e.get("source") or ""); dst=str(e.get("target") or "")
        if src not in nodes or dst not in nodes:
            issues.append(("BROKEN_NORM_REFERENCE","edge[%d]"%i)); continue
        sl,dl=_node_level(nodes[src]),_node_level(nodes[dst])

        # Lower normative levels may not create a relation claiming they override
        # Genesis/DNA. This is conservative and does not manufacture precedence.
        if typ in ("OVERRIDES","SUPERSEDES"):
            issues.append(("UNSUPPORTED_OVERRIDE_RELATION","edge[%d]"%i))
        if typ=="CONFLICTS_WITH" and any(k in e for k in FORBIDDEN_ARBITRATION_KEYS):
            issues.append(("CONFLICT_MUST_REMAIN_UNRESOLVED","edge[%d]"%i))
        if typ in HARD_RELATIONS and sl in LEVEL_RANK and dl in LEVEL_RANK:
            # These relations may encode explicit source relations; V3 records them
            # but never turns numeric rank into a global DNA-H ordering.
            if sl=="DNA_H" and dl=="DNA_H" and e.get("numeric_priority") is not None:
                issues.append(("DNA_H_GLOBAL_NUMERIC_HIERARCHY_FORBIDDEN","edge[%d]"%i))

    # Evidence is not authority.
    for n in nodes.values():
        if n.get("evidence_ids") and n.get("authority_from_evidence") is True:
            issues.append(("EVIDENCE_IS_NOT_AUTHORITY",n["node_id"]))

    if issues:
        return _r(FAIL,"NORMATIVE_COHERENCE_VIOLATION",issues=tuple(sorted(issues)))

    report={"schema":"oce.p159.occ1b.v3.normative_coherence.v1",
            "object_count":len(nodes),"issue_count":0,
            "coherence_checked":True,"conflicts_arbitrated":False,
            "authority_created":False,"execution_enabled":False,
            "dna_h_global_numeric_hierarchy_created":False,
            "evidence_promoted_to_authority":False,
            "unknown_preserved":True,
            "v4_semantic_preservation_claimed":False}
    return _r(PASS,"P159_OCC1B_V3_NORMATIVE_COHERENCE_OK",
              report=report,report_sha256=nir.canonical_sha256(report),issue_count=0)
