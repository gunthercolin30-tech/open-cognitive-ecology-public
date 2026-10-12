from __future__ import annotations
from pathlib import Path
import hashlib, json
from ontology import occ_postcommit_population_verifier as pv
from ontology import occ_canonical_principal_kernel_population as population
from ontology import occ_semantic_binding as semantic
from ontology import occ_source_lineage_binding as lineage
from ontology import occ_l0_governed_kernel_representation_proof as l0proof

PRIMITIVE="occ_post_validation_independent_audit"
VERSION="P159-OCC1A-post-validation-independent-audit-v1.1"
MANIFEST_REL="normative/occ1a/manifest.yaml"
PASS="POST_VALIDATION_INDEPENDENT_AUDIT_OK"
FAIL="POST_VALIDATION_INDEPENDENT_AUDIT_BLOCKED"
EXPECTED_MANIFEST_SHA256="d9a2635167a8b68fdd72763003abaa0759a4659e9a9b38164dc86aeba3260f8e"
EXPECTED_PARTITIONS={
"normative/occ1a/ccad/ccad_arbitration_rules.yaml":"b5277fa3d371888e79059b71e1606c4e7e22ec3bf7d361f017819dc1c823ba58",
"normative/occ1a/ccad/ccad_principles.yaml":"8b6e8dd2759d139191aa0236f92a2d53ff6e82d62683e696bdf0172277339d19",
"normative/occ1a/dna/dna_h.yaml":"122e0d3828034227789ef1a66249148e4c1ad5b2c0e4fd5c56d67ac7b6d82407",
"normative/occ1a/dna/dna_l0.yaml":"88e1fd081c8d1a5c6dc03ac084f603cf4108b5a0eee662ffc4515f72dd1ef8a4",
"normative/occ1a/dna/dna_l1.yaml":"851304aa98476ce274d793896f2de0db9b9d7bd2e1318ccf9806ca8cb60afd3e",
"normative/occ1a/genesis/genesis.yaml":"7321d1044fbc5d9eb06fe795ebc0acb0780e08e2af4e8c87d6d0a28b38c0d908"}

def _root(root=None): return Path(root) if root else Path.home()/"open-cognitive-ecology"
def _sha(b): return hashlib.sha256(b).hexdigest()
def _structured_bytes(b):
    text=b.decode("utf-8")
    try: return json.loads(text)
    except Exception:
        import yaml
        return yaml.safe_load(text)
def _find(obj,key):
    found=[]
    def walk(x):
        if isinstance(x,dict):
            for k,v in x.items():
                if str(k)==key: found.append(v)
                walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
    walk(obj); return found
def _single(obj,key):
    x=_find(obj,key)
    return x[0] if len(x)==1 else None
def _rows(payloads):
    rows=[]
    for rel in pv.PARTITIONS:
        if rel not in payloads: continue
        d=_structured_bytes(payloads[rel])
        if isinstance(d,dict) and isinstance(d.get("norms"),list): rows.extend(d["norms"])
    return rows

def audit(root=None, manifest_bytes=None, partition_bytes=None):
    r=_root(root)
    mb=manifest_bytes if manifest_bytes is not None else (r/MANIFEST_REL).read_bytes()
    payloads=partition_bytes if partition_bytes is not None else {rel:(r/rel).read_bytes() for rel in pv.PARTITIONS}
    try: md=_structured_bytes(mb)
    except Exception: md=None
    rows=_rows(payloads)
    ids=[x.get("canonical_id") for x in rows if isinstance(x,dict)]
    sm=semantic.manifest(r); lm=lineage.manifest(r); lp=l0proof.proof(r)
    expected_ids=set(population.EXPECTED_IDS)
    genesis=[x for x in rows if x.get("canonical_id")=="GENESIS.G0"]
    l0=[x for x in rows if str(x.get("canonical_id","")).startswith("DNA.L0.")]
    h9=next((x for x in sm.get("bindings",[]) if x.get("canonical_id")=="DNA.H9"),{})
    checks={
      "manifest_parseable":isinstance(md,dict),
      "manifest_hash_pinned":_sha(mb)==EXPECTED_MANIFEST_SHA256,
      "partition_set_exact":set(payloads)==set(EXPECTED_PARTITIONS),
      "partition_hashes_pinned":set(payloads)==set(EXPECTED_PARTITIONS) and all(_sha(payloads[k])==v for k,v in EXPECTED_PARTITIONS.items()),
      "package_state_validated":isinstance(md,dict) and _single(md,"package_state")=="VALIDATED",
      "kernel_status_verified":isinstance(md,dict) and _single(md,"kernel_population_status")=="POPULATED_48_VERIFIED",
      "physical_kernel_valid":set(payloads)==set(EXPECTED_PARTITIONS) and population.verify_plan(payloads),
      "exact_48_unique_canonical_ids":len(ids)==48 and len(set(ids))==48 and set(ids)==expected_ids,
      "semantic_binding_complete":sm.get("semantic_disposition_complete") is True and sm.get("target_count")==48 and sm.get("explicit_disposition_count")==48,
      "source_lineage_complete":lm.get("source_lineage_resolved") is True and lm.get("lineage_verified_count")==48 and lm.get("target_count")==48,
      "l0_representation_proven":lp.get("decision")==l0proof.ALLOWED and lp.get("represented_count")==6 and lp.get("l0_kernel_representation_permitted") is True,
      "l0_protection_preserved":len(l0)==6 and all(x.get("semantic_status")=="PROTECTED_CONSTITUTIVE_BINDING_NOT_ORDINARY_ADOPTION" and x.get("ordinary_adoption_performed") is False and x.get("refounding_or_fork_rule_preserved") is True for x in l0),
      "genesis_no_invention":len(genesis)==1 and genesis[0].get("text") is None and genesis[0].get("machine_formalization_claimed") is False,
      "h9_f12_f17_distinct":sm.get("h9_f12_f17_distinct") is True and tuple(h9.get("evidence_ids") or ())==("F12","F17"),
      "f18_excluded_from_h9":sm.get("f18_bound_to_h9") is False and "F18" not in tuple(h9.get("evidence_ids") or ()),
      "no_row_authority_or_execution":not any(x.get("runtime_authority_granted") or x.get("execution_enabled") for x in rows),
      "occ1b_not_opened":isinstance(md,dict) and _single(md,"occ1b_opened") is False,
      "p160_not_opened":isinstance(md,dict) and _single(md,"p160_opened") is False,
      "functional_only":isinstance(md,dict) and _single(md,"functional_conclusion_only") is True,
      "phenomenology_undetermined":isinstance(md,dict) and _single(md,"phenomenology_undetermined") is True,
    }
    blockers=["FAILED_"+k.upper() for k,v in checks.items() if not v]
    return {"primitive":PRIMITIVE,"version":VERSION,"decision":PASS if not blockers else FAIL,
      "check_count":len(checks),"passed_count":sum(bool(v) for v in checks.values()),"blockers":blockers,"checks":checks,
      "manifest_sha256":_sha(mb),"partition_sha256":{k:_sha(v) for k,v in sorted(payloads.items())},
      "package_state":_single(md,"package_state") if isinstance(md,dict) else None,
      "kernel_population_status":_single(md,"kernel_population_status") if isinstance(md,dict) else None,
      "read_only":True,"package_state_changed":False,"authority_activated":False,"execution_performed":False,
      "occ1a_closed":False,"occ1b_opened":False,"p160_opened":False,
      "functional_conclusion_only":True,"phenomenology_undetermined":True}
