from __future__ import annotations
from copy import deepcopy
from typing import Any, Dict, Mapping, Sequence, Tuple

from ontology import occ_normative_ir as nir

PRIMITIVE="occ_normative_ir_diff_coverage"
VERSION="P159-OCC1B-NormativeIRDiff-SemanticCoverage-v1"
PASS,FAIL="PASS","FAIL"

TRACKED_FIELDS=(
    "normative_level","formalization_level","semantic_status","source_object_id","text",
    "evidence_ids","lineage_kind","lineage_artifacts","source_map",
    "partial_formalization_explicit","human_judgment_required",
    "runtime_authority_granted","execution_enabled",
    "scope","temporal","uncertainty","review",
)
FORMAL_RANK={"F0":0,"F1":1,"F2":2,"F3":3}

def _canon(v:Any)->str:
    return nir.canonical_json(v)

def _classify(field:str,before:Any,after:Any)->str:
    if field=="formalization_level":
        a,b=FORMAL_RANK.get(str(before),-1),FORMAL_RANK.get(str(after),-1)
        return "FORMALIZATION_PROMOTION" if b>a else "FORMALIZATION_DEMOTION" if b<a else "FORMALIZATION_CHANGE"
    if field in ("runtime_authority_granted","execution_enabled"):
        return "AUTHORITY_OR_EXECUTION_AMPLIFICATION" if after is True and before is not True else "AUTHORITY_OR_EXECUTION_REDUCTION"
    if field in ("source_object_id","lineage_kind","lineage_artifacts","source_map"):
        return "PROVENANCE_CHANGE"
    if field=="scope": return "SCOPE_CHANGE_DIRECTION_REQUIRES_TYPED_SCOPE_SEMANTICS"
    if field=="temporal": return "TEMPORAL_CHANGE_DIRECTION_REQUIRES_TYPED_TEMPORAL_SEMANTICS"
    if field=="uncertainty": return "UNCERTAINTY_CHANGE"
    if field=="review": return "REVIEW_CHANGE"
    if field=="text": return "NORMATIVE_TEXT_CHANGE"
    if field=="semantic_status": return "SEMANTIC_STATUS_CHANGE"
    if field=="evidence_ids": return "EVIDENCE_SET_CHANGE"
    return "SEMANTIC_FIELD_CHANGE"

def normative_ir_diff(before_graph:Mapping[str,Any],after_graph:Mapping[str,Any])->Dict[str,Any]:
    b={str(n.get("node_id","")):n for n in before_graph.get("nodes",())}
    a={str(n.get("node_id","")):n for n in after_graph.get("nodes",())}
    changes=[]
    for cid in sorted(set(b)-set(a)): changes.append({"kind":"NODE_REMOVED","node_id":cid})
    for cid in sorted(set(a)-set(b)): changes.append({"kind":"NODE_ADDED","node_id":cid})
    for cid in sorted(set(a)&set(b)):
        for field in TRACKED_FIELDS:
            bv,av=b[cid].get(field),a[cid].get(field)
            if _canon(bv)!=_canon(av):
                changes.append({"kind":_classify(field,bv,av),"node_id":cid,"field":field,
                                "before":deepcopy(bv),"after":deepcopy(av)})
    be={_canon(e):e for e in before_graph.get("edges",())}
    ae={_canon(e):e for e in after_graph.get("edges",())}
    for k in sorted(set(be)-set(ae)): changes.append({"kind":"EDGE_REMOVED","edge":deepcopy(be[k])})
    for k in sorted(set(ae)-set(be)): changes.append({"kind":"EDGE_ADDED","edge":deepcopy(ae[k])})
    report={"schema":"oce.p159.occ1b.normative_ir_diff.v1","change_count":len(changes),
            "changes":changes,"authority_decision_made":False,"conflict_arbitrated":False}
    report["diff_sha256"]=nir.canonical_sha256(report)
    return report

def semantic_coverage_report(source_fingerprint:Mapping[str,Any],graph:Mapping[str,Any])->Dict[str,Any]:
    src=source_fingerprint["objects"]
    nodes={str(n.get("node_id","")):n for n in graph.get("nodes",())}
    rows=[]; counts={"SUPPORTED":0,"PARTIAL":0,"HUMAN_JUDGMENT_REQUIRED":0,"UNSUPPORTED":0,"NOT_APPLICABLE":0}
    for cid in sorted(src):
        s=src[cid]; n=nodes.get(cid)
        if n is None:
            status="UNSUPPORTED"
        elif str(s.get("semantic_status"))=="HUMAN_JUDGMENT_REQUIRED":
            status="HUMAN_JUDGMENT_REQUIRED"
        elif str(s.get("formalization_level")) in ("F0","F1","F2"):
            status="PARTIAL"
        elif str(s.get("formalization_level"))=="F3":
            status="SUPPORTED"
        else:
            status="UNSUPPORTED"
        counts[status]+=1
        rows.append({"canonical_id":cid,"coverage_status":status,
                     "formalization_level":s.get("formalization_level"),
                     "semantic_status":s.get("semantic_status"),
                     "represented_in_nir":n is not None})
    # Scope/temporal are absent in the current 48-object source kernel. They are
    # explicitly N/A, never counted as semantic success.
    dimensions={
        "principal_object_presence":{"status":"MEASURED","represented":sum(1 for r in rows if r["represented_in_nir"]),"total":len(rows)},
        "formalization":{"status":"MEASURED","counts":counts},
        "scope":{"status":"NOT_APPLICABLE","reason":"SOURCE_ABSENT"},
        "temporal":{"status":"NOT_APPLICABLE","reason":"SOURCE_ABSENT"},
    }
    report={"schema":"oce.p159.occ1b.semantic_coverage.v1","object_count":len(rows),
            "coverage_counts":counts,"rows":rows,"dimensions":dimensions,
            "presence_is_not_full_semantic_coverage":True,
            "full_semantic_coverage_claimed":False,
            "authority_decision_made":False}
    report["coverage_sha256"]=nir.canonical_sha256(report)
    return report
