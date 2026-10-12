from __future__ import annotations
from pathlib import Path
from copy import deepcopy
from ontology import occ_semantic_binding as semantic
from ontology import occ_source_lineage_binding as lineage

PRIMITIVE="occ_l0_governed_kernel_representation_proof"
VERSION="P159-OCC1A-l0-governed-kernel-representation-proof-v1"
PRESERVE="PRESERVE_EXISTING_L0_IN_KERNEL"
ORDINARY_ADOPT="ORDINARY_ADOPT_L0"
AMEND="AMEND_L0"
REMOVE_OR_WEAKEN="REMOVE_OR_WEAKEN_L0"
ALLOWED="L0_REPRESENTATION_IN_KERNEL_PERMITTED"
REFOUNDING="REFOUNDING_OR_FORK_REQUIRED"
REJECT="ORDINARY_L0_ADOPTION_FORBIDDEN"

def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"

def canonical_l0(root=None):
    r=_root(root)
    sm=semantic.manifest(r)
    lm=lineage.manifest(r)
    lb={x["canonical_id"]:x for x in lm["lineages"]}
    rows=[]
    for b in sm["bindings"]:
        if not b["canonical_id"].startswith("DNA.L0."): continue
        l=lb.get(b["canonical_id"],{})
        rows.append({
          "canonical_id":b["canonical_id"],
          "binding_status":b.get("binding_status"),
          "text":b.get("text"),
          "source_object_id":b.get("source_object_id"),
          "evidence_ids":tuple(b.get("evidence_ids") or ()),
          "proposal_hash":b.get("proposal_hash"),
          "formalization":b.get("formalization"),
          "lineage_verifiable":l.get("lineage_verifiable") is True,
          "lineage_artifacts":tuple(
              (a.get("path"),a.get("sha256")) for a in l.get("artifacts",())
          ),
          "runtime_authority_granted":False})
    return tuple(rows)

def evaluate(operation, candidate_rows=None, root=None):
    base=canonical_l0(root)
    candidate=tuple(deepcopy(candidate_rows if candidate_rows is not None else base))
    if operation==ORDINARY_ADOPT:
        return {"decision":REJECT,"permitted":False,"requires_refounding_or_fork":False,
                "reason":"DNA-L0 cannot be ordinary-adopted."}
    if operation in (AMEND,REMOVE_OR_WEAKEN):
        return {"decision":REFOUNDING,"permitted":False,"requires_refounding_or_fork":True,
                "reason":"Changing, removing or weakening DNA-L0 is not kernel representation."}
    if operation!=PRESERVE:
        return {"decision":"UNSUPPORTED_OPERATION","permitted":False,
                "requires_refounding_or_fork":False}
    if len(base)!=6 or len(candidate)!=6:
        return {"decision":"L0_REPRESENTATION_REJECTED","permitted":False,
                "requires_refounding_or_fork":False,"reason":"Exactly six canonical L0 objects required."}
    b={x["canonical_id"]:x for x in base}
    c={x["canonical_id"]:x for x in candidate}
    if set(b)!=set(c):
        return {"decision":"L0_REPRESENTATION_REJECTED","permitted":False,
                "requires_refounding_or_fork":False,"reason":"Canonical L0 ID set changed."}
    immutable=("binding_status","text","source_object_id","evidence_ids","proposal_hash",
               "formalization","lineage_verifiable","lineage_artifacts")
    drift=[]
    for cid in sorted(b):
        for k in immutable:
            if b[cid].get(k)!=c[cid].get(k): drift.append(cid+":"+k)
        if c[cid].get("binding_status")!="PROTECTED_CONSTITUTIVE_BINDING_NOT_ORDINARY_ADOPTION":
            drift.append(cid+":constitutional_status")
        if c[cid].get("lineage_verifiable") is not True:
            drift.append(cid+":lineage")
        if c[cid].get("runtime_authority_granted") is not False:
            drift.append(cid+":authority_expansion")
    if drift:
        return {"decision":"L0_REPRESENTATION_REJECTED","permitted":False,
                "requires_refounding_or_fork":False,"drift":sorted(set(drift)),
                "reason":"Representation is not identity-preserving."}
    return {"decision":ALLOWED,"permitted":True,"requires_refounding_or_fork":False,
            "represented_count":6,"semantic_identity_preserved":True,
            "source_lineage_preserved":True,"constitutional_status_preserved":True,
            "ordinary_adoption_performed":False,"amendment_performed":False,
            "weakening_performed":False,"authority_expansion":False,
            "package_population_performed":False,"execution_performed":False}

def proof(root=None):
    nominal=evaluate(PRESERVE,root=root)
    return {"primitive":PRIMITIVE,"version":VERSION,
      "decision":nominal["decision"],"represented_count":nominal.get("represented_count",0),
      "l0_kernel_representation_permitted":nominal.get("permitted",False),
      "refounding_or_fork_triggered":nominal.get("requires_refounding_or_fork",False),
      "package_population_performed":False,"package_state_changed":False,
      "authority_activated":False,"execution_performed":False,
      "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,
      "functional_conclusion_only":True,"phenomenology_undetermined":True}
