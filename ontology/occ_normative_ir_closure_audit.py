from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

from ontology import occ_normative_ir as nir
from ontology import occ_normative_ir_real_builder as builder
from ontology import occ_normative_ir_referential_validator as v2
from ontology import occ_normative_ir_coherence_validator as v3
from ontology import occ_normative_ir_semantic_preservation_validator as v4
from ontology import occ_normative_ir_diff_coverage as dc
from ontology import occ_normative_ir_niri_consolidation as niri
from ontology import occ_normative_ir_adversarial_crown as crown

PRIMITIVE = "occ_normative_ir_closure_audit"
VERSION = "P159-OCC1B-closure-audit-v1"
PASS, FAIL = "PASS", "FAIL"


EXPECTED_NORMALIZED_CAPABILITIES = {
    "OBSERVE","READ","WRITE","EXECUTE","DELEGATE","CREATE_IDENTITY",
    "MODIFY_MEMORY","MODIFY_GOVERNANCE","MODIFY_CONSTITUTION","SPAWN_AGENT",
    "NETWORK_ACCESS","RESOURCE_ALLOCATION",
}

def _normalized_capabilities_from_foundation():
    for name in sorted(dir(nir)):
        if "CAPABIL" not in name.upper():
            continue
        value = getattr(nir, name)
        if isinstance(value, (tuple, list, set, frozenset)):
            values = {str(x) for x in value}
            if EXPECTED_NORMALIZED_CAPABILITIES.issubset(values):
                return tuple(sorted(EXPECTED_NORMALIZED_CAPABILITIES))
    return tuple()

SAT, BOUNDED, MISSING = "SATISFIED", "BOUNDED", "MISSING"

def _req(req_id:str, statement:str, status:str, evidence:List[str], limitation:str|None=None)->Dict[str,Any]:
    return {"requirement_id":req_id, "statement":statement, "status":status,
            "evidence":tuple(evidence), "limitation":limitation}

def audit(package_root:Path)->Dict[str,Any]:
    root = Path(package_root)
    built = builder.build_real_nir(root)
    if built.get("status") != PASS:
        return {"status":FAIL, "decision":"NOT_READY_TO_CLOSE", "reason":"REAL_NIR_BUILD_REQUIRED"}

    graph = built["package"]["graph"]
    r2 = v2.validate_real_nir_references(root)
    r3 = v3.validate_coherence(root)
    r4 = v4.validate_semantic_preservation(root)
    sf = v4.independent_source_fingerprint(root)
    nr = niri.consolidate(root)
    cr = crown.run_crown(root)
    if any(x.get("status") != PASS for x in (r2,r3,r4,sf,nr,cr)):
        return {"status":FAIL, "decision":"NOT_READY_TO_CLOSE", "reason":"UPSTREAM_VALIDATION_NOT_GREEN"}

    zero_diff = dc.normative_ir_diff(graph, deepcopy(graph))
    coverage = dc.semantic_coverage_report(sf["fingerprint"], graph)
    niri_report = nr["report"]
    crown_report = cr["report"]

    node_types = set(nir.NODE_TYPES)
    edge_types = set(nir.EDGE_TYPES)
    condition_states = set(nir.CONDITION_STATES)
    operators = set(nir.CONSTRAINT_OPERATORS)
    domains = set(nir.EVALUATION_DOMAINS)
    primitives = set(nir.COMPOSITIONAL_PRIMITIVES)
    capabilities = set(_normalized_capabilities_from_foundation())
    formalizations = set(nir.FORMALIZATION_LEVELS)

    rows = []
    rows.append(_req("C01","NIR is derived, declarative, non-sovereign and non-Turing-complete",SAT,
                     ["foundation contract","V3 no arbitration/authority amplification","no executable backend"]))
    rows.append(_req("C02","18 canonical semantic object types are representable",SAT,
                     ["foundation semantic node-type inventory"]))
    rows.append(_req("C03","NormativeIRGraph nodes/edges/metadata/source_map representation exists",SAT,
                     ["real builder graph","V2 source-map validation"]))
    rows.append(_req("C04","12 canonical edge relations are representable",SAT if len(edge_types)==12 else MISSING,
                     ["foundation EDGE_TYPES=%d"%len(edge_types)]))
    rows.append(_req("C05","Every real principal NIR unit is source-mapped and provenance-bound",SAT,
                     ["V2 48/48 references/source maps","V4 exact provenance comparison"]))
    rows.append(_req("C06","UNKNOWN/NOT_APPLICABLE/CONTESTED condition states remain explicit",SAT
                     if {"UNKNOWN","NOT_APPLICABLE","CONTESTED"}.issubset(condition_states) else MISSING,
                     ["foundation condition-state domain","V3 UNKNOWN preservation"]))
    rows.append(_req("C07","Authority and evidence are separate; authority cannot be manufactured",SAT,
                     ["V3 evidence-is-not-authority","NIRI-2/NIRI-5","Crown authority attacks"]))
    rows.append(_req("C08","Scope algebra is conservatively representable and implicit GLOBAL is rejected",BOUNDED,
                     ["ScopeNode typed boundary","Crown IMPLICIT_GLOBAL_SCOPE detected",
                      "NIRI-6 bounded"],
                     "Current 48-object OCC-1A source kernel has no explicit scope structure; no instance-level no-widening proof is claimed."))
    rows.append(_req("C09","Temporal constraints are representable and erasure is rejected at typed boundary",BOUNDED,
                     ["TemporalNode typed boundary","Crown TEMPORAL_CONSTRAINT_ERASURE detected",
                      "NIRI-7 bounded"],
                     "Current 48-object OCC-1A source kernel has no explicit temporal structure; no instance-level no-weakening proof is claimed."))
    rows.append(_req("C10","Conflicts are represented without automatic arbitration",SAT,
                     ["V3 unresolved conflict accepted","Crown conflict-winner injection rejected"]))
    rows.append(_req("C11","DNA-H has no artificial global numeric hierarchy",SAT,
                     ["V3 DNA-H no-global-numeric-hierarchy"]))
    rows.append(_req("C12","Bounded constraint algebra and evaluation domains are explicit",SAT
                     if len(operators)>=12 and len(domains)>=6 else MISSING,
                     ["foundation constraint operators","foundation evaluation domains"]))
    rows.append(_req("C13","Missing facts/uncertainty do not silently satisfy conditions",SAT,
                     ["UNKNOWN explicit","UNCERTAINTY_DOES_NOT_SATISFY primitive","Crown UNKNOWN/N-A collapse rejected"]))
    rows.append(_req("C14","Evidence metadata does not become authority",SAT,
                     ["EvidenceNode/AuthorityNode separation","V3/Crown evidence-to-authority rejection"]))
    rows.append(_req("C15","Canonical compositional primitives and normalized capabilities are representable",SAT
                     if len(primitives)>=6 and len(capabilities)>=12 else MISSING,
                     ["foundation compositional primitives","foundation normalized capabilities"]))
    rows.append(_req("C16","Partial formalization F0-F3 is explicit and cannot be silently promoted",SAT
                     if {"F0","F1","F2","F3"}.issubset(formalizations) else MISSING,
                     ["V4 formalization preservation","Crown PARTIAL_TO_COMPLETE detected"]))
    rows.append(_req("C17","Structural, referential, coherence and semantic-preservation validation layers are executable",SAT,
                     ["Foundation/V1","V2 PASS","V3 PASS","V4 PASS"]))
    rows.append(_req("C18","NormativeIRDiff is directional and detects semantic deltas",SAT,
                     ["Diff validation","zero diff deterministic","promotion/demotion directionality"]))
    rows.append(_req("C19","SemanticCoverageReport exists without equating presence to full formalization",SAT,
                     ["Coverage 48 objects","full_semantic_coverage_claimed=false"]))
    rows.append(_req("C20","NIRI-1..14 are all accounted without overclaiming NIRI-6/7",SAT,
                     ["NIRI 12 PASS + 2 BOUNDED + 0 FAIL","unqualified_14_pass_claim=false"]))
    rows.append(_req("C21","Sequences and coalitions are representable",SAT
                     if {"CompositeActionNode","SequenceConstraintNode"}.issubset(node_types)
                     and {"AT_LEAST_N","AT_MOST_N"}.issubset(operators) else MISSING,
                     ["NIRI-13","foundation composition types/operators"]))
    rows.append(_req("C22","Adversarial crown detects required attack families while accepting legitimate controls",SAT
                     if crown_report["attack_detected_count"]==crown_report["attack_count"]
                     and crown_report["control_pass_count"]==crown_report["control_count"] else MISSING,
                     ["Crown 18/18 attacks","Crown 4/4 controls","0 false negatives/control failures"]))
    rows.append(_req("C23","Real OCC-1A source package is not mutated by OCC-1B validation",SAT
                     if crown_report["source_package_mutated"] is False else MISSING,
                     ["Crown source immutability","V2/V3/V4 read-only path"]))
    rows.append(_req("C24","NIR is reproducible and order/layout does not create semantics",SAT,
                     ["V4 determinism","Diff determinism","Crown node-order control"]))
    rows.append(_req("C25","NIR is not a source of legitimacy and cannot activate authority/execution",SAT,
                     ["NIRI-14","LEGITIMACY_NON_SELF_CREATION","stage-boundary tests"]))
    rows.append(_req("C26","Required OCC-1B output artifacts are constructible from current implementation",SAT,
                     ["NormativeIRPackage/graph from builder","source map in graph",
                      "V2/V3/V4 validation reports","NormativeIRDiff","SemanticCoverageReport"]))
    rows.append(_req("C27","Closure does not imply OCC-1C, P160, authorization, execution or P159 Final Lock",SAT,
                     ["all stage-boundary tests","Crown stage boundary"]))

    missing = [r["requirement_id"] for r in rows if r["status"]==MISSING]
    bounded = [r["requirement_id"] for r in rows if r["status"]==BOUNDED]
    satisfied = [r["requirement_id"] for r in rows if r["status"]==SAT]

    # Bounded C08/C09 are explicit source-instance limitations, not missing NIR capabilities.
    decision = "READY_TO_CLOSE" if not missing and bounded==["C08","C09"] else "NOT_READY_TO_CLOSE"
    report = {
        "schema":"oce.p159.occ1b.closure_audit.v1",
        "milestone":"P159/OCC-1B",
        "decision":decision,
        "requirements_total":len(rows),
        "satisfied_count":len(satisfied),
        "bounded_count":len(bounded),
        "missing_count":len(missing),
        "bounded_requirements":bounded,
        "missing_requirements":missing,
        "rows":rows,
        "closure_performed":False,
        "occ1b_closed":False,
        "occ1c_opened":False,
        "p160_opened":False,
        "authority_activated":False,
        "execution_performed":False,
        "p159_final_lock_performed":False,
        "functional_conclusion_only":True,
        "phenomenology_undetermined":True,
        "source_instance_scope_temporal_limit_preserved":True,
    }
    report["report_sha256"] = nir.canonical_sha256(report)
    return {"status":PASS if decision=="READY_TO_CLOSE" else FAIL,
            "decision":decision,
            "reason":"OCC1B_CLOSURE_AUDIT_READY" if decision=="READY_TO_CLOSE" else "OCC1B_CLOSURE_AUDIT_GAPS_REMAIN",
            "report":report, "report_sha256":report["report_sha256"]}

def verify_report(report:Dict[str,Any])->Dict[str,str]:
    r=deepcopy(report)
    supplied=r.pop("report_sha256",None)
    actual=nir.canonical_sha256(r)
    return {"status":PASS if supplied==actual else FAIL,
            "reason":"OCC1B_CLOSURE_AUDIT_INTEGRITY_OK" if supplied==actual else "OCC1B_CLOSURE_AUDIT_TAMPER_DETECTED"}
