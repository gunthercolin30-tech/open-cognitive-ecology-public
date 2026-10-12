from pathlib import Path
import json, hashlib, importlib.util
try: import yaml
except Exception: yaml=None
ROOT=Path.home()/"open-cognitive-ecology"
OUT=ROOT/"validation_artifacts/p159/occ1k_r9"

def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def y(rel):
    if yaml is None: raise RuntimeError("PyYAML required")
    return yaml.safe_load((ROOT/rel).read_text(encoding="utf-8"))
def source_hash_ok(entry):
    p=ROOT/entry["path"]
    return p.is_file() and sha(p)==entry["sha256"]

def build():
    manifest=y("normative/occ1a/manifest.yaml")
    sources={e["source_id"]:e for e in manifest["source_artifacts"]}
    required=("P156_CCAD","P091_CONSTITUTION_OPERATIONAL","CONSTITUTION_REGISTRY",
              "GOVERNANCE_CONTEXTUAL","HUMAN_RESERVED_AUTHORITY","NORMATIVE_HIERARCHY","P155_ARCHITECTURE")
    integrity={k:source_hash_ok(sources[k]) for k in required}
    semantic_required=tuple(k for k in required if k!="HUMAN_RESERVED_AUTHORITY")
    if not all(integrity[k] for k in semantic_required): raise RuntimeError("CANONICAL_SEMANTIC_SOURCE_HASH_MISMATCH")
    authority_drift = not integrity["HUMAN_RESERVED_AUTHORITY"]

    ccad=(ROOT/sources["P156_CCAD"]["path"]).read_text(encoding="utf-8")
    constitution=(ROOT/sources["P091_CONSTITUTION_OPERATIONAL"]["path"]).read_text(encoding="utf-8")
    registry=(ROOT/sources["CONSTITUTION_REGISTRY"]["path"]).read_text(encoding="utf-8")
    governance=(ROOT/sources["GOVERNANCE_CONTEXTUAL"]["path"]).read_text(encoding="utf-8")
    hierarchy=(ROOT/sources["NORMATIVE_HIERARCHY"]["path"]).read_text(encoding="utf-8")

    candidates={
      "S7.CCAD":[
        {"candidate_id":"S7-C1","source_id":"P156_CCAD","semantic_anchor":"CONFLICT_CLASSES","kind":"CONFLICT_TAXONOMY","adoption_status":"CANDIDATE_ONLY"},
        {"candidate_id":"S7-C2","source_id":"P156_CCAD","semantic_anchor":"PRINCIPLES","kind":"CONFLICT_GOVERNANCE_PRINCIPLES","adoption_status":"CANDIDATE_ONLY"},
        {"candidate_id":"S7-C3","source_id":"NORMATIVE_HIERARCHY","semantic_anchor":"lower_may_not_contradict_higher","kind":"PRECEDENCE_CONFLICT_CONSTRAINT","adoption_status":"CANDIDATE_ONLY"},
      ],
      "S8.COMPOSITION":[
        {"candidate_id":"S8-C1","source_id":"P091_CONSTITUTION_OPERATIONAL","semantic_anchor":"DNA_OPERATIONAL_BRIDGES","kind":"SOURCE_BACKED_BRIDGE","adoption_status":"CANDIDATE_ONLY"},
        {"candidate_id":"S8-C2","source_id":"CONSTITUTION_REGISTRY","semantic_anchor":"_CONSTITUTION_RULES","kind":"SOURCE_BACKED_RULE_COMPOSITION","adoption_status":"CANDIDATE_ONLY"},
        {"candidate_id":"S8-C3","source_id":"NORMATIVE_HIERARCHY","semantic_anchor":"CANONICAL_LEVEL_GROUPS","kind":"BOUNDED_PRECEDENCE_COMPOSITION","adoption_status":"CANDIDATE_ONLY"},
      ],
      "S10.ENFORCEMENT":[
        {"candidate_id":"S10-C1","source_id":"P091_CONSTITUTION_OPERATIONAL","semantic_anchor":"REQUIRED_EVIDENCE_FIELDS","kind":"DECLARATIVE_ENFORCEMENT_REQUIREMENT","adoption_status":"CANDIDATE_ONLY"},
        {"candidate_id":"S10-C2","source_id":"GOVERNANCE_CONTEXTUAL","semantic_anchor":"CONFLICT","kind":"FAIL_CLOSED_GOVERNANCE_RESPONSE","adoption_status":"CANDIDATE_ONLY"},
      ],
    }
    anchor_checks={
      "S7-C1":"CONFLICT_CLASSES" in ccad, "S7-C2":"PRINCIPLES" in ccad,
      "S7-C3":"lower_may_not_contradict_higher" in hierarchy,
      "S8-C1":"DNA_OPERATIONAL_BRIDGES" in constitution,
      "S8-C2":"_CONSTITUTION_RULES" in registry,
      "S8-C3":"CANONICAL_LEVEL_GROUPS" in hierarchy,
      "S10-C1":"REQUIRED_EVIDENCE_FIELDS" in constitution,
      "S10-C2":"CONFLICT" in governance and "ABSTAIN_ESCALATE" in governance,
    }
    if not all(anchor_checks.values()): raise RuntimeError("SEMANTIC_ANCHOR_MISSING")
    result={
      "schema":"oce.p159.occ1k.r9.governed_semantic_binding_candidate_set.v1",
      "milestone":"P159/OCC-1K-R9",
      "status":"GOVERNED_BINDING_CANDIDATES_READY_NOT_ADOPTED",
      "canonical_source_integrity":integrity,
      "semantic_source_integrity":{k:integrity[k] for k in semantic_required},
      "authority_dependency_integrity":{
        "HUMAN_RESERVED_AUTHORITY":integrity["HUMAN_RESERVED_AUTHORITY"],
        "state":"PROVENANCE_DEBT_BLOCKS_AUTHORITY_PREFLIGHT" if authority_drift else "BOUND",
        "historical_manifest_hash":sources["HUMAN_RESERVED_AUTHORITY"]["sha256"],
        "current_hash":sha(ROOT/sources["HUMAN_RESERVED_AUTHORITY"]["path"]),
        "historical_version_recoverable_from_git":False,
        "current_file_git_state":"UNTRACKED",
      },
      "candidate_anchor_checks":anchor_checks,
      "candidates":candidates,
      "governance":{
        "existing_occ1a_binding_and_adoption_path_reused":True,
        "candidate_is_not_norm":True,
        "candidate_is_not_relation":True,
        "candidate_is_not_adoption":True,
        "human_or_governed_adoption_not_bypassed":True,
        "authority_preflight_allowed":not authority_drift,
        "authority_provenance_debt_preserved":authority_drift,
        "canonical_partitions_modified":False,
        "historical_evidence_modified":False,
        "runtime_binding_created":False,
        "p160b_opened":False,
      },
      "conclusion":{
        "s7":"UNRESOLVED_PENDING_GOVERNED_BINDING",
        "s8":"UNRESOLVED_PENDING_GOVERNED_BINDING",
        "s10":"PARTIAL_PENDING_GOVERNED_BINDING",
        "fl_b3":"BLOCKED","lock_ready":False,"lock_granted":False,
        "next_required_step":"R9B_AUTHORITY_PROVENANCE_RECONCILIATION" if authority_drift else "R9B_GOVERNED_BINDING_PROPOSAL_AND_AUTHORITY_PREFLIGHT"
      },
      "functional_conclusion_only":True,"phenomenology_undetermined":True
    }
    result["semantic_hash"]=hashlib.sha256(canon(result)).hexdigest()
    return result

def write():
    OUT.mkdir(parents=True,exist_ok=True); r=build()
    p=OUT/"governed_semantic_binding_candidate_set_v1.json"; p.write_bytes(canon(r)+b"\n")
    mp=OUT/"occ1k_r9_sha256_manifest_v1.json"
    mp.write_bytes(canon({"schema":"oce.p159.occ1k.r9.manifest.v1","artifact":p.relative_to(ROOT).as_posix(),"sha256":sha(p)})+b"\n")
    return r,p,mp
def main():
    r,p,mp=write()
    print("P159_OCC1K_R9_GOVERNED_SEMANTIC_BINDING_CANDIDATES_COMPLETE")
    print("STATUS="+r["status"])
    print("SEMANTIC_SOURCE_HASHES_VALID=true")
    a=r["authority_dependency_integrity"]
    print("HUMAN_RESERVED_AUTHORITY_HASH_VALID="+str(a["HUMAN_RESERVED_AUTHORITY"]).lower())
    print("AUTHORITY_PROVENANCE_STATE="+a["state"])
    print("S7="+r["conclusion"]["s7"]); print("S8="+r["conclusion"]["s8"]); print("S10="+r["conclusion"]["s10"])
    print("CANONICAL_PARTITIONS_MODIFIED=false")
    print("HISTORICAL_EVIDENCE_MODIFIED=false")
    print("RUNTIME_BINDING_CREATED=false"); print("P160B_OPENED=false")
    print("FL_B3=BLOCKED"); print("LOCK_READY=false"); print("LOCK_GRANTED=false")
    print("NEXT="+r["conclusion"]["next_required_step"])
    print("ARTIFACT_SHA256="+sha(p)); print("MANIFEST_SHA256="+sha(mp))
if __name__=="__main__": main()
