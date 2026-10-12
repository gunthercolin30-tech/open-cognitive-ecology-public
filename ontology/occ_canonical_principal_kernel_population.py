from __future__ import annotations
from pathlib import Path
from copy import deepcopy
import hashlib, json, os, shutil, tempfile
from ontology import occ_semantic_binding as semantic
from ontology import occ_source_lineage_binding as lineage
from ontology import occ_l0_governed_kernel_representation_proof as l0proof

PRIMITIVE="occ_canonical_principal_kernel_population"
VERSION="P159-OCC1A-canonical-principal-kernel-population-v1.1"
EXPECTED_IDS=tuple(semantic.TARGETS)
PARTITIONS={
 "GENESIS.":"genesis/genesis.yaml",
 "DNA.H":"dna/dna_h.yaml",
 "DNA.L0.":"dna/dna_l0.yaml",
 "DNA.L1.":"dna/dna_l1.yaml",
 "CCAD.P":"ccad/ccad_principles.yaml",
 "CCAD.AR":"ccad/ccad_arbitration_rules.yaml",
}
MANIFEST_REL="normative/occ1a/manifest.yaml"

def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"
def _sha_bytes(b): return hashlib.sha256(b).hexdigest()
def _json_bytes(x): return (json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(",",":"))+"\n").encode()
def _partition(cid):
    for p,r in PARTITIONS.items():
        if cid.startswith(p): return r
    raise ValueError("NO_PARTITION:"+cid)

def build_kernel(root=None):
    r=_root(root); sm=semantic.manifest(r); lm=lineage.manifest(r)
    if not sm.get("semantic_disposition_complete"): raise RuntimeError("SEMANTIC_BINDING_NOT_COMPLETE")
    if not lm.get("source_lineage_resolved") or lm.get("lineage_verified_count")!=48:
        raise RuntimeError("SOURCE_LINEAGE_NOT_COMPLETE")
    lp=l0proof.proof(r)
    if not lp.get("l0_kernel_representation_permitted"): raise RuntimeError("L0_REPRESENTATION_NOT_PROVEN")
    lb={x["canonical_id"]:x for x in lm["lineages"]}
    objs=[]
    for b in sm["bindings"]:
        cid=b["canonical_id"]; l=lb[cid]
        obj={
          "canonical_id":cid,
          "semantic_status":b["binding_status"],
          "text":b.get("text"),
          "source_object_id":b.get("source_object_id"),
          "evidence_ids":list(b.get("evidence_ids") or ()),
          "formalization":b.get("formalization"),
          "lineage_kind":l["lineage_kind"],
          "lineage_artifacts":[{"path":a["path"],"sha256":a["sha256"]} for a in l["artifacts"]],
          "runtime_authority_granted":False,
          "execution_enabled":False,
        }
        if cid=="GENESIS.G0":
            if obj["text"] is not None: raise RuntimeError("GENESIS_TEXT_INVENTION")
            obj["machine_formalization_claimed"]=False
        if cid.startswith("DNA.L0."):
            if obj["semantic_status"]!="PROTECTED_CONSTITUTIVE_BINDING_NOT_ORDINARY_ADOPTION":
                raise RuntimeError("L0_STATUS_DRIFT:"+cid)
            obj["ordinary_adoption_performed"]=False
            obj["refounding_or_fork_rule_preserved"]=True
        objs.append(obj)
    ids=[x["canonical_id"] for x in objs]
    if len(ids)!=48 or len(set(ids))!=48 or set(ids)!=set(EXPECTED_IDS):
        raise RuntimeError("KERNEL_IDENTITY_SET_INVALID")
    return tuple(sorted(objs,key=lambda x:x["canonical_id"]))

def plan(root=None):
    objs=build_kernel(root)
    groups={v:[] for v in PARTITIONS.values()}
    for o in objs: groups[_partition(o["canonical_id"])].append(o)
    payloads={}
    for rel,rows in groups.items():
        payload={"schema":"oce.p159.occ1a.principal_partition.v1",
                 "population_status":"POPULATED_EXPLICIT_SEMANTICS",
                 "norms":rows}
        payloads["normative/occ1a/"+rel]=_json_bytes(payload)
    return payloads

def verify_plan(payloads):
    allrows=[]
    for rel,b in payloads.items():
        d=json.loads(b.decode()); allrows.extend(d["norms"])
    ids=[x["canonical_id"] for x in allrows]
    if len(ids)!=48 or len(set(ids))!=48 or set(ids)!=set(EXPECTED_IDS): return False
    g=next(x for x in allrows if x["canonical_id"]=="GENESIS.G0")
    if g["text"] is not None or g.get("machine_formalization_claimed") is not False: return False
    l0=[x for x in allrows if x["canonical_id"].startswith("DNA.L0.")]
    if len(l0)!=6 or any(x["semantic_status"]!="PROTECTED_CONSTITUTIVE_BINDING_NOT_ORDINARY_ADOPTION" for x in l0): return False
    if any(x.get("runtime_authority_granted") or x.get("execution_enabled") for x in allrows): return False
    return True

def commit(root=None, fail_before_replace=False):
    r=_root(root); payloads=plan(r)
    if not verify_plan(payloads): raise RuntimeError("STAGING_VERIFY_FAILED")
    targets={r/rel:data for rel,data in payloads.items()}
    # Back up every target before any replacement.
    for p in targets:
        if not p.is_file(): raise RuntimeError("TARGET_MISSING:"+str(p))
    backups={p:p.read_bytes() for p in targets}
    staged={}
    try:
        for p,data in targets.items():
            fd,tmp=tempfile.mkstemp(prefix=p.name+".stage.",dir=str(p.parent))
            os.close(fd); tp=Path(tmp); tp.write_bytes(data)
            with tp.open("rb") as f: os.fsync(f.fileno())
            staged[p]=tp
        if fail_before_replace: raise RuntimeError("INJECTED_PRECOMMIT_FAILURE")
        # Replace all partitions; rollback from in-memory exact bytes on any failure.
        for p,tp in staged.items(): os.replace(str(tp),str(p))
        # Independent disk re-read.
        disk={str(p.relative_to(r)):p.read_bytes() for p in targets}
        if not verify_plan(disk): raise RuntimeError("POSTCOMMIT_VERIFY_FAILED")
    except Exception:
        for p,b in backups.items():
            p.write_bytes(b)
        for tp in staged.values():
            if tp.exists(): tp.unlink()
        raise
    # Manifest deliberately remains DRAFT and is not mutated in v1.
    return {"decision":"CANONICAL_PRINCIPAL_KERNEL_POPULATION_COMMITTED",
      "populated_count":48,"partition_count":len(targets),
      "partition_sha256":{str(p.relative_to(r)):_sha_bytes(p.read_bytes()) for p in targets},
      "package_state_changed":False,"package_state_expected":"DRAFT",
      "authority_activated":False,"execution_performed":False,
      "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False}

def inspect_disk(root=None):
    r=_root(root); payloads={}
    for rel in ("genesis/genesis.yaml","dna/dna_h.yaml","dna/dna_l0.yaml","dna/dna_l1.yaml",
                "ccad/ccad_principles.yaml","ccad/ccad_arbitration_rules.yaml"):
        p=r/"normative/occ1a"/rel
        if not p.is_file(): return {"valid":False,"reason":"MISSING:"+rel}
        payloads["normative/occ1a/"+rel]=p.read_bytes()
    return {"valid":verify_plan(payloads),"populated_count":48 if verify_plan(payloads) else 0}
