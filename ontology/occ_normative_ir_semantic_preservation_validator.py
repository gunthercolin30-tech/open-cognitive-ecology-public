from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json, re
from pathlib import Path
from typing import Any, Dict, Mapping, Tuple

from ontology import occ_normative_ir as nir
from ontology import occ_normative_ir_real_builder as builder
from ontology import occ_normative_ir_coherence_validator as v3

PRIMITIVE="occ_normative_ir_semantic_preservation_validator"
VERSION="P159-OCC1B-V4-semantic-preservation-v1"
PASS,FAIL="PASS","FAIL"
PARTITIONS=builder.PARTITIONS

def _r(status,reason,**extra):
    out={"primitive":PRIMITIVE,"version":VERSION,"status":status,"reason":reason,
         "authorization_created":False,"authority_activated":False,"execution_performed":False,
         "occ1c_opened":False,"p160_opened":False,"functional_conclusion_only":True,
         "phenomenology_undetermined":True}
    out.update(deepcopy(extra)); return out

def _sha(p:Path)->str: return sha256(p.read_bytes()).hexdigest()

def _formal(v:Any)->str:
    m=re.match(r"^(F[0-3])(?:_|$)",str(v or "").strip().upper())
    return m.group(1) if m else ""

def independent_source_fingerprint(root:Path)->Dict[str,Any]:
    # Deliberately does not call the NIR builder: source semantics are extracted
    # independently from the six canonical principal partitions.
    root=Path(root); objects={}
    for level,rel in PARTITIONS:
        p=root/rel
        if not p.is_file(): return _r(FAIL,"SOURCE_PARTITION_MISSING",path=rel)
        try: data=json.loads(p.read_text(encoding="utf-8"))
        except Exception as e: return _r(FAIL,"SOURCE_PARTITION_PARSE_FAILED",path=rel,error=str(e))
        if not isinstance(data,Mapping) or not isinstance(data.get("norms"),list):
            return _r(FAIL,"SOURCE_PARTITION_STRUCTURE_INVALID",path=rel)
        digest=_sha(p)
        for idx,n in enumerate(data["norms"]):
            cid=str(n.get("canonical_id","")).strip()
            if not cid or cid in objects: return _r(FAIL,"SOURCE_IDENTITY_INVALID",canonical_id=cid)
            objects[cid]={
                "canonical_id":cid,"normative_level":level,
                "formalization_level":_formal(n.get("formalization")),
                "semantic_status":n.get("semantic_status"),
                "source_object_id":n.get("source_object_id"),
                "text":n.get("text"),
                "evidence_ids":deepcopy(n.get("evidence_ids",[])),
                "lineage_kind":n.get("lineage_kind"),
                "lineage_artifacts":deepcopy(n.get("lineage_artifacts",[])),
                "execution_enabled":bool(n.get("execution_enabled",False)),
                "runtime_authority_granted":bool(n.get("runtime_authority_granted",False)),
                "source_map":{"source_id":cid,"source_path":"normative/occ1a/"+rel,
                              "source_field":"norms[%d]"%idx,"source_sha256":digest},
                "machine_formalization_claimed":bool(n.get("machine_formalization_claimed",False)),
            }
    if len(objects)!=48: return _r(FAIL,"SOURCE_KERNEL_COUNT_MISMATCH",count=len(objects))
    fp={"schema":"oce.p159.occ1b.v4.source_fingerprint.v1",
        "objects":{k:objects[k] for k in sorted(objects)}}
    return _r(PASS,"INDEPENDENT_SOURCE_FINGERPRINT_OK",fingerprint=fp,
              fingerprint_sha256=nir.canonical_sha256(fp))

def _compare(src:Mapping[str,Any],node:Mapping[str,Any])->Tuple[Tuple[str,str],...]:
    cid=src["canonical_id"]; issues=[]
    exact=("normative_level","formalization_level","semantic_status","source_object_id","text",
           "evidence_ids","lineage_kind","lineage_artifacts","execution_enabled",
           "runtime_authority_granted","source_map")
    for key in exact:
        if node.get(key)!=src.get(key):
            code={
              "formalization_level":"FORMALIZATION_PROMOTION_OR_CHANGE",
              "source_object_id":"PROVENANCE_BREAK",
              "evidence_ids":"SILENT_LOSS_OR_EXTENSION",
              "lineage_kind":"PROVENANCE_BREAK",
              "lineage_artifacts":"PROVENANCE_BREAK",
              "source_map":"PROVENANCE_BREAK",
              "execution_enabled":"AUTHORITY_OR_EXECUTION_AMPLIFICATION",
              "runtime_authority_granted":"AUTHORITY_OR_EXECUTION_AMPLIFICATION",
              "text":"SILENT_LOSS_OR_SEMANTIC_EXTENSION",
              "semantic_status":"SEMANTIC_STATUS_CHANGE",
              "normative_level":"NORMATIVE_LEVEL_CHANGE",
            }[key]
            issues.append((code,cid+":"+key))
    expected_partial=src["formalization_level"] in ("F0","F1","F2")
    if node.get("partial_formalization_explicit") is not expected_partial:
        issues.append(("PARTIAL_FORMALIZATION_LOST",cid))
    if cid=="GENESIS.G0":
        if node.get("human_judgment_required") is not True:
            issues.append(("HUMAN_JUDGMENT_REQUIREMENT_LOST",cid))
        if node.get("machine_formalization_claimed") is not False:
            issues.append(("FORMALIZATION_PROMOTION_OR_CHANGE",cid))
    return tuple(issues)

def validate_semantic_preservation(package_root:Path, graph_override=None)->Dict[str,Any]:
    sf=independent_source_fingerprint(Path(package_root))
    if sf.get("status")!=PASS: return sf
    built=builder.build_real_nir(Path(package_root))
    if built.get("status")!=PASS: return _r(FAIL,"REAL_NIR_BUILD_REQUIRED",build_result=built)
    graph=deepcopy(graph_override if graph_override is not None else built["package"]["graph"])
    coh=v3.validate_coherence(Path(package_root),graph)
    if coh.get("status")!=PASS: return _r(FAIL,"V3_COHERENCE_REQUIRED",v3_result=coh)

    src=sf["fingerprint"]["objects"]
    nodes={str(n.get("node_id","")):n for n in graph.get("nodes",())}
    issues=[]
    missing=sorted(set(src)-set(nodes)); invented=sorted(set(nodes)-set(src))
    issues += [("SILENT_LOSS",x) for x in missing]
    issues += [("SEMANTIC_EXTENSION",x) for x in invented]
    for cid in sorted(set(src)&set(nodes)): issues.extend(_compare(src[cid],nodes[cid]))

    # Current OCC-1A kernel has no explicit source scope/temporal structures in
    # these 48 principal records. V4 must not fabricate them merely to test them.
    scope_temporal="NOT_APPLICABLE_SOURCE_ABSENT"
    if issues:
        return _r(FAIL,"SEMANTIC_PRESERVATION_VIOLATION",issues=tuple(sorted(issues)),
                  source_fingerprint_sha256=sf["fingerprint_sha256"])

    report={"schema":"oce.p159.occ1b.v4.semantic_preservation.v1",
            "objects_compared":48,"silent_loss":0,"semantic_extension":0,
            "formalization_change":0,"authority_amplification":0,"provenance_break":0,
            "partial_formalization_lost":0,"source_to_nir_exact_semantic_fields":"48/48",
            "scope_temporal_preservation":scope_temporal,
            "independent_source_fingerprint":True,
            "builder_used_as_source_oracle":False}
    return _r(PASS,"P159_OCC1B_V4_SEMANTIC_PRESERVATION_OK",report=report,
              report_sha256=nir.canonical_sha256(report),
              source_fingerprint_sha256=sf["fingerprint_sha256"])
