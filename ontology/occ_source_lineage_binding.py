from __future__ import annotations
from pathlib import Path
import hashlib, json
from ontology import occ_semantic_binding as semantic

PRIMITIVE="occ_source_lineage_binding"
VERSION="P159-OCC1A-source-lineage-binding-v1"
STATUS="SOURCE_LINEAGE_48_VERIFIABLE_PACKAGE_NOT_POPULATED"
TARGETS=semantic.TARGETS

def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _inside(root,p):
    try: Path(p).resolve().relative_to(root.resolve()); return True
    except Exception: return False

def _artifact(root, rel):
    p=root/rel
    if not p.is_file(): return {"path":rel,"exists":False,"sha256":None}
    if not _inside(root,p): return {"path":rel,"exists":False,"sha256":None}
    return {"path":rel,"exists":True,"sha256":_sha(p)}

def lineage_table(root=None):
    r=_root(root)
    sm=semantic.manifest(r)
    rows=[]
    for b in sm["bindings"]:
        cid=b["canonical_id"]
        arts=[]
        def add(rel):
            if rel and rel not in [x["path"] for x in arts]: arts.append(_artifact(r,rel))
        add(b.get("source_path"))
        add(b.get("historical_source_path"))
        add(b.get("adoption_evidence_path"))
        # Genesis provenance remains conceptual/human-interpreted: lineage to source
        # is verifiable, but no machine text/formal semantics are inferred.
        if cid=="GENESIS.G0":
            kind="GENESIS_CONCEPTUAL_SOURCE_LINEAGE"
            ancestry=("GENESIS.G0","P155_GENESIS_CONCEPTUAL_SOURCE")
        elif cid.startswith("DNA."):
            kind="DNA_GOVERNED_SOURCE_LINEAGE"
            ancestry=(cid,)+tuple(b.get("evidence_ids") or ())
        else:
            kind="CCAD_DIRECT_CANONICAL_SOURCE_LINEAGE"
            ancestry=(cid,b.get("source_object_id"))
        valid=bool(arts) and all(a["exists"] and a["sha256"] for a in arts) and bool(b.get("source_object_id"))
        rows.append({
          "canonical_id":cid,"lineage_kind":kind,"semantic_binding_status":b["binding_status"],
          "source_object_id":b.get("source_object_id"),"ancestry":ancestry,
          "artifacts":tuple(arts),"lineage_verifiable":valid,
          "machine_formalization_claimed":False if cid=="GENESIS.G0" else b.get("formalization")!="F0_HUMAN_INTERPRETIVE",
          "runtime_authority_granted":False,"execution_enabled":False})
    return tuple(rows)

def manifest(root=None):
    r=_root(root); rows=lineage_table(r)
    unresolved=[x["canonical_id"] for x in rows if not x["lineage_verifiable"]]
    g=next(x for x in rows if x["canonical_id"]=="GENESIS.G0")
    return {
      "primitive":PRIMITIVE,"version":VERSION,"status":STATUS,"target_count":48,
      "lineage_verified_count":48-len(unresolved),"unresolved_lineage_ids":unresolved,
      "source_lineage_resolved":not unresolved,
      "genesis_lineage_verified":g["lineage_verifiable"],
      "genesis_machine_formalization_claimed":g["machine_formalization_claimed"],
      "lineages":rows,
      "package_population_performed":False,"package_state_changed":False,
      "authority_activated":False,"execution_performed":False,
      "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,
      "functional_conclusion_only":True,"phenomenology_undetermined":True}
