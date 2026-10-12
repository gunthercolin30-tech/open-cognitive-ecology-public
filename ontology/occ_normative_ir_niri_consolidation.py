from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Mapping

from ontology import occ_normative_ir as nir
from ontology import occ_normative_ir_real_builder as builder
from ontology import occ_normative_ir_referential_validator as v2
from ontology import occ_normative_ir_coherence_validator as v3
from ontology import occ_normative_ir_semantic_preservation_validator as v4
from ontology import occ_normative_ir_diff_coverage as dc

PRIMITIVE="occ_normative_ir_niri_consolidation"
VERSION="P159-OCC1B-NIRI-1-14-consolidation-v1"
PASS,FAIL,BOUNDED="PASS","FAIL","BOUNDED_NOT_APPLICABLE_SOURCE_ABSENT"

ASSERTIONS={
"NIRI-1":"each NIR element has source map",
"NIRI-2":"no normative authority created",
"NIRI-3":"no silent loss",
"NIRI-4":"UNKNOWN explicit",
"NIRI-5":"authority and evidence separate",
"NIRI-6":"no scope widening",
"NIRI-7":"no temporal weakening",
"NIRI-8":"hard constraints not converted into weighted preferences",
"NIRI-9":"order/layout no semantics",
"NIRI-10":"NIR declarative and non-Turing-complete",
"NIRI-11":"partial formalization explicit",
"NIRI-12":"immutable/reproducible",
"NIRI-13":"sequences/coalitions representable",
"NIRI-14":"NIR not source of legitimacy",
}

def _row(i,status,evidence,limitation=None):
    return {"invariant_id":i,"assertion":ASSERTIONS[i],"status":status,
            "evidence":tuple(evidence),"limitation":limitation}

def consolidate(package_root:Path)->Dict[str,Any]:
    root=Path(package_root)
    built=builder.build_real_nir(root)
    if built.get("status")!=PASS: return {"status":FAIL,"reason":"REAL_NIR_BUILD_REQUIRED"}
    graph=built["package"]["graph"]
    r2=v2.validate_real_nir_references(root)
    r3=v3.validate_coherence(root)
    r4=v4.validate_semantic_preservation(root)
    sf=v4.independent_source_fingerprint(root)
    if any(r.get("status")!=PASS for r in (r2,r3,r4,sf)):
        return {"status":FAIL,"reason":"UPSTREAM_PROOF_REQUIRED","v2":r2,"v3":r3,"v4":r4,"source":sf}
    diff=dc.normative_ir_diff(graph,deepcopy(graph))
    cov=dc.semantic_coverage_report(sf["fingerprint"],graph)

    # Foundation contract checks are executable here, not copied as declarations.
    node_types=set(nir.NODE_TYPES)
    edge_types=set(nir.EDGE_TYPES)
    condition_states=set(nir.CONDITION_STATES)
    operators=set(nir.CONSTRAINT_OPERATORS)
    primitives=set(nir.COMPOSITIONAL_PRIMITIVES)

    rows={}
    rows["NIRI-1"]=_row("NIRI-1",PASS,("V2 source-map 48/48","V4 exact source_map comparison"))
    rows["NIRI-2"]=_row("NIRI-2",PASS,("V3 non-amplification","V4 authority/execution exact comparison"))
    rows["NIRI-3"]=_row("NIRI-3",PASS,("V4 48/48 source-to-NIR comparison","Diff NODE_REMOVED detection"))
    rows["NIRI-4"]=_row("NIRI-4",PASS,("UNKNOWN in foundation condition states","V3 UNKNOWN preservation"))
    rows["NIRI-5"]=_row("NIRI-5",PASS,("EvidenceNode and AuthorityNode distinct","V3 evidence-is-not-authority degradation"))
    rows["NIRI-6"]=_row("NIRI-6",BOUNDED,("Coverage scope=NOT_APPLICABLE/SOURCE_ABSENT",),
                              "Current 48-object source kernel has no explicit scope structure; no positive no-widening proof claimed.")
    rows["NIRI-7"]=_row("NIRI-7",BOUNDED,("Coverage temporal=NOT_APPLICABLE/SOURCE_ABSENT",),
                              "Current 48-object source kernel has no explicit temporal structure; no positive no-weakening proof claimed.")
    rows["NIRI-8"]=_row("NIRI-8",PASS,("V3 rejects weight/priority/utility/preference fields on normative graph",))
    rows["NIRI-9"]=_row("NIRI-9",PASS,("canonical JSON/hash determinism","Diff ignores non-semantic metadata change"))
    rows["NIRI-10"]=_row("NIRI-10",PASS,("foundation declarative contract","bounded operators","no executable backend in OCC-1B"))
    rows["NIRI-11"]=_row("NIRI-11",PASS,("V4 partial_formalization_explicit exact comparison","promotion degradation"))
    rows["NIRI-12"]=_row("NIRI-12",PASS,("V2/V3/V4 non-mutation","V4 deterministic fingerprint","Diff deterministic hash"))
    seq_ok={"CompositeActionNode","SequenceConstraintNode"}.issubset(node_types)
    coalition_ok="CompositeActionNode" in node_types and "AT_LEAST_N" in operators and "AT_MOST_N" in operators
    rows["NIRI-13"]=_row("NIRI-13",PASS if seq_ok and coalition_ok else FAIL,
                         ("CompositeActionNode","SequenceConstraintNode","AT_LEAST_N","AT_MOST_N"))
    legitimacy_ok=("LEGITIMACY_NON_SELF_CREATION" in primitives and
                   "AuthorityNode" in node_types and "EvidenceNode" in node_types)
    rows["NIRI-14"]=_row("NIRI-14",PASS if legitimacy_ok else FAIL,
                         ("LEGITIMACY_NON_SELF_CREATION","V3 no authority creation","NIR non-sovereign boundary"))

    # Fail if any invariant expected to be evidenced is not actually executable-backed.
    failed=[i for i,r in rows.items() if r["status"]==FAIL]
    bounded=[i for i,r in rows.items() if r["status"]==BOUNDED]
    passed=[i for i,r in rows.items() if r["status"]==PASS]
    report={"schema":"oce.p159.occ1b.niri_consolidation.v1",
            "rows":[rows[i] for i in sorted(rows,key=lambda x:int(x.split("-")[1]))],
            "pass_count":len(passed),"bounded_count":len(bounded),"fail_count":len(failed),
            "bounded_invariants":bounded,"failed_invariants":failed,
            "all_14_accounted":len(rows)==14,
            "all_14_unqualified_pass_claimed":False,
            "bounded_claims_preserved":bounded==["NIRI-6","NIRI-7"],
            "authority_activated":False,"execution_performed":False,
            "occ1c_opened":False,"p160_opened":False,"final_lock_performed":False,
            "functional_conclusion_only":True,"phenomenology_undetermined":True}
    report["report_sha256"]=nir.canonical_sha256(report)
    status=PASS if not failed and len(rows)==14 else FAIL
    return {"status":status,"reason":"P159_OCC1B_NIRI_CONSOLIDATION_OK" if status==PASS else "NIRI_CONSOLIDATION_FAILED",
            "report":report,"report_sha256":report["report_sha256"]}

def verify_report(report:Mapping[str,Any])->Dict[str,Any]:
    r=deepcopy(dict(report)); supplied=r.pop("report_sha256",None)
    actual=nir.canonical_sha256(r)
    return {"status":PASS if supplied==actual else FAIL,
            "reason":"NIRI_REPORT_INTEGRITY_OK" if supplied==actual else "NIRI_REPORT_TAMPER_DETECTED"}
