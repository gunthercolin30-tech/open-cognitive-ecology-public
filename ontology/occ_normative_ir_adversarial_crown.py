from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Mapping

from ontology import occ_normative_ir as nir
from ontology import occ_normative_ir_real_builder as builder
from ontology import occ_normative_ir_referential_validator as v2
from ontology import occ_normative_ir_coherence_validator as v3
from ontology import occ_normative_ir_semantic_preservation_validator as v4
from ontology import occ_normative_ir_diff_coverage as dc
from ontology import occ_normative_ir_niri_consolidation as niri

PRIMITIVE="occ_normative_ir_adversarial_crown"
VERSION="P159-OCC1B-adversarial-crown-v1"
PASS,FAIL="PASS","FAIL"

def _hash_sources(root:Path)->Dict[str,str]:
    out={}
    for _,rel in builder.PARTITIONS:
        p=root/rel; out[rel]=sha256(p.read_bytes()).hexdigest()
    p=root/"manifest.yaml"; out["manifest.yaml"]=sha256(p.read_bytes()).hexdigest()
    return out

def _base(root:Path):
    r=builder.build_real_nir(root)
    if r.get("status")!=PASS: raise RuntimeError("REAL_NIR_BUILD_REQUIRED:"+str(r))
    return deepcopy(r["package"]["graph"])

def _node(g,cid):
    return next(n for n in g["nodes"] if n["node_id"]==cid)

def _v4_codes(r):
    codes=[x[0] for x in r.get("issues",())]
    if r.get("reason")=="V3_COHERENCE_REQUIRED":
        codes += [x[0] for x in r.get("v3_result",{}).get("issues",())]
    return tuple(codes)

def _record(rows,name,detected,detector,detail="",control=False):
    rows.append({"attack":name,"detected":bool(detected),"detector":detector,
                 "detail":detail,"control":bool(control)})

def run_crown(package_root:Path)->Dict[str,Any]:
    root=Path(package_root); before=_hash_sources(root); rows=[]
    base=_base(root)

    # Baseline composition must itself be healthy.
    baseline=(v2.validate_real_nir_references(root).get("status")==PASS and
              v3.validate_coherence(root).get("status")==PASS and
              v4.validate_semantic_preservation(root).get("status")==PASS and
              niri.consolidate(root).get("status")==PASS)
    _record(rows,"CONTROL_BASELINE_ACCEPTED",baseline,"V2+V3+V4+NIRI",control=True)

    # 1: silent loss.
    g=deepcopy(base); g["nodes"]=[x for x in g["nodes"] if x["node_id"]!="DNA.H1"]
    r=v4.validate_semantic_preservation(root,g)
    _record(rows,"DROP_NORM",r.get("status")==FAIL and "SILENT_LOSS" in _v4_codes(r),"V4")

    # 2: invented normative object.
    g=deepcopy(base); x=deepcopy(g["nodes"][0]); x["node_id"]="DNA.H999"; g["nodes"].append(x)
    r=v4.validate_semantic_preservation(root,g)
    _record(rows,"INVENT_NORM",r.get("status")==FAIL,"V3/V4")

    # 3: H9 F17 laundering/loss.
    g=deepcopy(base); h9=_node(g,"DNA.H9"); h9["source_object_id"]="F12"; h9["evidence_ids"]=["F12"]
    r=v4.validate_semantic_preservation(root,g)
    _record(rows,"H9_DROP_F17",r.get("status")==FAIL and "SILENT_LOSS_OR_EXTENSION" in _v4_codes(r),"V4")

    # 4: partial -> more formal without source basis.
    g=deepcopy(base); _node(g,"DNA.H1")["formalization_level"]="F3"
    r=v4.validate_semantic_preservation(root,g)
    _record(rows,"PARTIAL_TO_COMPLETE",r.get("status")==FAIL and "FORMALIZATION_PROMOTION_OR_CHANGE" in _v4_codes(r),"V4")

    # 5: provenance break.
    g=deepcopy(base); _node(g,"DNA.H1")["source_object_id"]="F999"
    r=v4.validate_semantic_preservation(root,g)
    _record(rows,"PROVENANCE_BREAK",r.get("status")==FAIL and "PROVENANCE_BREAK" in _v4_codes(r),"V4")

    # 6: source-map fingerprint laundering.
    g=deepcopy(base); _node(g,"DNA.H1")["source_map"]["source_sha256"]="0"*64
    r=v4.validate_semantic_preservation(root,g)
    _record(rows,"FINGERPRINT_LAUNDERING",r.get("status")==FAIL and "PROVENANCE_BREAK" in _v4_codes(r),"V4")

    # 7: evidence promoted to authority.
    g=deepcopy(base); n=_node(g,"DNA.H1"); n["authority_from_evidence"]=True
    r=v3.validate_coherence(root,g)
    _record(rows,"EVIDENCE_TO_AUTHORITY",r.get("status")==FAIL and
            any(x[0]=="EVIDENCE_IS_NOT_AUTHORITY" for x in r.get("issues",())),"V3")

    # 8: direct authority inflation.
    g=deepcopy(base); g["metadata"]["authority_granted"]=True
    r=v3.validate_coherence(root,g)
    _record(rows,"AUTHORITY_INFLATION",r.get("status")==FAIL and
            any(x[0]=="AUTHORITY_OR_EXECUTION_AMPLIFICATION" for x in r.get("issues",())),"V3")

    # 9: execution activation.
    g=deepcopy(base); g["metadata"]["execution_enabled"]=True
    r=v3.validate_coherence(root,g)
    _record(rows,"EXECUTION_ACTIVATION",r.get("status")==FAIL and
            any(x[0]=="AUTHORITY_OR_EXECUTION_AMPLIFICATION" for x in r.get("issues",())),"V3")

    # 10: hard constraint converted into weight.
    g=deepcopy(base); _node(g,"DNA.H1")["weight"]=0.5
    r=v3.validate_coherence(root,g)
    _record(rows,"HARD_CONSTRAINT_TO_WEIGHT",r.get("status")==FAIL and
            any(x[0]=="HARD_CONSTRAINT_WEIGHTING_FORBIDDEN" for x in r.get("issues",())),"V3")

    # 11: forbidden override relation.
    g=deepcopy(base); g["edges"]=[{"source":"CCAD.P0","target":"DNA.L0.1","type":"OVERRIDES"}]
    r=v3.validate_coherence(root,g)
    _record(rows,"CCAD_OVERRIDE_DNA",r.get("status")==FAIL and
            any(x[0]=="UNSUPPORTED_OVERRIDE_RELATION" for x in r.get("issues",())),"V3")

    # 12: conflict silently arbitrated.
    g=deepcopy(base); g["edges"]=[{"source":"DNA.H1","target":"DNA.H2",
                                   "type":"CONFLICTS_WITH","winner":"DNA.H1"}]
    r=v3.validate_coherence(root,g)
    _record(rows,"CONFLICT_WINNER_INJECTION",r.get("status")==FAIL and
            any(x[0]=="NIR_ARBITRATION_FORBIDDEN" for x in r.get("issues",())),"V3")

    # 13: hidden executable payload.
    g=deepcopy(base); _node(g,"DNA.H1")["script"]="echo forbidden"
    r=nir.validate_graph(g)
    _record(rows,"HIDDEN_EXECUTABLE_PAYLOAD",r.get("status")==FAIL,"FOUNDATION")

    # 14: unbounded recursion.
    expr={"operator":"ALL_OF","operands":["leaf"]}
    for _ in range(35): expr={"operator":"ALL_OF","operands":[expr]}
    r=nir.validate_constraint_expression(expr)
    _record(rows,"UNBOUNDED_RECURSION",r.get("status")==FAIL and
            r.get("reason")=="UNBOUNDED_CONSTRAINT_RECURSION","FOUNDATION")

    # 15: coalition inflation / invalid threshold.
    expr={"operator":"AT_LEAST_N","n":3,"operands":["a","b"]}
    r=nir.validate_constraint_expression(expr)
    _record(rows,"COALITION_INFLATION",r.get("status")==FAIL and
            r.get("reason")=="CONSTRAINT_N_INVALID","FOUNDATION")

    # 16: UNKNOWN/N-A collapse attempt at typed condition boundary.
    sm=deepcopy(_node(base,"DNA.H1")["source_map"])
    cond={"node_id":"SYN.COND","node_type":"ConditionNode","formalization_level":"F1",
          "source_map":sm,"condition_state":"TRUE"}
    r=nir.validate_node(cond)
    _record(rows,"UNKNOWN_NA_DOMAIN_COLLAPSE",r.get("status")==FAIL and
            r.get("reason")=="UNKNOWN_CONDITION_STATE","FOUNDATION")

    # 17: implicit global scope.
    scope={"node_id":"SYN.SCOPE","node_type":"ScopeNode","formalization_level":"F1",
           "source_map":sm,"dimensions":{"subject":"GLOBAL"}}
    r=nir.validate_node(scope)
    _record(rows,"IMPLICIT_GLOBAL_SCOPE",r.get("status")==FAIL and
            r.get("reason")=="IMPLICIT_GLOBAL_SCOPE_FORBIDDEN","FOUNDATION",
            detail="synthetic typed-boundary test; NIRI-6 remains bounded for real 48-object source")

    # 18: missing temporal constraints.
    temp={"node_id":"SYN.TIME","node_type":"TemporalNode","formalization_level":"F1","source_map":sm}
    r=nir.validate_node(temp)
    _record(rows,"TEMPORAL_CONSTRAINT_ERASURE",r.get("status")==FAIL and
            r.get("reason")=="TEMPORAL_CONSTRAINTS_MISSING","FOUNDATION",
            detail="synthetic typed-boundary test; NIRI-7 remains bounded for real 48-object source")

    # Controls: unresolved conflict is legal and order is non-semantic.
    g=deepcopy(base); g["edges"]=[{"source":"DNA.H1","target":"DNA.H2","type":"CONFLICTS_WITH"}]
    r=v3.validate_coherence(root,g)
    _record(rows,"CONTROL_UNRESOLVED_CONFLICT_ACCEPTED",r.get("status")==PASS,"V3",control=True)

    g=deepcopy(base); g["nodes"]=list(reversed(g["nodes"]))
    r=v4.validate_semantic_preservation(root,g)
    _record(rows,"CONTROL_NODE_ORDER_NON_SEMANTIC",r.get("status")==PASS,"V4",control=True)

    d=dc.normative_ir_diff(base,deepcopy(base))
    _record(rows,"CONTROL_ZERO_DIFF",d.get("change_count")==0,"DIFF",control=True)

    after=_hash_sources(root)
    source_immutable=before==after
    attacks=[x for x in rows if not x["control"]]
    controls=[x for x in rows if x["control"]]
    false_neg=[x["attack"] for x in attacks if not x["detected"]]
    false_pos=[x["attack"] for x in controls if not x["detected"]]
    report={"schema":"oce.p159.occ1b.adversarial_crown.v1",
            "attack_count":len(attacks),"attack_detected_count":sum(1 for x in attacks if x["detected"]),
            "control_count":len(controls),"control_pass_count":sum(1 for x in controls if x["detected"]),
            "false_negatives":false_neg,"control_failures":false_pos,
            "source_package_mutated":not source_immutable,
            "rows":rows,
            "niri_6_scope_real_source_claim":"BOUNDED_NOT_APPLICABLE_SOURCE_ABSENT",
            "niri_7_temporal_real_source_claim":"BOUNDED_NOT_APPLICABLE_SOURCE_ABSENT",
            "authority_activated":False,"execution_performed":False,
            "occ1c_opened":False,"p160_opened":False,"final_lock_performed":False,
            "functional_conclusion_only":True,"phenomenology_undetermined":True}
    report["report_sha256"]=nir.canonical_sha256(report)
    ok=(not false_neg and not false_pos and source_immutable)
    return {"status":PASS if ok else FAIL,
            "reason":"P159_OCC1B_ADVERSARIAL_CROWN_OK" if ok else "P159_OCC1B_ADVERSARIAL_CROWN_FAILED",
            "report":report,"report_sha256":report["report_sha256"]}
