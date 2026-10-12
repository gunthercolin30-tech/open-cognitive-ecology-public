from __future__ import annotations
from pathlib import Path
import json, hashlib
from ontology import occ_semantic_binding as semantic
from ontology import occ_source_lineage_binding as lineage

PRIMITIVE="occ1a_post_lineage_exit_reaudit"
VERSION="P159-OCC1A-post-lineage-exit-reaudit-v1"
HISTORICAL_BLOCKERS=(
 "6_DNA_L0_REQUIRE_REFOUNDING_OR_FORK_PATH",
 "CANONICAL_PACKAGE_PRINCIPAL_KERNEL_NOT_POPULATED",
 "CANONICAL_PACKAGE_STATE_DRAFT",
 "KERNEL_SEMANTIC_BINDING_STILL_UNRESOLVED",
 "SOURCE_LINEAGE_BINDING_STILL_UNRESOLVED",
)

def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"

def _load_yaml_minimal(path):
    # Audit only needs explicit scalar/list facts from the package manifest.
    # Prefer PyYAML when present; otherwise use conservative textual checks.
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {"__raw__": path.read_text(encoding="utf-8",errors="replace")}

def _manifest_facts(root):
    p=root/"normative/occ1a/manifest.yaml"
    if not p.is_file():
        return {"exists":False,"package_state":None,"kernel_population_status":None}
    d=_load_yaml_minimal(p)
    raw=d.get("__raw__","")
    def scalar(key):
        if raw:
            for ln in raw.splitlines():
                s=ln.strip()
                if s.startswith(key+":"):
                    return s.split(":",1)[1].strip().strip("'\"")
            return None
        return d.get(key)
    return {"exists":True,"package_state":scalar("package_state"),
            "kernel_population_status":scalar("kernel_population_status")}

def audit(root=None):
    r=_root(root)
    sm=semantic.manifest(r)
    lm=lineage.manifest(r)
    pf=_manifest_facts(r)
    semantic_ok=(sm.get("semantic_disposition_complete") is True
                 and sm.get("unresolved_ids")==[])
    lineage_ok=(lm.get("source_lineage_resolved") is True
                and lm.get("unresolved_lineage_ids")==[]
                and lm.get("lineage_verified_count")==48)
    # Physical package facts remain authoritative for population/state.
    package_populated=(pf.get("kernel_population_status") in
                       ("POPULATED","COMPLETE","POPULATED_COMPLETE"))
    package_not_draft=(pf.get("package_state") not in (None,"DRAFT"))
    statuses={}
    statuses["KERNEL_SEMANTIC_BINDING_STILL_UNRESOLVED"] = (
        "RESOLVED_BY_CURRENT_EVIDENCE" if semantic_ok else "STILL_BLOCKING")
    statuses["SOURCE_LINEAGE_BINDING_STILL_UNRESOLVED"] = (
        "RESOLVED_BY_CURRENT_EVIDENCE" if lineage_ok else "STILL_BLOCKING")
    statuses["CANONICAL_PACKAGE_PRINCIPAL_KERNEL_NOT_POPULATED"] = (
        "RESOLVED_BY_CURRENT_EVIDENCE" if package_populated else "STILL_BLOCKING")
    statuses["CANONICAL_PACKAGE_STATE_DRAFT"] = (
        "RESOLVED_BY_CURRENT_EVIDENCE" if package_not_draft else "STILL_BLOCKING")

    # Critical conservative conclusion:
    # The specialized evidence proves the six L0 have explicit protected
    # constitutive semantic bindings and verifiable lineage, but it does NOT
    # prove that OCC-1A may erase the constitutional REFOUNDING_OR_FORK rule.
    # Therefore this audit cannot silently classify that blocker as resolved.
    l0=[b for b in sm.get("bindings",[]) if b["canonical_id"].startswith("DNA.L0.")]
    l0_repr=(len(l0)==6 and all(
        b.get("binding_status")=="PROTECTED_CONSTITUTIVE_BINDING_NOT_ORDINARY_ADOPTION"
        for b in l0))
    statuses["6_DNA_L0_REQUIRE_REFOUNDING_OR_FORK_PATH"] = (
        "REFORMULATED_REQUIRES_GOVERNED_KERNEL_REPRESENTATION_PROOF"
        if l0_repr else "STILL_BLOCKING")

    remaining=[k for k,v in statuses.items() if v!="RESOLVED_BY_CURRENT_EVIDENCE"]
    return {
      "primitive":PRIMITIVE,"version":VERSION,
      "decision":"OCC1A_REMAINS_OPEN" if remaining else "OCC1A_EXIT_CANDIDATE",
      "historical_blocker_count":5,"blocker_status":statuses,
      "resolved_blocker_count":sum(v=="RESOLVED_BY_CURRENT_EVIDENCE" for v in statuses.values()),
      "remaining_blockers":sorted(remaining),
      "semantic_evidence_valid":semantic_ok,"source_lineage_evidence_valid":lineage_ok,
      "l0_protected_constitutive_representation_available":l0_repr,
      "l0_refounding_or_fork_requirement_erased":False,
      "package_population_performed":False,"package_state_changed":False,
      "authority_activated":False,"execution_performed":False,
      "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,
      "functional_conclusion_only":True,"phenomenology_undetermined":True,
      "package_facts":pf}

def write_report(root=None, *, evidence_bridge=None, evidence_decision=None,
                 parent_create_filesystem_context=None, parent_create_filesystem_contexts=None):
    r=_root(root)
    a=audit(r)
    p=r/"oif_review/campaigns/P159-OCC1A/occ1a_post_lineage_exit_reaudit_v1.json"
    if evidence_bridge is None or evidence_decision is None:
        raise RuntimeError("governed_evidence_context_required")
    filesystem_context=getattr(evidence_bridge,"filesystem_context",None)
    bridge_root_value=getattr(filesystem_context,"root_path",None)
    if bridge_root_value is None:
        raise RuntimeError("governed_evidence_filesystem_root_required")
    bridge_root=Path(bridge_root_value).expanduser().resolve()
    try:
        rel=p.resolve().relative_to(bridge_root).as_posix()
    except ValueError as exc:
        raise RuntimeError("governed_evidence_target_outside_root") from exc

    missing=[]
    cursor=p.parent
    while cursor != bridge_root and not cursor.exists():
        missing.append(cursor)
        cursor=cursor.parent
    if cursor != bridge_root and not cursor.exists():
        raise RuntimeError("governed_filesystem_parent_chain_outside_root")
    missing.reverse()

    supplied=[]
    if parent_create_filesystem_contexts is not None:
        supplied=list(parent_create_filesystem_contexts)
    elif parent_create_filesystem_context is not None:
        supplied=[parent_create_filesystem_context]

    if missing:
        if len(supplied) != len(missing):
            raise RuntimeError(
                "governed_filesystem_parent_create_context_cardinality_required:"+
                str(len(missing))+":"+str(len(supplied))
            )
        if any(ctx is filesystem_context for ctx in supplied):
            raise RuntimeError("distinct_governed_filesystem_parent_create_context_required:occ1a_report")
        if len({id(ctx) for ctx in supplied}) != len(supplied):
            raise RuntimeError("unique_governed_filesystem_parent_create_contexts_required:occ1a_report")
        for idx,(directory,ctx) in enumerate(zip(missing,supplied)):
            ctx.execute_path(
                slot="occ1a_report_parent_"+str(idx),
                operation_id="FS_CREATE_DIR",
                path=directory,
            )
    elif supplied:
        raise RuntimeError("unused_governed_filesystem_parent_create_contexts:occ1a_report")

    payload=(json.dumps(a,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode("utf-8")
    effect_result=evidence_bridge.execute_path(
        decision=evidence_decision,
        evidence_role=evidence_decision.evidence_role,
        slot="occ1a_report_write",
        operation_id="FS_WRITE_REPLACE_BYTES",
        path=rel,
        payload=payload,
    )
    if not isinstance(effect_result,dict) or effect_result.get("status")!="EVIDENCE_EFFECT_CONFIRMED":
        raise RuntimeError(
            "governed_evidence_effect_not_confirmed:"+
            str(effect_result.get("status") if isinstance(effect_result,dict) else None)
        )
    return p,a
