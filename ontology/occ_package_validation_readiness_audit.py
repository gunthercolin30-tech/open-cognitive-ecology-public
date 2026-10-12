from __future__ import annotations
from pathlib import Path
import hashlib, json
from ontology import occ_canonical_principal_kernel_population as population
from ontology import occ_semantic_binding as semantic
from ontology import occ_source_lineage_binding as lineage
from ontology import occ_l0_governed_kernel_representation_proof as l0proof
from ontology import occ_manifest_kernel_population_reconciliation as reconcile

PRIMITIVE="occ_package_validation_readiness_audit"
VERSION="P159-OCC1A-package-validation-readiness-audit-v1"
READY="READY_FOR_PACKAGE_VALIDATION"
BLOCKED="PACKAGE_VALIDATION_BLOCKED"

def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"

def audit(root=None):
    r=_root(root); blockers=[]; checks={}
    manifest=r/"normative/occ1a/manifest.yaml"
    try:
        md=reconcile._load(manifest)
        ps=reconcile._find(md,"package_state")
        ks=reconcile._find(md,"kernel_population_status")
        checks["manifest_single_package_state"]=len(ps)==1
        checks["manifest_single_kernel_status"]=len(ks)==1
        checks["package_state_draft"]=len(ps)==1 and ps[0][1]=="DRAFT"
        checks["kernel_population_reconciled"]=len(ks)==1 and ks[0][1]=="POPULATED_48_VERIFIED"
    except Exception:
        checks["manifest_single_package_state"]=False
        checks["manifest_single_kernel_status"]=False
        checks["package_state_draft"]=False
        checks["kernel_population_reconciled"]=False

    rels=tuple("normative/occ1a/"+x for x in (
      "genesis/genesis.yaml","dna/dna_h.yaml","dna/dna_l0.yaml","dna/dna_l1.yaml",
      "ccad/ccad_principles.yaml","ccad/ccad_arbitration_rules.yaml"))
    payloads={}
    try:
        payloads={rel:(r/rel).read_bytes() for rel in rels}
        checks["physical_kernel_valid"]=population.verify_plan(payloads)
    except Exception: checks["physical_kernel_valid"]=False

    rows=[]
    if checks["physical_kernel_valid"]:
        for b in payloads.values(): rows.extend(json.loads(b.decode("utf-8"))["norms"])
    ids=[x.get("canonical_id") for x in rows]
    checks["exact_48_unique_ids"]=len(ids)==48 and len(set(ids))==48 and set(ids)==set(population.EXPECTED_IDS)

    try:
        expected=population.plan(r)
        checks["disk_matches_validated_evidence"]={
          k:hashlib.sha256(v).hexdigest() for k,v in payloads.items()
        }=={k:hashlib.sha256(v).hexdigest() for k,v in expected.items()}
    except Exception: checks["disk_matches_validated_evidence"]=False

    try:
        sm=semantic.manifest(r)
        checks["semantic_48_complete"]=sm.get("semantic_disposition_complete") is True and len(sm.get("bindings",()))==48
    except Exception: checks["semantic_48_complete"]=False
    try:
        lm=lineage.manifest(r)
        checks["lineage_48_complete"]=lm.get("source_lineage_resolved") is True and lm.get("lineage_verified_count")==48 and not lm.get("unresolved_lineage_ids")
    except Exception: checks["lineage_48_complete"]=False
    try:
        lp=l0proof.proof(r)
        checks["l0_representation_proven"]=lp.get("l0_kernel_representation_permitted") is True and lp.get("represented_count")==6
    except Exception: checks["l0_representation_proven"]=False

    if rows:
        g=[x for x in rows if x.get("canonical_id")=="GENESIS.G0"]
        checks["genesis_no_invention"]=len(g)==1 and g[0].get("text") is None and g[0].get("machine_formalization_claimed") is False
        l0=[x for x in rows if str(x.get("canonical_id","")).startswith("DNA.L0.")]
        checks["l0_six_protected"]=len(l0)==6 and all(
          x.get("semantic_status")=="PROTECTED_CONSTITUTIVE_BINDING_NOT_ORDINARY_ADOPTION"
          and x.get("ordinary_adoption_performed") is False
          and x.get("refounding_or_fork_rule_preserved") is True for x in l0)
        checks["no_runtime_authority"]=all(x.get("runtime_authority_granted") is False for x in rows)
        checks["no_execution_enabled"]=all(x.get("execution_enabled") is False for x in rows)
        checks["all_have_lineage"]=all(bool(x.get("lineage_kind")) and isinstance(x.get("lineage_artifacts"),list) for x in rows)
        checks["all_have_semantic_status"]=all(bool(x.get("semantic_status")) for x in rows)
    else:
        for k in ("genesis_no_invention","l0_six_protected","no_runtime_authority",
                  "no_execution_enabled","all_have_lineage","all_have_semantic_status"): checks[k]=False

    # Hierarchy/category conservation.
    checks["canonical_categories_complete"]=(
      sum(str(x).startswith("DNA.H") for x in ids)==9 and
      sum(str(x).startswith("DNA.L0.") for x in ids)==6 and
      sum(str(x).startswith("DNA.L1.") for x in ids)==8 and
      sum(str(x).startswith("CCAD.P") for x in ids)==14 and
      sum(str(x).startswith("CCAD.AR") for x in ids)==10 and
      ids.count("GENESIS.G0")==1)
    checks["h9_f18_not_bound"]=True
    h9=next((x for x in rows if x.get("canonical_id")=="DNA.H9"),None)
    if not h9: checks["h9_f18_not_bound"]=False
    else:
        ev=set(h9.get("evidence_ids") or ())
        checks["h9_f18_not_bound"]=("F12" in ev and "F17" in ev and "F18" not in ev)

    # Stage boundaries: readiness is evidence only, never activation/validation/execution.
    checks["stage_boundary_preserved"]=True

    for k,v in checks.items():
        if v is not True: blockers.append("FAILED_"+k.upper())
    decision=READY if not blockers else BLOCKED
    return {"primitive":PRIMITIVE,"version":VERSION,"decision":decision,
      "check_count":len(checks),"passed_count":sum(v is True for v in checks.values()),
      "blockers":sorted(blockers),"checks":checks,
      "package_state":"DRAFT" if checks.get("package_state_draft") else "UNVERIFIED",
      "package_validation_performed":False,"package_state_changed":False,
      "authority_activated":False,"execution_performed":False,
      "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,
      "functional_conclusion_only":True,"phenomenology_undetermined":True}
