from __future__ import annotations
from pathlib import Path
import hashlib, json
from ontology import occ_canonical_principal_kernel_population as population
from ontology import occ_semantic_binding as semantic
from ontology import occ_source_lineage_binding as lineage

PRIMITIVE="occ_postcommit_population_verifier"
VERSION="P159-OCC1A-postcommit-population-verifier-v1.2"

PARTITIONS=(
 "normative/occ1a/genesis/genesis.yaml",
 "normative/occ1a/dna/dna_h.yaml",
 "normative/occ1a/dna/dna_l0.yaml",
 "normative/occ1a/dna/dna_l1.yaml",
 "normative/occ1a/ccad/ccad_principles.yaml",
 "normative/occ1a/ccad/ccad_arbitration_rules.yaml",
)

def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def _load_structured(path):
    text=Path(path).read_text(encoding="utf-8")
    try:
        return json.loads(text), "JSON"
    except Exception:
        try:
            import yaml
            return yaml.safe_load(text), "YAML"
        except Exception as e:
            return None, "UNPARSEABLE:"+type(e).__name__

def _find_key(obj,key):
    found=[]
    def walk(x,path=()):
        if isinstance(x,dict):
            for k,v in x.items():
                np=path+(str(k),)
                if str(k)==key: found.append((np,v))
                walk(v,np)
        elif isinstance(x,list):
            for i,v in enumerate(x): walk(v,path+(str(i),))
    walk(obj)
    return found

def verify(root=None):
    r=_root(root)
    manifest=r/"normative/occ1a/manifest.yaml"
    if not manifest.is_file(): raise RuntimeError("MANIFEST_MISSING")
    before={rel:_sha(r/rel) for rel in PARTITIONS}
    manifest_sha=_sha(manifest)

    # Independent physical reread of the six committed partitions.
    payloads={}
    for rel in PARTITIONS:
        p=r/rel
        if not p.is_file(): raise RuntimeError("PARTITION_MISSING:"+rel)
        payloads[rel]=p.read_bytes()
    if not population.verify_plan(payloads):
        raise RuntimeError("PHYSICAL_48_REVERIFY_FAILED")

    rows=[]
    for b in payloads.values():
        d=json.loads(b.decode("utf-8"))
        rows.extend(d["norms"])
    ids=[x["canonical_id"] for x in rows]
    if len(ids)!=48 or len(set(ids))!=48:
        raise RuntimeError("PHYSICAL_ID_SET_INVALID")

    # Rebuild expected population from current validated semantic+lineage evidence.
    expected=population.plan(r)
    expected_sha={rel:hashlib.sha256(data).hexdigest() for rel,data in expected.items()}
    disk_sha={rel:_sha(r/rel) for rel in PARTITIONS}
    if expected_sha!=disk_sha:
        raise RuntimeError("DISK_VS_VALIDATED_EVIDENCE_DRIFT")

    # Semantic / lineage evidence remains complete.
    sm=semantic.manifest(r); lm=lineage.manifest(r)
    if not sm.get("semantic_disposition_complete"):
        raise RuntimeError("SEMANTIC_EVIDENCE_NOT_COMPLETE")
    if not lm.get("source_lineage_resolved") or lm.get("lineage_verified_count")!=48:
        raise RuntimeError("LINEAGE_EVIDENCE_NOT_COMPLETE")

    # Manifest: parse structurally; never rely on literal formatting.
    md,fmt=_load_structured(manifest)
    if not isinstance(md,dict): raise RuntimeError("MANIFEST_NOT_STRUCTURED:"+fmt)
    ps=_find_key(md,"package_state")
    if len(ps)!=1: raise RuntimeError("PACKAGE_STATE_CARDINALITY_INVALID:"+str(len(ps)))
    package_state=ps[0][1]
    if package_state!="DRAFT":
        raise RuntimeError("PACKAGE_STATE_NOT_DRAFT:"+repr(package_state))

    # The historical population status may intentionally still be unresolved until reconciliation.
    kp=_find_key(md,"kernel_population_status")
    kernel_status=kp[0][1] if len(kp)==1 else None

    # Critical boundaries.
    genesis=next(x for x in rows if x["canonical_id"]=="GENESIS.G0")
    if genesis.get("text") is not None or genesis.get("machine_formalization_claimed") is not False:
        raise RuntimeError("GENESIS_BOUNDARY_VIOLATION")
    l0=[x for x in rows if x["canonical_id"].startswith("DNA.L0.")]
    if len(l0)!=6 or any(x.get("semantic_status")!="PROTECTED_CONSTITUTIVE_BINDING_NOT_ORDINARY_ADOPTION" for x in l0):
        raise RuntimeError("L0_BOUNDARY_VIOLATION")
    if any(x.get("runtime_authority_granted") or x.get("execution_enabled") for x in rows):
        raise RuntimeError("AUTHORITY_OR_EXECUTION_WIDENING")

    after={rel:_sha(r/rel) for rel in PARTITIONS}
    if before!=after or manifest_sha!=_sha(manifest):
        raise RuntimeError("VERIFIER_MUTATED_PACKAGE")

    return {
      "decision":"POSTCOMMIT_POPULATION_VERIFIED",
      "physical_population_verified":True,
      "populated_count":48,
      "partition_count":6,
      "disk_matches_validated_evidence":True,
      "semantic_evidence_complete":True,
      "source_lineage_complete":True,
      "package_state":package_state,
      "kernel_population_status_observed":kernel_status,
      "manifest_format":fmt,
      "manifest_sha256":manifest_sha,
      "partition_sha256":disk_sha,
      "genesis_no_invention":True,
      "l0_protection_preserved":True,
      "authority_activated":False,
      "execution_performed":False,
      "package_state_changed":False,
      "manifest_mutated":False,
      "occ1a_closed":False,
      "occ1b_opened":False,
      "p160_opened":False,
      "functional_conclusion_only":True,
      "phenomenology_undetermined":True,
    }
